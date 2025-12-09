
from flask import render_template, request, redirect, url_for, jsonify, session
from flask_login import logout_user, login_user, current_user

from gymapp import app, dao, login
from gymapp.decorators import login_required
from gymapp.models import UserRole

from decorators import login_required

from gymapp.models import UserRole

@app.route('/')
def index():
    packages = dao.load_package()
    return render_template('index.html',packages=packages)


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
    if current_user.user_role != UserRole.COACH:
        return redirect('/')

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
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    members = dao.load_members()
    packages = dao.load_packages()
    invoices = dao.get_invoices(kw=kw, from_date=from_date, to_date=to_date)

    return render_template('cashier/index_cashier.html', members=members, packages=packages,
                           invoices=invoices)

@app.route('/api/cashier/pay', methods=['post'])
@login_required(UserRole.CASHIER)
def cashier_pay_process():
    member_id = request.json.get('member_id')
    package_id = request.json.get('package_id')

    if not member_id or not package_id:
        return jsonify({'status': 400, 'msg': 'Thiếu thông tin hội viên hoặc gói tập'})

    try:
        new_invoice = dao.add_member_package_and_pay(member_id, package_id)
        if new_invoice:
            return jsonify({'status': 200, 'msg': 'Thanh toán thành công'})
        else:
            return jsonify({'status': 400, 'msg': 'Lỗi xử lý nghiệp vụ'})
    except Exception as ex:
        return jsonify({'status': 500, 'msg': str(ex)})


@app.route("/api/invoices/<int:invoice_id>", methods=['get'])
@login_required(UserRole.CASHIER)
def get_invoice_detail_api(invoice_id):
    try:
        invoice = dao.get_invoice_detail(invoice_id)
        if invoice: #Quan trọng đáy, dùng để phòng ngừa invoice rỗng khi truy xuất
            detail = invoice.invoice_details[0] if invoice.invoice_details else None
            pkg_name = detail.member_package.package.description if detail else "N/A"
            duration = detail.member_package.package.duration if detail else 0

            data = {
                'id': invoice.id,
                'created_date': invoice.payment_date.strftime('%d/%m/%Y %H:%M'),
                'member_name': invoice.member.name,
                'staff_name': current_user.name,
                'package_name': pkg_name,
                'duration': duration,
                'total_amount': invoice.total_amount
            }
            return jsonify({'status': 200, 'data': data})

        return jsonify({'status': 404, 'msg': 'Không tìm thấy hóa đơn'})
    except Exception as ex:
        return jsonify({'status': 500, 'msg': str(ex)})


@app.route('/receptionist')
@login_required(UserRole.RECEPTIONIST)
def receptionist_view():
    return render_template('receptionist/index_receptionist.html')


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
    if u.user_role == UserRole.COACH:
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
