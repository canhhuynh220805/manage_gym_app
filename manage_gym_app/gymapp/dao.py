import hashlib
from datetime import datetime, timedelta

import cloudinary
from flask_login import current_user

from gymapp import db, app
from gymapp.models import User, Member, UserRole, Exercise, Invoice, InvoiceDetail, MemberPackage, StatusInvoice, \
    StatusPackage, Package, ExerciseSchedule, DayOfWeek, PlanDetail, WorkoutPlan


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


#CASHIER

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

        bill = Invoice(member_id=member_id, total_amount=pack.price, status=StatusInvoice.PAID, payment_date=datetime.now())
        db.session.add(bill)

        detail = InvoiceDetail(invoice=bill, member_package=mp, amount=pack.price)
        db.session.add(detail)

        db.session.commit()

        return bill

    return None


