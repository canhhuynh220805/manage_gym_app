import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import cloudinary
from flask_login import current_user
from cloudinary import uploader  # them uploader de up anh luc dang ki
from gymapp import db, app
from gymapp.models import (User, Member, UserRole, Exercise, Invoice, InvoiceDetail, MemberPackage,
                           StatusInvoice, StatusPackage, Package, ExerciseSchedule, DayOfWeek,
                           PlanDetail, WorkoutPlan, PackageBenefit, Coach)

from dateutil.relativedelta import relativedelta
from sqlalchemy import text, func, extract


def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username.strip(),
                             User.password == password).first()


def count_members():
    return Member.query.count()


def count_coaches():
    return Coach.query.count()


def count_packages():
    return Package.query.count()


def get_total_revenue_month():
    current_month = datetime.now().month
    current_year = datetime.now().year
    result = db.session.query(func.sum(Invoice.total_amount)) \
        .filter(extract('month', Invoice.payment_date) == current_month,
                extract('year', Invoice.payment_date) == current_year,
                Invoice.status == StatusInvoice.PAID).scalar()
    return result if result else 0


def stats_package_usage():
    return (db.session.query(Package.id, Package.name, func.count(MemberPackage.id))
            .outerjoin(MemberPackage, MemberPackage.package_id == Package.id)
            .group_by(Package.id, Package.name)
            .order_by(Package.id).all())


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

    #BỎ NGÀY BẮT ĐẦU VÀ NGÀY NGÀY KẾT THÚC KHI ĐĂNG KÍ#
    #########################
    new_invoice_pending = Invoice(
        member_id=member.id,
        status=StatusInvoice.PENDING,
        total_amount=package.price,
        invoice_day_create=datetime.now()
    )
    _upgrade_user_to_member_force(user_id)
    ########################
    new_registration = MemberPackage(
        member_id=member.id,
        package_id=package.id,
        status=StatusPackage.PENDING,
        coach_id=None
    )
    ########################
    try:
        db.session.add_all([new_invoice_pending, new_registration])
        db.session.commit()
        invoice = Invoice.query.get(new_invoice_pending.id)
        member_package = MemberPackage.query.get(new_registration.id)
        new_invoice_detail = InvoiceDetail(
            invoice_id=invoice.id,
            amount=invoice.total_amount,
            member_package_id=member_package.id
        )

        try:
            db.session.add(new_invoice_detail)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False, str(e)
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


def load_members(kw=None):
    query = Member.query
    if kw:
        query = query.filter(Member.name.contains(kw) | Member.phone.contains(kw))
    return query.limit(10).all()


def load_packages():
    return Package.query.all()


def get_invoices(kw=None, status=None):
    query = Invoice.query

    if kw:
        query = query.join(Member).filter(Member.name.contains(kw) | Member.phone.contains(kw))

    if status:
        query = query.filter(Invoice.status == status)

    return query.order_by(Invoice.id.desc()).all()
  
def get_invoice_from_cur_user(cur_user_id):
    return Invoice.query.filter_by(member_id=cur_user_id).order_by(Invoice.payment_date.desc()).all()

def get_package_name_by_invoice(invoice_id):
    try:
        detail = InvoiceDetail.query.filter_by(invoice_id=invoice_id).first()
        if detail:
            mem_pack = MemberPackage.query.get(detail.member_package_id)
            if mem_pack:
                pack = Package.query.get(mem_pack.package_id)
                if pack:
                    return pack.name
    except Exception as e:
        print(e)

    return "Không đăng kí gói nào"

def get_invoice_detail(invoice_id):
    return Invoice.query.get(invoice_id)

def calculate_package_dates(member_id, duration_months):
    now = datetime.now()

    last_active_package = MemberPackage.query.filter(MemberPackage.member_id == member_id, MemberPackage.status == StatusPackage.ACTIVE,
                                                     MemberPackage.endDate > now).order_by(MemberPackage.endDate.desc()).first()

    if last_active_package:
        start_date = last_active_package.endDate
    else:
        start_date = now
    end_date = start_date + relativedelta(months=duration_months)

    return start_date, end_date


