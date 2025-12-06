import hashlib

import cloudinary

from gymapp import db, app
from gymapp.models import User, Member, UserRole, Exercise


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
