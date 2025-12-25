import math
import threading
from datetime import datetime
import sys

print("Python đang chạy ở:", sys.executable)

from flask import render_template, request, redirect, url_for, jsonify, session
from flask_login import logout_user, login_user, current_user

from gymapp import app, dao, login, db, observers
from gymapp.decorators import login_required
from gymapp.models import UserRole, StatusInvoice, DayOfWeek, WorkoutPlan


@app.route('/')
def index():
    packages = dao.load_package()
    gym_rules = dao.get_gym_rules()
    return render_template('index.html', packages=packages, gym_rules=gym_rules)


###################### VIEW ############################
# coach view
@app.route('/coach')
@login_required(UserRole.COACH)
def coach_view():
    if 'workout-plan' in session:
        del session['workout-plan']
    workout_plans = dao.get_workout_plan_by_coach_id(current_user.id)
    return render_template('coach/index_coach.html', workout_plans=workout_plans)


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

    data = request.json
    if not data:
        return jsonify({'err_msg': 'Dữ liệu không hợp lệ', 'status': 400})

    id = str(data.get('id'))
    if not id:
        return jsonify({'err_msg': "Thiếu ID", 'status': 400})
    name = data.get('name')
    if not name:
        return jsonify({'err_msg': "Thiếu tên bài tập", 'status': 400})

    if id in plan:
        plan[id]['sets'] += 1
    else:
        plan[id] = {
            "id": id,
            "name": name,
            "sets": 0,
            "reps": 0,
            "days": []
        }

    session['workout-plan'] = plan
    print(list(plan.values()))
    return jsonify({
        'status': 200,
        'data': list(plan.values()),
        'msg': "Thêm bài tập thành công"
    })


@app.route('/api/workout-exercises/<id>', methods=['PUT'])
@login_required(UserRole.COACH)
def update_exercise_to_plan(id):
    data = request.json
    if not data:
        return jsonify({'err_msg': 'Dữ liệu không hợp lệ', 'status': 400})
    plan = session.get('workout-plan')
    if not plan or id not in plan:
        return jsonify({'err_msg': 'Bài tập không tồn tại trong giáo án!', 'status': 404})
    try:
        sets = int(data.get("sets"), 0)
        reps = int(data.get("reps"), 0)
        days = data.get("days", [])

        plan[id]["sets"] = sets
        plan[id]["reps"] = reps
        plan[id]["days"] = days

        session['workout-plan'] = plan
        print(plan[id])
        return jsonify({
            'status': 200,
            'data': plan[id],
            'msg': "Cập nhật thay đổi"
        })
    except ValueError:
        return jsonify({'err_msg': 'Sets và Reps phải là số nguyên!', 'status': 400})
    except Exception as e:
        return jsonify({'err_msg': f'Lỗi hệ thống: {str(e)}', 'status': 500})


@app.route('/api/workout-exercises/<id>', methods=['DELETE'])
@login_required(UserRole.COACH)
def delete_exercise_from_plan(id):
    try:
        plan = session.get('workout-plan', {})

        if plan and id in plan:
            del plan[id]

            session['workout-plan'] = plan
            return jsonify({
                'status': 200,
                'data': list(plan.values()),
                'msg': "Gỡ thành công bài tập"
            })
        return jsonify({
            'status': 400,
            'err_msg': "Bài tập không tồn tại"
        })
    except Exception as e:
        return jsonify({
            'status': 500,
            'err_msg': "Lỗi hệ thống: " + str(e)
        })


