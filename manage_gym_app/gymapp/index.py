from flask import render_template, request, redirect, url_for, jsonify
from flask_login import logout_user, login_user, current_user
from gymapp.decorators import login_required

from gymapp import app, dao, login
from gymapp.models import UserRole


@app.route('/')
def index():
    return render_template('index.html', )


###################### VIEW ############################
# coach view
@app.route('/coach')
@login_required(UserRole.COACH)
def coach_view():
    return render_template('coach/index_coach.html')


@app.route('/coach/workout-plans/create')
@login_required(UserRole.COACH)
def workout_plans_create():
    exercises = dao.get_all_exercises()

    return render_template('coach/create_workout_plan.html', exercises=exercises)


###########
@app.route('/cashier')
@login_required(UserRole.CASHIER)
def cashier_view():
    return render_template('cashier/index_cashier.html')

@app.route('/api/cashier/pay', methods = ['post'])
@login_required(UserRole.CASHIER)
def cashier_pay():
    try:
        data = request.json
        id = data.get('member_package_id')

        new_invoice = dao.process_payment(member_package_id=id)

        if new_invoice:
            return jsonify({
                'status': 200,
                'data': {
                    'invoice_id': new_invoice.id,
                    'total_amount': new_invoice.total_amount,
                    'payment_date': str(new_invoice.payment_date)
                }
            })
        else:
            return jsonify({'status': 400, 'err_msg': 'Gói tập không tồn tại hoặc lỗi xử lý'})

    except Exception as ex:
        return jsonify({'status': 400, 'err_msg': str(ex)})

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


###################################################
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
        return render_template('register.html', err_msg="Hệ thống đang có lỗi!")

    return redirect('/login')


@app.route('/login', methods=['post'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password)
    print()
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


if __name__ == '__main__':
    from gymapp import admin

    app.run(debug=True)
