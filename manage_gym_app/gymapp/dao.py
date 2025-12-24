import hashlib
from datetime import datetime, timedelta
from flask_mail import Message

from sqlalchemy.orm import joinedload
import cloudinary
from flask_login import current_user
from cloudinary import uploader  # them uploader de up anh luc dang ki
from gymapp import db, app, mail
from gymapp.models import (User, Member, UserRole, Exercise, Invoice, MemberPackage,
                           StatusInvoice, StatusPackage, Package, ExerciseSchedule, DayOfWeek,
                           PlanDetail, WorkoutPlan, PackageBenefit, Coach, PlanAssignment, Regulation)

from dateutil.relativedelta import relativedelta
from sqlalchemy import text, func, extract
from gymapp.states import get_invoice_state



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

def stats_revenue_package_usage():
    return (db.session.query(Package.id, Package.name, func.count(MemberPackage.id))
            .outerjoin(MemberPackage, MemberPackage.package_id == Package.id)
            .group_by(Package.id, Package.name)
            .order_by(Package.id).all())



def add_member_full_info(name, username, password, avatar,phone,gender,dob, email):
    u = Member(name=name,
               username=username.strip(),
               password=str(hashlib.md5(password.strip().encode('utf-8')).hexdigest()),phone=phone,gender=gender,dob=dob,email=email)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()
    return u

def get_workout_plan_by_member_id(member_id):
    return (db.session.query(PlanAssignment) \
            .join(MemberPackage, MemberPackage.id == PlanAssignment.member_package_id) \
            .filter(MemberPackage.member_id == member_id)\
            .order_by(PlanAssignment.start_date.desc())\
            .all())
def get_workout_plan_by_coach_id(coach_id):
    return WorkoutPlan.query.filter(WorkoutPlan.coach_id == coach_id).all()

def get_detail_workout_plan_by_id(workout_plan_id):
    return WorkoutPlan.query.get(workout_plan_id)

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

    try:
        _upgrade_user_to_member_force(user_id)

        new_registration = MemberPackage(
            member=member,
            package=package,
            status=StatusPackage.PENDING,
            coach_id=None
        )
        db.session.add(new_registration)

        new_invoice_pending = Invoice(
            member=member,
            status=StatusInvoice.PENDING,
            total_amount=package.price,
            invoice_day_create=datetime.now(),
            member_package=new_registration
        )
        db.session.add(new_invoice_pending)
        db.session.commit()

        return True, "Đăng ký thành công, vui lòng đến phòng gym để thanh toán và kích hoạt tài khoản!"

    except Exception as e:
        db.session.rollback()
        return False, str(e)

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
    return [e.value for e in DayOfWeek]


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


def get_latest_assignment_end_date(member_id):
    latest_assignment = (db.session.query(PlanAssignment)
                         .join(MemberPackage, MemberPackage.id == PlanAssignment.member_package_id)
                         .filter(MemberPackage.member_id == member_id)
                         .order_by(PlanAssignment.end_date.desc())
                         .first())

    if latest_assignment:
        return latest_assignment.end_date
    return None

def assign_existing_plan(coach_id, member_id, plan_id, start_date, end_date):
    plan = WorkoutPlan.query.get(plan_id)

    if plan and plan.coach_id == coach_id:
        packages = get_active_packages(coach_id, [member_id])
        if not packages:
            return False
        for pkg in packages:
            assignment = PlanAssignment(
                workout_plan=plan,
                member_package=pkg,
                start_date=start_date,
                end_date=end_date,
            )

            db.session.add(assignment)
        db.session.commit()
        return True

    return False


def add_workout_plan(name, plan, member_ids, start_date=None, end_date=None):

    if plan:
        p = WorkoutPlan(name=name, coach=current_user)
        db.session.add(p)

        if member_ids and start_date:
            packages = get_active_packages(coach_id=current_user.id, member_ids=member_ids)
            for pkg in packages:
                assignment = PlanAssignment(
                    workout_plan = p,
                    member_package = pkg,
                    start_date=start_date,
                    end_date=end_date
                )

                db.session.add(assignment)


        for ex in plan.values():
            pd = PlanDetail(exercise_id=ex['id'], reps=ex['reps'], sets=ex['sets'], workout_plan=p)
            db.session.add(pd)

            for day in ex['days']:
                day_enum = DayOfWeek(day)
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
  
