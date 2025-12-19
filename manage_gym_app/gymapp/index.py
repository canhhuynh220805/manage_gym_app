
import math

from flask import render_template, request, redirect, url_for, jsonify, session
from flask_login import logout_user, login_user, current_user

from gymapp import app, dao, login, db
from gymapp.decorators import login_required
from gymapp.models import UserRole, StatusInvoice



@app.route('/')
def index():
    packages = dao.load_package()
    return render_template('index.html', packages=packages)


###################### VIEW ############################
# coach view
@app.route('/coach')
@login_required(UserRole.COACH)
def coach_view():
    return render_template('coach/index_coach.html')


@app.route('/coach/members')
@login_required(UserRole.COACH)
def coach_members_view():
    members = dao.get_members_by_coach(current_user.id)
    for m in members:
        m.has_plan = dao.has_plan_assigned(coach_id=current_user.id, member_id=m.id)
    plans = dao.get_plan_by_coach(current_user.id)
    return render_template('coach/members_coach.html', members=members, plans=plans)


@app.route('/coach/workout-plans/create')
@login_required(UserRole.COACH)
def workout_plans_create():
    members = dao.get_members_by_coach(current_user.id)
    exercises = dao.get_all_exercises()
    days = dao.get_all_day_of_week()
    return render_template('coach/create_workout_plan.html', exercises=exercises,
                           days=days, members=members)


@app.route('/api/workout-exercises', methods=['POST'])
@login_required(UserRole.COACH)
def add_exercise_to_plan():
    plan = session.get('workout-plan')
    if not plan:
        plan = {}

    id = str(request.json.get('id'))
    name = request.json.get('name')
    description = request.json.get('description')
    image_url = request.json.get('image')

    if id in plan:
        plan[id]['sets'] += 1
    else:
        plan[id] = {
            "id": id,
            "name": name,
            "description": description,
            "image": image_url,
            "sets": 0,
            "reps": 0,
            "days": []
        }

    session['workout-plan'] = plan
    print(list(plan.values()))
    return jsonify(list(plan.values()))


@app.route('/api/workout-exercises/<id>', methods=['PUT'])
@login_required(UserRole.COACH)
def update_exercise_to_plan(id):
    if current_user.user_role != UserRole.COACH:
        return redirect('/')

    plan = session.get('workout-plan')
    sets = int(request.json.get("sets"))
    reps = int(request.json.get("reps"))
    days = request.json.get("days")
    if plan and id in plan:
        if sets:
            plan[id]["sets"] = sets
        if reps:
            plan[id]["reps"] = reps
        if days:
            plan[id]["days"] = days

    session['workout-plan'] = plan
    print(plan[id])
    return jsonify(plan[id])


@app.route('/api/workout-exercises/<id>', methods=['DELETE'])
@login_required(UserRole.COACH)
def delete_exercise_from_plan(id):
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    plan = session.get('workout-plan', {})

    if plan and id in plan:
        del plan[id]

    session['workout-plan'] = plan
    return jsonify(list(plan.values()))


@app.route('/api/workout-plans', methods=['POST'])
@login_required(UserRole.COACH)
def create_workout_plan():
    try:
        data = request.json
        name_plan = str(data.get('name-plan'))
        member_ids = data.get('member_ids')

        print(name_plan)
        dao.add_workout_plan(name=name_plan, plan=session.get('workout-plan'), member_ids=member_ids)
        del session['workout-plan']

        return jsonify({'status': 200})
    except Exception as e:
        return jsonify({'status': 400, 'err_msg': str(e)})


@app.route('/api/assign-existing-plan', methods=['POST'])
@login_required(UserRole.COACH)
def assign_workout_plan():
    data = request.json
    member_id = data.get('member_id')
    plan_id = data.get('plan_id')
    try:
        success = dao.assign_existing_plan(coach_id=current_user.id, member_id=member_id, plan_id=plan_id)
        if success:
            return jsonify({'status': 200, 'msg': 'Gán thành công!'})
        else:
            return jsonify({'status': 400, 'msg': 'Gán thất bại (Gói hết hạn hoặc lỗi dữ liệu)'})
    except Exception as e:
        return jsonify({'status': 400, 'err_msg': str(e)})


