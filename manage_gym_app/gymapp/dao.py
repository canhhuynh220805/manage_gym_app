import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import cloudinary
from flask_login import current_user
from cloudinary import uploader #them uploader de up anh luc dang ki
from gymapp import db, app
from gymapp.models import (User, Member, UserRole, Exercise, Invoice, InvoiceDetail, MemberPackage,
                           StatusInvoice, StatusPackage, Package, ExerciseSchedule, DayOfWeek,
                           PlanDetail, WorkoutPlan, PackageBenefit, Coach)

from dateutil.relativedelta import relativedelta
from sqlalchemy import text

def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username.strip(),
                             User.password == password).first()



def add_member(name, username, password, avatar):

    u = Member(name=name,
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
    query = Package.query.all()
    return query

def add_package_registration(user_id, package_id):
    member = User.query.get(user_id)

    if not member:
        return False, "User không tồn tại"

    package = Package.query.get(package_id)
    if not package:
        return False, "Gói tập không tồn tại"
    start_date = datetime.now()
    duration = getattr(package, 'duration', 1)
    end_date = start_date + relativedelta(months=duration)

    #########################
    new_invoice_pending = Invoice(
        member_id=member.id,
        status=StatusInvoice.PENDING,
        total_amount=package.price
    )
    _upgrade_user_to_member_force(user_id)
    ########################
    new_registration = MemberPackage(
        member_id=member.id,
        package_id=package.id,
        startDate=start_date,
        endDate=end_date,
        status=StatusPackage.EXPIRED,
        coach_id=None
    )
    ########################
    try:
        db.session.add_all([new_invoice_pending,new_registration])
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

# HUẤN LUYỆN VIÊN
def get_all_exercises():
    return Exercise.query.all()


def get_all_day_of_week():
    return [e.name for e in DayOfWeek]


def get_active_packages(coach_id, member_ids):
    if not member_ids:
        return []
    return db.session.query(MemberPackage).filter(
                MemberPackage.member_id.in_(member_ids),
                MemberPackage.coach_id == coach_id,
                MemberPackage.status == StatusPackage.ACTIVE
            ).all()

def has_plan_assigned(coach_id, member_id):
    active_packages = get_active_packages(coach_id, [member_id])
    for pkg in active_packages:
        if pkg.workout_plans:
            return True
    return False

def assign_existing_plan(coach_id, member_id, plan_id):
    plan = WorkoutPlan.query.get(plan_id)

    if plan and plan.coach_id == coach_id:
        packages = get_active_packages(coach_id, [member_id])
        if packages:
            plan.member_packages.extend(packages)
            db.session.commit()
            return True

    return False




def add_workout_plan(name, plan, member_ids):
    if plan:
        p = WorkoutPlan(name=name, coach=current_user)
        db.session.add(p)

        if member_ids:
            packages = get_active_packages(coach_id=current_user.id, member_ids=member_ids)
            p.member_packages.extend(packages)

        for ex in plan.values():
            pd = PlanDetail(exercise_id=ex['id'], reps=ex['reps'], sets=ex['sets'], workout_plan=p)
            db.session.add(pd)

            for day in ex['days']:
                day_enum = DayOfWeek[day]
                d = ExerciseSchedule(
                    day=day_enum,
                    plan_detail=pd
                )
                db.session.add(d)

        db.session.commit()


def get_members_by_coach(coach_id):
    query = (db.session.query(Member)
             .join(MemberPackage, MemberPackage.member_id == Member.id)
             .filter(MemberPackage.coach_id == coach_id))

    return query.all()


def get_plan_by_coach(coach_id):
    return WorkoutPlan.query.filter(WorkoutPlan.coach_id == coach_id).all()

# CASHIER

def get_payment_history():
    return Invoice.query.all()


def process_payment(member_package_id):
    mp = MemberPackage.query.get(member_package_id)

    if mp:
        bill = Invoice(member_id=mp.member_id, total_amount=mp.package.price, status=StatusInvoice.PAID,
                       payment_date=datetime.now())
        db.session.add(bill)

        detail = InvoiceDetail(invoice=bill, member_package_id=mp.id, amount=mp.package.price)

        db.session.add(detail)
        mp.status = StatusPackage.ACTIVE
        db.session.commit()
        return bill
    return None


def get_invoice_detail(invoice_id):
    return Invoice.query.get(invoice_id)


def load_members(kw=None):
    query = Member.query
    if kw:
        query = query.filter(Member.name.contains(kw) | Member.phone.contains(kw))
    return query.limit(10).all()

def load_packages():
    return Package.query.all()


def get_invoices(kw=None, from_date=None, to_date=None):
    q = Invoice.query
    if kw:
        q = q.join(Member).filter(Member.name.contains(kw) | Member.username.contains(kw))

    if from_date:
        q = q.filter(Invoice.payment_date >= from_date)

    if to_date:
        q = q.filter(Invoice.payment_date <= to_date)

    return q.order_by(Invoice.payment_date.desc()).all()


def get_invoice_detail(invoice_id):
    return Invoice.query.get(invoice_id)

def add_member_package_and_pay(member_id, package_id):
    pack = Package.query.get(package_id)

    if pack:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=pack.duration * 30)

        mp = MemberPackage(member_id=member_id, package_id=package_id, startDate=start_date, endDate=end_date,
                           status=StatusPackage.ACTIVE)
        db.session.add(mp)

        bill = Invoice(member_id=member_id, total_amount=pack.price, status=StatusInvoice.PAID,
                       payment_date=datetime.now())
        db.session.add(bill)

        detail = InvoiceDetail(invoice=bill, member_package=mp, amount=pack.price)
        db.session.add(detail)

        db.session.commit()

        return bill

    return None


#RECEPTIONIST
def get_members_for_receptionist(kw=None, page=1):
    # query = MemberPackage.query.filter(MemberPackage.status == StatusPackage.ACTIVE)
    query = MemberPackage.query.join(MemberPackage.member)\
        .options(joinedload(MemberPackage.member))\
        .options(joinedload(MemberPackage.coach)) \
        .options(joinedload(MemberPackage.package))\
        .filter(MemberPackage.status == StatusPackage.ACTIVE)

    if kw:
        query = query.filter(Member.name.contains(kw))
    if page:
        start = (page - 1) * app.config['MEMBER_RECEP']
        query = query.slice(start, start + app.config['MEMBER_RECEP'])

    return query.all()

def count_members_for_receptionist():
    return MemberPackage.query\
        .options(joinedload(MemberPackage.member))\
        .options(joinedload(MemberPackage.coach)) \
        .options(joinedload(MemberPackage.package)).count()

def get_all_coach():
    return Coach.query.all()

def assign_coach(coach_id, package_id):
    coach = Coach.query.get(coach_id)
    package = MemberPackage.query.get(package_id)
    if not package or not coach:
        return None
    package.coach = coach
    try:
        db.session.commit()
        return package
    except Exception as ex:
        print(f"Lỗi khi gán HLV: {str(ex)}")
        db.session.rollback()
        return None





if __name__ == '__main__':
    with app.app_context():
        # for m in get_members_for_receptionist():
        #     print(m.member.name)
        # print(get_members_for_receptionist())
        print(count_members_for_receptionist())