def get_invoice_from_cur_user(user_id, date_filter=None, status_filter=None):
    query = Invoice.query.filter(Invoice.member_id == user_id)

    if date_filter:
        query = query.filter(func.date(Invoice.invoice_day_create) == date_filter)

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    return query.order_by(Invoice.id.desc()).all()

def get_package_name_by_invoice(invoice_id):
    try:
        inv = db.session.get(Invoice, invoice_id)
        if inv and inv.member_package:
            return inv.member_package.package.name
    except Exception as e:
        print(e)
    return "Không đăng kí gói nào"

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


def process_pending_invoice(invoice_id):
    is_valid, result = validate_cashier(invoice_id)

    if not is_valid:
        if result == "Hóa đơn đã quá hạn thanh toán":
            try:
                inv = db.session.get(Invoice, invoice_id)
                if inv:
                    inv.status = StatusInvoice.FAILED
                    db.session.commit()
                    return False, "Hóa đơn này đã quá hạn 7 ngày"
            except Exception as ex:
                db.session.rollback()
                return False, f"Lỗi khi tự động hủy đơn quá hạn: {str(ex)}"
        return False, result
    inv = result
    try:
        state = get_invoice_state(inv)
        success, msg = state.pay(calculate_date=calculate_package_dates)
        if success:
            db.session.commit()
        return success, msg
    except Exception as ex:
        db.session.rollback()
        return False, str(ex)

def add_member_package_and_pay(member_id, package_id):

    p = db.session.get(Package, package_id)
    u = db.session.get(User, member_id)

    if p and u:
        try:
            _upgrade_user_to_member_force(member_id)

            s, e = calculate_package_dates(member_id, p.duration)

            mp = MemberPackage(member_id=u.id, package_id=p.id, startDate=s, endDate=e, status=StatusPackage.ACTIVE)
            db.session.add(mp)
            inv = Invoice(member_id=u.id, total_amount=p.price,
                          status=StatusInvoice.PAID, payment_date=datetime.now())
            db.session.add(inv)

            db.session.commit()
            return inv
        except Exception as ex:
            db.session.rollback()
            return None
    return None


def cancel_pending_invoice(invoice_id):
    is_valid, result = validate_cashier(invoice_id)
    if not is_valid:
        return False, result

    inv = result
    try:
        state = get_invoice_state(inv)
        success, msg = state.cancel()
        if success:
            db.session.commit()
        return success, msg
    except Exception as ex:
        db.session.rollback()
        return False, str(ex)

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

#VALIDATE

def validate_cashier(invoice_id):
    if not invoice_id:
        return False, "Mã hóa đơn không được để trống"
    inv = db.session.query(Invoice).filter(Invoice.id == invoice_id).with_for_update().first() #pessimistic locking
    if not inv:
        return False, f"Hóa đơn mã {invoice_id} không tồn tại trong hệ thống"
    if inv.status != StatusInvoice.PENDING:
        return False, "Hóa đơn đã được thanh toán trước hoặc đã bị hủy"
    if not inv.member_package:
        return False, "Hóa đơn không có gói tập đi kèm"
    if not inv.member:
        return False, "Không tìm thấy thông tin hội viên của hóa đơn"
    if not inv.member_package.package:
        return False, "Gói tập đã bị xóa khỏi hệ thống"
    if inv.total_amount <= 0:
        return False, "Số tiền không hợp lệ"
    if inv.invoice_day_create:
        expired_day = 7
        expired_date = inv.invoice_day_create + timedelta(days = expired_day)
        if datetime.now() > expired_date:
            return False, "Hóa đơn đã quá hạn thanh toán"
    return True, inv

