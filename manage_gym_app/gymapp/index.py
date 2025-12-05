from flask import render_template, request, redirect
from flask_login import logout_user, login_user

from gymapp import app, dao, login


@app.route('/')
def index():
    packages = dao.load_package()
    package_benefits = dao.load_package_benefit()
    print(packages)
    return render_template('index.html',packages=packages,package_benefits = package_benefits)


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
        dao.add_user(avatar=avatar,
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
    if u:
        login_user(user=u)

    next = request.args.get('next')
    return redirect(next if next else '/')


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