def add_package_registration(user_id, package_id):
    u = db.session.get(User, user_id)
    p = db.session.get(Package, package_id)

    if u and p:
        try:
            _upgrade_user_to_member_force(user_id)
            start = datetime.now()
            end = start + relativedelta(months=p.duration)

            mp = MemberPackage(member_id=u.id, package_id=p.id, startDate=start, endDate=end, status=StatusPackage.EXPIRED)
            db.session.add(mp)

            invoice = Invoice(member_id=u.id, total_amount=p.price, status=StatusInvoice.PENDING)
            db.session.add(invoice)

            d = InvoiceDetail(invoice=invoice, member_package=mp, amount=p.price)
            db.session.add(d)

            db.session.commit()
            return True, "Đăng ký thành công! Vui lòng thanh toán tại quầy lễ tân."

        except Exception as ex:
            db.session.rollback()
            return False, str(ex)

    return False, "Thông tin người dùng hoặc gói tập không hợp lệ"

def process_pending_invoice(invoice_id):
    inv = db.session.get(Invoice, invoice_id)

    if inv and inv.status == StatusInvoice.PENDING:
        try:
            inv.status = StatusInvoice.PAID
            inv.payment_date = datetime.now()

            for d in inv.invoice_details:
                mp = d.member_package
                s, e = calculate_package_dates(mp.member_id, mp.package.duration)

                mp.startDate = s
                mp.endDate = e
                mp.status = StatusPackage.ACTIVE

            db.session.commit()
            return True, "Thanh toán thành công!"

        except Exception as ex:
            db.session.rollback()
            return False, str(ex)

    return False, "Hóa đơn không hợp lệ hoặc đã thanh toán"

def add_member_package_and_pay(member_id, package_id):

    p = db.session.get(Package, package_id)
    u = db.session.get(User, member_id)

    if p and u:
        try:
            _upgrade_user_to_member_force(member_id)

            s, e = calculate_package_dates(member_id, p.duration)

            mp = MemberPackage(member_id=u.id, package_id=p.id,
                               startDate=s, endDate=e,
                               status=StatusPackage.ACTIVE)
            db.session.add(mp)

            inv = Invoice(member_id=u.id, total_amount=p.price,
                          status=StatusInvoice.PAID, payment_date=datetime.now())
            db.session.add(inv)

            d = InvoiceDetail(invoice=inv, member_package=mp, amount=p.price)
            db.session.add(d)

            db.session.commit()
            return inv

        except Exception as ex:
            db.session.rollback()
            return None
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



# RECEPTIONIST
def get_members_for_receptionist(kw=None, page=1):
    # query = MemberPackage.query.filter(MemberPackage.status == StatusPackage.ACTIVE)
    query = MemberPackage.query.join(MemberPackage.member) \
        .options(joinedload(MemberPackage.member)) \
        .options(joinedload(MemberPackage.coach)) \
        .options(joinedload(MemberPackage.package)) \
        .filter(MemberPackage.status == StatusPackage.ACTIVE)

    if kw:
        query = query.filter(Member.name.contains(kw))
    if page:
        start = (page - 1) * app.config['MEMBER_RECEP']
        query = query.slice(start, start + app.config['MEMBER_RECEP'])

    return query.all()


def count_members_for_receptionist():
    return MemberPackage.query \
        .options(joinedload(MemberPackage.member)) \
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


# if __name__ == '__main__':
#     with app.app_context():
#         u_id = 1
#         p_id = 1
#
#         success, msg = add_package_registration(u_id, p_id)
#
#         if success:
#             print(f"{msg}")
#         else:
#             print(f" Lỗi: {msg}")