@app.route('/api/workout-plans', methods=['POST'])
@login_required(UserRole.COACH)
def create_workout_plan():
    try:
        data = request.json
        if not data:
            return jsonify({'err_msg': 'Dữ liệu không hợp lệ', 'status': 400})
        name_plan = str(data.get('name-plan'))
        member_ids = data.get('member_ids')
        start_date = data.get('startDate')
        end_date = data.get('endDate')
        plan = session.get('workout-plan')
        success, err_msg, msg = (
            WorkoutPlan.Builder() \
                .set_info(name=name_plan, coach_id=current_user.id) \
                .set_exercise(plan) \
                .set_member(member_ids=member_ids, start_date=start_date, end_date=end_date) \
                .build()
        )
        if success:
            del session['workout-plan']
            return jsonify({'msg': msg, 'status': 200})
        else:
            return jsonify({'err_msg': err_msg, 'status': 400})
    except Exception as e:
        return jsonify({'err_msg': f'Lỗi hệ thống: {str(e)}', 'status': 500})


@app.route('/api/assign-existing-plan', methods=['POST'])
@login_required(UserRole.COACH)
def assign_workout_plan():
    data = request.json
    if not data:
        return jsonify({'err_msg': 'Dữ liệu không hợp lệ', 'status': 400})

    member_id = data.get('member_id')
    plan_id = data.get('plan_id')

    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not start_date or not end_date:
        return jsonify({"err_msg": "Vui lòng chọn ngày bắt đầu và ngày kết thúc", 'status': 400})

    start_date = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date[:10], "%Y-%m-%d").date()

    end_lates_date = dao.get_latest_assignment_end_date(member_id).date()
    if end_lates_date and start_date <= end_lates_date:
        fmt_date = end_lates_date.strftime('%d/%m/%Y')
        return jsonify({
            'err_msg': f"Hội viên đang bận tập giáo án cũ đến hết ngày {fmt_date}. Vui lòng chọn ngày bắt đầu sau ngày này!",
            'status': 400
        })

    if start_date >= end_date:
        return jsonify({'err_msg': "Ngày bắt đầu phải nhỏ hơn ngày kết thúc", 'status': 400})
    if start_date < datetime.now().date():
        return jsonify({'err_msg': "Ngày bắt đầu không được ở trong quá khứ", 'status': 400})

    try:

        success = dao.assign_existing_plan(coach_id=current_user.id, member_id=member_id,
                                           plan_id=plan_id, start_date=start_date, end_date=end_date)
        if success:
            return jsonify({'status': 200, 'msg': 'Gán thành công!'})
        else:
            return jsonify({'status': 400, 'err_msg': 'Gán thất bại (Gói hết hạn hoặc lỗi dữ liệu)'})
    except Exception as e:
        return jsonify({'status': 400, 'err_msg': str(e)})


###########
@app.route('/cashier')
@login_required(UserRole.CASHIER)
def cashier_view():
    kw = request.args.get('kw')

    pending_invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PENDING, limit=5)
    paid_invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PAID, limit=5)
    packages = dao.load_packages()
    return render_template('cashier/index_cashier.html', packages=packages, pending_invoices=pending_invoices,
                           paid_invoices=paid_invoices)


@app.route('/cashier/history')
@login_required(UserRole.CASHIER)
def cashier_history_view():
    kw = request.args.get('kw')
    invoices = dao.get_invoices(kw=kw, status=StatusInvoice.PAID, page=int(request.args.get('page', 1)))

    return render_template('cashier/history_cashier.html', invoices=invoices
                           , pages=math.ceil(
            dao.count_invoices(kw=kw, status=StatusInvoice.PAID) / app.config['PAGE_SIZE']))


@app.route('/api/cashier/process-pending', methods=['post'])
@login_required(UserRole.CASHIER)
def process_pending():
    invoice_id = request.json.get('invoice_id')
    success, msg = dao.process_pending_invoice(invoice_id)
    return jsonify({'status': 200 if success else 400,
                    'msg': msg
                    })


@app.route('/api/cashier/direct-pay', methods=['post'])
@login_required(UserRole.CASHIER)
def direct_pay():
    data = request.json
    member_id = data.get('member_id')
    package_id = data.get('package_id')
    invoice = dao.process_payment(member_id, package_id)

    if invoice:
        return jsonify({'status': 200, 'msg': 'Thanh toán thành công!'})
    else:
        return jsonify({'status': 400, 'msg': 'Lỗi xử lý! Vui lòng kiểm tra lại thông tin.'})