###########
@app.route('/cashier')
@login_required(UserRole.CASHIER)
def cashier_view():
    kw = request.args.get('kw')

    pending_invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PENDING)
    paid_invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PAID)
    packages = dao.load_packages()
    return render_template('cashier/index_cashier.html', packages=packages, pending_invoices=pending_invoices,
                           paid_invoices=paid_invoices)

@app.route('/cashier/history')
@login_required(UserRole.CASHIER)
def cashier_history_view():
    kw = request.args.get('kw')
    invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PAID)

    return render_template('cashier/history_cashier.html', invoices=invoices)

@app.route('/api/cashier/process-pending', methods=['post'])
@login_required(UserRole.CASHIER)
def process_pending():
    data = request.json
    invoice_id = data.get('invoice_id')

    is_valid, result = dao.validate_invoice_payment(invoice_id)
    if not is_valid:
        return jsonify({'status': 400, 'msg': result})

    success, msg = dao.process_pending_invoice(invoice_id)

    if success:
        return jsonify({'status': 200, 'msg': msg})
    else:
        return jsonify({'status': 400, 'msg': msg})

@app.route('/api/cashier/direct-pay', methods=['post'])
@login_required(UserRole.CASHIER)
def direct_pay():
    data = request.json
    member_id = data.get('member_id')
    package_id = data.get('package_id')
    invoice = dao.add_member_package_and_pay(member_id, package_id)

    if invoice:
        return jsonify({'status': 200, 'msg': 'Đăng ký và thanh toán thành công!'})
    else:
        return jsonify({'status': 400, 'msg': 'Lỗi xử lý! Vui lòng kiểm tra lại thông tin.'})


@app.route('/api/cashier/cancel-invoice', methods=['post'])
@login_required(UserRole.CASHIER)
def cancel_invoice():
    data = request.json
    invoice_id = data.get('invoice_id')

    if not invoice_id:
        return jsonify({'status': 400, 'msg': 'Mã hóa đơn không hợp lệ!'})

    success, msg = dao.cancel_pending_invoice(invoice_id)

    if success:
        return jsonify({'status': 200, 'msg': msg})
    else:
        return jsonify({'status': 400, 'msg': msg})

@app.route('/payment_history')
@login_required(UserRole.USER)
def payment_history_member():
    date_arg = request.args.get('date_filter')
    status_arg = request.args.get('status_filter')

    invoice = dao.get_invoice_from_cur_user(current_user.id,date_filter=date_arg,status_filter=status_arg)

    if invoice is None:
        invoice = []

    view_data = []

    if invoice:
        for inv in invoice:
            pkg_name = dao.get_package_name_by_invoice(inv.id)

            view_data.append({
                'id': inv.id,
                'invoice_day_create': inv.invoice_day_create,
                'total_amount': inv.total_amount,
                'status': inv.status,
                'service_name': pkg_name
            })

    return render_template('member/payment_history_member.html',
                           invoice=view_data,StatusInvoice=StatusInvoice,date_filter=date_arg,status_filter=status_arg)

#############RECEPTIONIST##################

@app.route('/receptionist')
@login_required(UserRole.RECEPTIONIST)
def receptionist_view():
    return render_template('receptionist/index_receptionist.html')

@app.route('/api/members', methods=['post'])
@login_required(UserRole.RECEPTIONIST)
def search_members_api():
    data = request.json
    kw = data.get('kw')
    members = dao.load_members(kw)

    result = []
    for m in members:
        result.append({
            'id': m.id,
            'name': m.name,
            'phone': m.phone,
            'avatar': m.avatar
        })

    return jsonify(result)

