from flask import render_template, request, redirect, url_for
from flask_login import logout_user, login_user, current_user, login_required

from gymapp import app, dao, login
from gymapp.models import UserRole


@app.route('/')
def index():
    return render_template('index.html',)

@app.route('/coach')
@login_required
def coach_view():
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    return render_template('coach/index_coach.html')

@app.route('/cashier')
@login_required
def cashier_view():
    if current_user.user_role != UserRole.CASHIER:
        return redirect('/')
    return render_template('cashier/index_cashier.html')

@app.route('/receptionist')
@login_required
def receptionist_view():
    if current_user.user_role != UserRole.RECEPTIONIST:
        return redirect('/')
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