def validate_registration_package(member_id):
    active_package = MemberPackage.query.filter(MemberPackage.member_id == member_id,MemberPackage.status == 'ACTIVE').first()

    if active_package and active_package.endDate > datetime.now():
        end_date = active_package.endDate.strftime('%d/%m/%Y')
        return False, f"Gói '{active_package.package.name}' của bạn còn hạn đến {end_date}, nếu muốn đăng kí gói mới, vui lòng đến phòng gym để hủy gói hiện tại"

    pending_invoice = Invoice.query.filter(Invoice.member_id == member_id,Invoice.status == StatusInvoice.PENDING).first()

    if pending_invoice:
        create_date = pending_invoice.invoice_day_create.strftime('%H:%M %d/%m')
        return False, (f"Hội viên đã có một yêu cầu đăng ký chờ thanh toán lúc {create_date}."
                       f" Vui lòng xử lý hóa đơn cũ trước, nếu muốn đăng kí gói Khác, vui lòng đến phòng gym để hủy")

    return True, 'Thông tin hợp lệ'


#SEND MAIL
def send_mail(member_id, package_id):
    member = User.query.get(member_id)
    package = Package.query.get(package_id)

    msg = Message("Email xác nhận đăng kí thành công", recipients=[member.email])
    formatted_price = "{:,.0f}".format(package.price)

    msg.body = (f"Chào {member.name}, bạn đã đăng kí thành công gói {package.name}!\n" 
                f"Vui lòng chuẩn bị {formatted_price} VNĐ đến quầy thu ngân để thanh toán và kích hoạt tài khoản.")
    mail.send(msg)


#Thong ke

def active_member_stats(kw=None):
    query = db.session.query(Package.id, Package.name, func.count(MemberPackage.id))\
                      .join(MemberPackage, MemberPackage.package_id.__eq__(Package.id))\
                      .filter(MemberPackage.status.__eq__(StatusPackage.ACTIVE))
    if kw:
        query = query.filter(Package.name.contains(kw))
    return query.group_by(Package.id, Package.name).all()

def stats_revenue_by_month(time="month", year=datetime.now().year):
   query =  (db.session.query(func.extract(time, Invoice.payment_date), func.sum(Invoice.total_amount))
            .join(MemberPackage, Invoice.member_package_id == MemberPackage.id)
            .filter(Invoice.status == StatusInvoice.PAID,func.extract('year', Invoice.payment_date) == year)
            .group_by(func.extract(time, Invoice.payment_date))).all()
   return query

def count_members_by_time(year=datetime.now().year):
    query = (db.session.query(func.extract('month', User.join_date),func.count(User.id.distinct())).join(MemberPackage, User.id == MemberPackage.member_id)
           .filter(func.extract('year', User.join_date) == year,MemberPackage.status == 'active').group_by(func.extract('month', User.join_date))).all()
    return query

def stats_by_quarter(year=datetime.now().year):
    query = (db.session.query(func.extract('quarter', Invoice.payment_date), func.sum(Invoice.total_amount))
             .join(MemberPackage, Invoice.member_package_id == MemberPackage.id)
             .filter(Invoice.status == StatusInvoice.PAID,func.extract('year', Invoice.payment_date) == year)
             .group_by(func.extract('quarter', Invoice.payment_date)).order_by(func.extract('quarter', Invoice.payment_date)).all())
    return query
def count_active_members():
    return MemberPackage.query.filter(MemberPackage.status == StatusPackage.ACTIVE).count()

def get_gym_rules():
    return Regulation.query.filter(Regulation.code.like('GYM_RULE_%')).all()

#ADMIN
def add_exercise(name, description, image):
    try:
        ex = Exercise(name=name, description=description, image=image)
        db.session.add(ex)
        db.session.commit()
        return True, "Thêm bài tập thành công!"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def add_package(name, price, duration, description, image, benefits):
    try:
        p = Package(name=name, price=float(price), duration=int(duration), description=description, image=image)
        db.session.add(p)

        for b in benefits:
            if b.get('name'):
                benefit = PackageBenefit(name=b['name'], detail=b.get('detail', ''), package=p)
                db.session.add(benefit)

        db.session.commit()
        return True, "Thêm gói dịch vụ thành công!"

    except Exception as e:
        db.session.rollback()
        return False, str(e)

if __name__ == '__main__':
    with app.app_context():
        # u_id = 1
        # p_id = 1
        #
        # success, msg = add_package_registration(u_id, p_id)
        #
        # if success:
        #     print(f"{msg}")
        # else:
        #     print(f" Lỗi: {msg}")
        # pass
        print(active_member_stats())
        # print(stats_revenue_by_month(time='month', year=2025))