@app.route('/receptionist/members')
@login_required(UserRole.RECEPTIONIST)
def receptionist_members_view():
    page = int(request.args.get('page', 1))
    packages = dao.get_members_for_receptionist(page=page, kw=request.args.get('kw'))
    coaches = dao.get_all_coach()

    return render_template('receptionist/members_receptionist.html', packages=packages, coaches=coaches,
                           pages=math.ceil(dao.count_members_for_receptionist() / app.config['MEMBER_RECEP']))

@app.route('/receptionist/create-invoice')
@login_required(UserRole.RECEPTIONIST)
def receptionist_create_invoice_view():
    packages = dao.load_packages()
    return render_template('receptionist/create_invoice.html', packages=packages)

@app.route('/api/member-packages/<package_id>/assign-coach', methods=['PATCH'])
@login_required(UserRole.RECEPTIONIST)
def assign_coach(package_id):
    coach_id = request.json.get('coach_id')
    updated_package = dao.assign_coach(package_id=package_id, coach_id=coach_id)
    if updated_package:
        new_coach_name=updated_package.coach.name

        return jsonify({
            'message': 'Gán HLV thành công!',
            'coach_name': new_coach_name
        }), 200
    else:
        return jsonify({'error': 'Lỗi: Không tìm thấy gói tập hoặc HLV!'}), 400


@app.route('/receptionist/issue_an_invoice_receptionist')
@login_required(UserRole.RECEPTIONIST)
def issue_an_invoice_receptionist_view():
    pakages = dao.load_package()
    return render_template('receptionist/issue_an_invoice_receptionist.html',pakages=pakages)

@app.route('/api/receptionist/issue_an_invoice_receptionist', methods=['post'])
def issue_an_invoice_receptionist_process():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    package_id = request.form.get('package_id')
    if not package_id:
        return jsonify({'status': 400, 'err_msg': 'Vui lòng chọn gói tập!'})

    if not dob:
        dob = None

    avatar = request.files.get('avatar')
    try:
        member = dao.add_member_full_info(avatar=avatar,
                       name=name,
                       username=username,
                       password= password,phone=phone,gender=gender,dob=dob)

        dao.add_package_registration(user_id=member.id,package_id=package_id)
        return jsonify({
            'status': 200,
            'msg': 'Tạo hóa đơn thành công! Vui lòng báo khách qua quầy thu ngân.'
        })
    except Exception as ex:
        print(str(ex))
        return jsonify({
            'status': 500,
            'err_msg': 'đã có tài username này rồi'
        })

##################################################

@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['post'])
def register_process():
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    if password != confirm:
        err_msg = 'Mật khẩu KHÔNG khớp'
        return render_template('register.html', err_msg=err_msg)

    avatar = request.files.get('avatar')
    try:
        dao.add_member(avatar=avatar,
                       name=request.form.get('name'),
                       username=request.form.get('username'),
                       password=request.form.get('password'))
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))

    return redirect('/login')


@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(user=u)
    else:
        return redirect('/login')
    next = request.args.get('next')
    if next:
        return redirect(next)
    if u.user_role == UserRole.ADMIN:
        return redirect('/admin')
    elif u.user_role == UserRole.COACH:
        return redirect('/coach')
    elif u.user_role == UserRole.CASHIER:
        return redirect('/cashier')
    elif u.user_role == UserRole.RECEPTIONIST:
        return redirect('/receptionist')
    else:
        return redirect('/')


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')


@login.user_loader
def load_user(pk):
    return dao.get_user_by_id(pk)


@app.route('/api/register_package', methods=['post'])
def register_package():
    data = request.json
    user_id = data.get('user_id')
    package_id = data.get('package_id')

    if not user_id or not package_id:
        return jsonify({'status': 400, 'err_msg': 'Dữ liệu không hợp lệ'})

    is_success, message = dao.add_package_registration(user_id, package_id)

    if is_success:
        return jsonify({'status': 200, 'msg': message})
    else:
        return jsonify({'status': 400, 'err_msg': message})


if __name__ == '__main__':
    from gymapp import admin

    app.run(debug=True)
