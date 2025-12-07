import hashlib

import cloudinary
from flask_login import current_user

from gymapp import db, app
from gymapp.models import User, Member, UserRole, Exercise, DayOfWeek, WorkoutPlan, PlanDetail, ExerciseSchedule


def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username==username.strip(),
                             User.password==password).first()


def add_member(name, username, password, avatar):
    u = Member(name=name,
             username=username.strip(),
             password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()))

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

#HUẤN LUYỆN VIÊN

def get_all_exercises():
    return Exercise.query.all()

def get_all_day_of_week():
    return [e.name for e in DayOfWeek]

def add_workout_plan(name, plan):
    if plan:
        p = WorkoutPlan(name=name, coach=current_user)
        db.session.add(p)
        print(plan.values())
        for ex in plan.values():
            pd = PlanDetail(exercise_id=ex['id'], reps=ex['reps'], sets=ex['sets'], workout_plan=p)
            db.session.add(pd)

            for day in ex['days']:
                try:
                    day_enum = DayOfWeek[day]
                except KeyError:
                    continue
                d = ExerciseSchedule(
                    day = day_enum,
                    plan_detail=pd
                )
                db.session.add(d)

        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        print(get_all_day_of_week())