from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import logout_user, login_user, current_user, login_required

from gymapp import app, dao, login
from gymapp.models import UserRole


@app.route('/')
def index():
    return render_template('index.html', )


###################### VIEW ############################
# coach view
@app.route('/coach')
@login_required
def coach_view():
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    return render_template('coach/index_coach.html')


@app.route('/coach/workout-plans/create')
@login_required
def workout_plans_create():
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    exercises = dao.get_all_exercises()
    days = dao.get_all_day_of_week()
    return render_template('coach/create_workout_plan.html', exercises=exercises, days=days)


@app.route('/api/workout-exercises', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def delete_exercise_from_plan(id):
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    plan = session.get('workout-plan', {})

    if plan and id in plan:
        del plan[id]

    session['workout-plan'] = plan
    return jsonify(list(plan.values()))


@app.route('/api/workout-plans', methods=['POST'])
@login_required
def create_workout_plan():
    if current_user.user_role != UserRole.COACH:
        return redirect('/')
    try:
        data = request.json
        name_plan = str(data.get('name-plan'))
        print(name_plan)
        dao.add_workout_plan(name=name_plan,  plan=session.get('workout-plan'))
        del session['workout-plan']

        return jsonify({'status': 200})
    except Exception as e:
        return jsonify({'status': 400, 'err_msg': str(e)})


###########
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