@app.route('/api/cashier/cancel-invoice', methods=['post'])
@login_required(UserRole.CASHIER)
def cancel_invoice():
    data = request.json
    invoice_id = data.get('invoice_id')

    is_valid, result = dao.validate_cashier(invoice_id)
    if not is_valid:
        return jsonify({'status': 400, 'msg': result})

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

    invoice = dao.get_invoice_from_cur_user(current_user.id, date_filter=date_arg, status_filter=status_arg)

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
                           invoice=view_data, StatusInvoice=StatusInvoice, date_filter=date_arg,
                           status_filter=status_arg)


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
    page_mem = int(request.args.get('page', 1))
    packages = dao.get_members_for_receptionist(page=page_mem, kw=request.args.get('kw'))
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
        return jsonify({
            'msg': 'Gán HLV thành công!',
            'status': 200
        })
    else:
        return jsonify({'error': 'Lỗi: Không tìm thấy gói tập hoặc HLV!', 'status': 400})


@app.route('/receptionist/issue_an_invoice_receptionist')
@login_required(UserRole.RECEPTIONIST)
def issue_an_invoice_receptionist_view():
    selected_package_id = request.args.get('package_id', type=int)
    pakages = dao.load_package()
    return render_template('receptionist/issue_an_invoice_receptionist.html', pakages=pakages,
                           selected_package_id=selected_package_id)


@app.route('/api/receptionist/issue_an_invoice_receptionist', methods=['post'])
@login_required(UserRole.RECEPTIONIST)
def issue_an_invoice_receptionist_process():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    package_id = request.form.get('package_id')
    email = request.form.get('email')
    if not package_id:
        return jsonify({'status': 400, 'err_msg': 'Vui lòng chọn gói tập!'})

    if not dob:
        dob = None

    avatar = request.files.get('avatar')
    try:
        member = dao.add_member_full_info(avatar=avatar,
                                          name=name,
                                          username=username,
                                          password=password, phone=phone, gender=gender, dob=dob, email=email)

        dao.add_package_registration(user_id=member.id, package_id=package_id)

        notifier = observers.RegistrationSubject()
        notifier.attach(observers.EmailNotificationObserver())
        notifier.notify(user_id=member.id, package_id=package_id)

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

#####ADMIN
@app.route('/api/admin/exercises', methods=['POST'])
@login_required(UserRole.ADMIN)
def add_exercise_api():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 400, 'err_msg': 'Dữ liệu không hợp lệ!'})
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        image = data.get('image', '').strip()
        if len(name) < 3:
            return jsonify({'status': 400, 'err_msg': 'Tên bài tập quá ngắn!'})

        if not description:
            return jsonify({'status': 400, 'err_msg': 'Thiếu mô tả bài tập!'})

        if not image.startswith(('http://', 'https://')):
            return jsonify({'status': 400, 'err_msg': 'URL ảnh không hợp lệ!'})

        success, msg = dao.add_exercise(name, description, image)
        if success:
            return jsonify({'status': 200, 'msg': msg})

        return jsonify({'status': 400, 'err_msg': msg})

    except Exception as e:
        return jsonify({'status': 500, 'err_msg': f'Lỗi hệ thống: {str(e)}'})


