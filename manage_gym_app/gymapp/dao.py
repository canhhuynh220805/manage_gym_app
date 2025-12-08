import hashlib
from sqlalchemy import text
from datetime import datetime
from dateutil.relativedelta import relativedelta
import cloudinary
import cloudinary.uploader

from gymapp import db, app
from gymapp.models import User, Package, PackageBenefit,MemberPackage,StatusPackage, Member


def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username==username.strip(),
                             User.password==password).first()


def add_user(name, username, password, avatar):
    u = User(name=name,
             username=username.strip(),
             password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()))

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()

def load_package():
    query = Package.query.all()
    return query

def load_package_benefit():
    query = PackageBenefit.query.all()
    return query


def add_package_registration(user_id, package_id):
    db.session.remove()

    member = Member.query.get(user_id)

    if not member:
        user = User.query.get(user_id)
        if not user:
            return False, "User không tồn tại"

        _upgrade_user_to_member_force(user_id)

        db.session.remove()

        member = Member.query.get(user_id)

        if not member:
            return False, "Lỗi hệ thống: Không thể khởi tạo thông tin hội viên."

    package = Package.query.get(package_id)
    if not package:
        return False, "Gói tập không tồn tại"
    start_date = datetime.now()
    duration = getattr(package, 'duration', 1)
    end_date = start_date + relativedelta(months=duration)

    new_registration = MemberPackage(
        member_id=member.id,
        package_id=package.id,
        startDate=start_date,
        endDate=end_date,
        status=StatusPackage.EXPIRED,
        coach_id=None
    )

    try:
        db.session.add(new_registration)
        db.session.commit()
        return True, "Đăng ký thành công, vui lòng đến phòng gym để thanh toán và kích hoạt tài khoản!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    finally:
        db.session.remove()


def _upgrade_user_to_member_force(user_id):
    try:
        sql_insert = text("INSERT IGNORE INTO member (id) VALUES (:id)")
        db.session.execute(sql_insert, {'id': user_id})

        sql_update = text("UPDATE user SET type = 'member' WHERE id = :id")
        db.session.execute(sql_update, {'id': user_id})

        db.session.commit()

        db.session.expire_all()
    except Exception as e:
        db.session.rollback()