@app.route('/api/admin/packages', methods=['POST'])
@login_required(UserRole.ADMIN)
def add_package_api():
    data = request.json
    name = data.get('name', '').strip()
    price = data.get('price')
    duration = data.get('duration')
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    benefits = data.get('benefits', [])

    if not name or len(name) < 3:
        return jsonify({'status': 400, 'err_msg': 'Tên gói tập phải từ 3 ký tự trở lên!'})

    try:
        if float(price) <= 0:
            return jsonify({'status': 400, 'err_msg': 'Giá tiền phải lớn hơn 0!'})
    except:
        return jsonify({'status': 400, 'err_msg': 'Giá tiền không hợp lệ!'})

    try:
        if int(duration) <= 0:
            return jsonify({'status': 400, 'err_msg': 'Thời hạn phải ít nhất 1 tháng!'})
    except:
        return jsonify({'status': 400, 'err_msg': 'Thời hạn không hợp lệ!'})

    if not description:
        return jsonify({'status': 400, 'err_msg': 'Mô tả không được để trống!'})

    if not image.startswith(('http://', 'https://')):
        return jsonify({'status': 400, 'err_msg': 'Link ảnh phải là một URL hợp lệ!'})

    success, msg = dao.add_package(name, price, duration, description, image, benefits)
    return jsonify({'status': 200 if success else 400, 'msg' if success else 'err_msg': msg})


@app.route('/login')
def login_view():
    return render_template('login.html')


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/workout-plans')
@login_required(UserRole.USER)
def workout_plan_view():
    workout_plans = dao.get_workout_plan_by_member_id(member_id=current_user.id)
    return render_template('member/member_workout_plan.html', workout_plans=workout_plans)


@app.route('/workout-plans/<plan_id>', methods=['GET'])
def workout_plan_detail(plan_id):
    workout_plan = dao.get_detail_workout_plan_by_id(workout_plan_id=plan_id)
    schedule = {day.value: [] for day in DayOfWeek}
    for detail in workout_plan.exercises:
        for s in detail.exercise_schedules:
            day_name = s.day.value
            schedule[day_name].append({
                'name': detail.exercise.name,
                'sets': detail.sets,
                'reps': detail.reps,
                'image': detail.exercise.image
            })

    return render_template('member/workout_plan_detail.html',
                           workout_plan=workout_plan, schedule=schedule)


@app.route('/register', methods=['post'])
def register_process():
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    name = request.form.get('name')
    username = request.form.get('username')
    phone = request.form.get('phone')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    email = request.form.get('email')

    if password != confirm:
        err_msg = 'Mật khẩu KHÔNG khớp'
        return render_template('register.html', err_msg=err_msg)
    if email is None:
        err_msg = 'Vui lòng nhập Email'
        return render_template('register.html', err_msg=err_msg)
    avatar = request.files.get('avatar')
    try:
        dao.add_member_full_info(avatar=avatar, name=name, username=username, password=password, phone=phone,
                                 gender=gender, dob=dob, email=email)
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
        err_msg = "Đăng nhập thất bại, tài khoản hoặc mật khẩu ko tồn tại!!!"
        return render_template('login.html', err_msg=err_msg)
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


#################
@app.route('/api/register_package', methods=['post'])
@login_required(UserRole.USER)
def register_package():
    data = request.json
    print(data)
    user_id = data.get('user_id')
    package_id = data.get('package_id')

    if not user_id or not package_id:
        return jsonify({'status': 400, 'err_msg': 'Dữ liệu không hợp lệ'})

    try:
        is_valid, result = dao.validate_registration_package(user_id)

        if not is_valid:
            return jsonify({
                'status': 400,
                'err_msg': result
            })

        is_success, message = dao.add_package_registration(user_id, package_id)

        if is_success:
            notifier = observers.RegistrationSubject()
            notifier.attach(observers.EmailNotificationObserver())
            notifier.notify(user_id=user_id, package_id=package_id)

            return jsonify({'status': 200, 'msg': message})
        else:
            return jsonify({'status': 400, 'err_msg': message})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 500, 'err_msg': 'Lỗi hệ thống: ' + str(e)})


@app.route('/view_package_receptionist')
def view_package_receptionist():
    packages = dao.load_package()
    return render_template('receptionist/view_package.html', packages=packages)

if __name__ == '__main__':
    from gymapp import admin

    app.run(debug=True)
