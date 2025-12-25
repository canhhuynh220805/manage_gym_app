import hashlib
from datetime import datetime, timedelta

from flask_login import UserMixin
from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey, Double, Text, column
import enum

from sqlalchemy.orm import relationship, backref

from gymapp import db, app


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    name = db.Column(String(100), nullable=False)


class Regulation(BaseModel):
    code = Column(String(100), nullable=False)
    value = Column(String(100), nullable=False)

    def __str__(self):
        return f"Regulation(code={self.code}, value={self.value}, name={self.name})"


# trạng thái hóa đơn
class StatusInvoice(enum.Enum):
    PENDING = 0
    PAID = 1
    FAILED = 2


# trạng thái gói tập
class StatusPackage(enum.Enum):
    ACTIVE = 1
    EXPIRED = 0
    PENDING = 2


# Ngày trong tuần
class DayOfWeek(enum.Enum):
    MONDAY = "Thứ 2"
    TUESDAY = "Thứ 3"
    WEDNESDAY = "Thứ 4"
    THURSDAY = "Thứ 5"
    FRIDAY = "Thứ 6"
    SATURDAY = "Thứ 7"
    SUNDAY = "Chủ nhật"


# Người dùng
class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2
    COACH = 3
    RECEPTIONIST = 4
    CASHIER = 5


# Giới tính
class Gender(enum.Enum):
    MALE = 0
    FEMALE = 1


class User(BaseModel, UserMixin):
    avatar = Column(String(150))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    join_date = Column(DateTime, default=datetime.now)
    dob = Column(DateTime, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), default=Gender.MALE)

    type = Column(String(50), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __str__(self):
        return self.name


class Member(User):
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    packages = relationship('MemberPackage', backref='member', lazy=True, cascade="all, delete-orphan")
    invoices = relationship('Invoice', backref='member', lazy=True, cascade="all, delete-orphan")
    __mapper_args__ = {
        'polymorphic_identity': 'member',
    }
    @property
    def current_package(self):
        for mp in self.packages:
            if mp.status == StatusPackage.ACTIVE:
                return mp.package.name
        return "Chưa có"

class Coach(User):
    id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    workout_plans = relationship("WorkoutPlan", backref="coach", lazy=True)
    assigned_packages = relationship('MemberPackage', backref='coach', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'trainer',
    }

# Tập luyện c5

class Exercise(BaseModel):
    description = Column(String(100), nullable=False)
    image = Column(String(150), nullable=False)
    workout_plans = relationship('PlanDetail', backref='exercise')
    def __str__(self):
        return f"Exercise(name={self.name}, description={self.description}, image={self.image})"


class WorkoutPlan(BaseModel):
    exercises = relationship('PlanDetail', backref='workout_plan', cascade='all, delete-orphan', lazy=True)
    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=False)
    member_packages = relationship('PlanAssignment', backref='workout_plan', lazy=True)

    def __str__(self):
        return self.name

    class Builder():
        def __init__(self):
            self.plan = WorkoutPlan()
            self.err_msg = []
            self.msg = []

        def set_info(self, name, coach_id):
            if not name:
                self.err_msg.append("Vui lòng nhập tên kế hoạch")
                return self
            self.plan.name = name
            self.plan.coach_id = coach_id
            return self

        def set_exercise(self, exercise):
            from gymapp import dao
            if not exercise:
                self.err_msg.append("Kế hoạch chưa có bài tập nào! Vui lòng chọn bài tập.")
                return self

            self.plan.exercises = []
            max_day = int(dao.get_regulation_by_code("MAX DAY PRACTISE").value)
            for ex in exercise.values():
                ex_name = ex.get('name', 'Bài tập')
                sets = int(ex.get('sets', 0))
                reps = int(ex.get('reps', 0))
                days = ex.get('days', [])
                if sets <= 0 or reps <= 0:
                    self.err_msg.append(f'Bài "{ex_name}" chưa nhập số hiệp/lần tập hợp lệ!, số hiệp và số lần phải lớn hơn 0')
                    return self
                if len(days) == 0:
                    self.err_msg.append(
                        f'Bài "{ex_name}" chưa chọn ngày tập!, vui lòng chọn ít nhất 1 ngày')
                    return self
                if len(days) > max_day:
                    self.err_msg.append(
                        f'Bài "{ex_name}"  vượt quá số ngày tập quy định, quy định chỉ cho tập tối đa {max_day}')
                    return self
                ex_detail = PlanDetail(
                    exercise_id=int(ex.get('id')),
                    reps=sets,
                    sets=reps,
                )
                days = ex.get('days', [])
                for day in days:
                    day_enum = DayOfWeek(day)
                    ex_detail.exercise_schedules.append(
                        ExerciseSchedule(day=day_enum)
                    )

                self.plan.exercises.append(ex_detail)
            return self

        def set_member(self, member_ids, start_date, end_date):
            from gymapp import dao
            if not member_ids:
                return self

            if not start_date or not end_date:
                self.err_msg.append("Vui lòng chọn ngày bắt đầu và ngày kết thúc")
                return self

            if self.plan.exercises == None:
                self.err_msg.append('Kế hoạch chưa có bài tập nào! Vui lòng chọn bài tập.')
                return self

            if start_date and end_date:
                start_date = datetime.strptime(start_date[:10], "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date[:10], "%Y-%m-%d").date()
                if start_date >= end_date:
                    self.err_msg.append("Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
                    return self
                if start_date < datetime.now().date():
                    self.err_msg.append("Ngày bắt đầu không được ở trong quá khứ")
                    return self

            for m_id in member_ids:
                end_lates_date = dao.get_latest_assignment_end_date(m_id)
                if end_lates_date and start_date <= end_lates_date.date():
                    fmt_date = end_lates_date.strftime('%d/%m/%Y')
                    u = dao.get_user_by_id(m_id)
                    self.err_msg.append(
                        f"Hội viên {u.name} đang bận tập giáo án cũ đến hết ngày {fmt_date}. Vui lòng chọn ngày bắt đầu sau ngày này!")
                    return self

            if member_ids and start_date:
                packages = dao.get_active_packages(coach_id=self.plan.coach_id, member_ids=member_ids)
                for pkg in packages:
                    assignment = PlanAssignment(
                        workout_plan=self.plan,
                        member_package=pkg,
                        start_date=start_date,
                        end_date=end_date
                    )
                    self.plan.member_packages.append(assignment)
            return self

        def build(self):
            if self.err_msg:
                return False, " | ".join(self.err_msg), None

            try:
                db.session.add(self.plan)
                db.session.commit()
                self.msg.append("Tạo kế hoạch thành công!")
                return True, None, self.msg
            except Exception as e:
                db.session.rollback()
                self.err_msg.append(f"Lỗi lưu Database: {str(e)}")
                return False, self.err_msg, None


class PlanDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_plan_id = Column(Integer, ForeignKey(WorkoutPlan.id), nullable=False)
    exercise_id = Column(Integer, ForeignKey(Exercise.id), nullable=False)
    reps = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    exercise_schedules = relationship('ExerciseSchedule', backref='plan_detail', lazy=True,
                                      cascade='all, delete-orphan')
    # def __str__(self):
    #     return f'Giáo án {self.id}'


class ExerciseSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_detail_id = Column(Integer, ForeignKey(PlanDetail.id), nullable=False)

    day = Column(Enum(DayOfWeek), nullable=False)


class PlanAssignment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)

    workout_plan_id = Column(Integer, ForeignKey(WorkoutPlan.id), nullable=False)
    member_package_id = Column(Integer, ForeignKey('member_package.id'), nullable=False)

    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)


class Package(BaseModel):
    duration = Column(Integer, nullable=False)
    price = Column(Double, nullable=False)
    description = Column(Text, nullable=False)
    members = relationship('MemberPackage', backref='package', lazy=True,
                           cascade="all, delete-orphan")  # Co the dung is_active de xoa an toan hon
    benefits = db.relationship("PackageBenefit", backref="package", lazy=True, cascade="all, delete-orphan")
    image = Column(String(100))

    def __str__(self):
        return f"Package (name={self.name}, duration={self.duration}, price={self.price})"


class PackageBenefit(BaseModel):
    detail = Column(Text, nullable=True)
    package_id = db.Column(db.Integer, db.ForeignKey(Package.id), nullable=False)


class MemberPackage(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    package_id = Column(Integer, ForeignKey(Package.id), nullable=False)
    startDate = Column(DateTime, nullable=True)  # CHO PHÉP NULLABLE NGÀY ĐĂNG KÍ
    endDate = Column(DateTime, nullable=True)  # CHO PHÉP NULLABLE NGÀY HẾT HẠN
    status = Column(Enum(StatusPackage), default=StatusPackage.ACTIVE)

    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=True)
    workout_plans = relationship(PlanAssignment, lazy='subquery', backref='member_package')


class Invoice(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    member_package_id = Column(Integer, ForeignKey('member_package.id'), nullable=False)
    status = Column(Enum(StatusInvoice), default=StatusInvoice.PENDING)
    total_amount = Column(Double, nullable=False)
    payment_date = Column(DateTime, nullable=True)
    invoice_day_create = Column(DateTime, nullable=True)
    member_package = relationship('MemberPackage', backref='invoice', lazy=True)


if __name__ == '__main__':
    from sqlalchemy import text
    from dateutil.relativedelta import relativedelta
    with app.app_context():
        db.create_all()
        default_avt = "https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg"
        coaches = [
            Coach(name='đăng béo', username='dangbeo',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE, avatar=default_avt,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='hợi gym', username='hoigym',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE,
                  avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765199333/Screenshot_2025-12-08_200923_qqbckv.png",
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='Lê trung chính', username='chinh',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE,
                  dob=datetime(2025, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='Ông Zũ', username='vu',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE,
                  dob=datetime(2025, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='công ngu', username='cong',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='123', gender=Gender.MALE,
                  dob=datetime(2025, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='Phạm Kim Nhân', username='nhan',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE,
                  dob=datetime(2025, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
            Coach(name='Sam Sulek', username='sam',
                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.COACH, phone='0969293472', gender=Gender.MALE,
                  dob=datetime(2025, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),
        ]
        members = [
            Member(name='cozgdeptrai', username='cozg',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, gender=Gender.MALE,phone='0969293472',
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='ronaldo', username='ronaldo',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, gender=Gender.MALE,phone='0969293472',
                   avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765200160/xb2vpquxw3gv0mxi7bbk.png",
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='messi', username='messi',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, gender=Gender.MALE,phone='0969293472',
                   avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1762914467/xby2eoj58t4dsi3u6vdj.jpg",
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='neymar', username='neymar',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, phone='0969293472', gender=Gender.MALE,
                   dob=datetime(2002, 12, 12, 19, 29, 53),email="huynhthecanhpvh@gmail.com"),

            Member(name='robben', username='robben',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, phone='123', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='muller', username='muller',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, phone='123', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='vinicius', username='vinicius',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, phone='123', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='Antony De Santos', username='antony',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER, phone='0969293472', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            Member(name='cong36', username='cong36',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                   user_role=UserRole.USER, email='huynhthecanhpvh@gmail.com', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0)),

            Member(name='Ngô Công Danh', username='danh',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                   user_role=UserRole.USER, email='danh03112005@gmail.com', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0)),

            Member(name='Ung Nguyễn Anh Tuấn', username='tuan',
                   password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                   user_role=UserRole.USER, email='ungtuan0812@gmail.com', gender=Gender.MALE,
                  dob=datetime(2000, 12, 12, 18, 46, 0)),
        ]
        others = [
            # ADMIN
            User(name='admin', username='admin',
                 password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                 user_role=UserRole.ADMIN, gender=Gender.MALE, avatar=default_avt,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            # CASHIER
            User(name='canh huynh', username='canh',
                 password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                 user_role=UserRole.CASHIER, gender=Gender.MALE, avatar=default_avt,
                  dob=datetime(2000, 12, 12, 18, 46, 0),email="huynhthecanhpvh@gmail.com"),

            # RECEPTIONIST
            User(name='nem chua', username='letan',
                 password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),phone='0969293472',
                 user_role=UserRole.RECEPTIONIST, gender=Gender.MALE, avatar=default_avt,
                 dob=datetime(2025, 12, 11, 21, 39, 0)
                 ,email="huynhthecanhpvh@gmail.com"),
        ]
        exercises = [
            Exercise(
                name="Pull up",
                description="vào lưng, tăng sức bền",
                image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172002_mjx9mg.png"
            ),
            Exercise(
                name="Dumbbel Press",
                description="vào ngực giữa, tăng sức bền",
                image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172013_x4kl3z.png"
            ),
            Exercise(
                name="Bar bell",
                description="vào ngực giữa, tăng sức bền",
                image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-12-06_101255_flozvt.png"
            ),
            Exercise(
                name="Dip",
                description="vào ngực dưới vai, tăng sức bền",
                image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764992819/Screenshot_2025-12-06_104738_c2u0nw.png"
            )
        ]
        packages = [
            Package(
            id=1, name="CLASSIC", duration=1, price=300000,
            description="Gói cơ bản với đầy đủ thiết bị và tiện ích cần thiết cho người mới bắt đầu.",
            image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png"
        ),Package(
            id=2, name="CLASSIC-PLUS", duration=1, price=500000,
            description="Nâng cấp từ CLASSIC, thêm quyền truy cập 24/7 và các dịch vụ phục hồi.",
            image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157774/bac_ljtnva.png"
        ),Package(
            id=3, name="ROYAL", duration=1, price=1500000,
            description="Gói cao cấp với PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.",
            image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vang_igx7ax.png"
        ),Package(
            id=4, name="SIGNATURE", duration=1, price=5000000,
            description="Gói VIP với tất cả quyền lợi ROYRAL, PT riêng nhiều buổi và ưu tiên dịch vụ tối đa.",
            image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vip_xsz4c4.png"
        )
            ]
        classic_benefits = [
            PackageBenefit(name="Truy cập phòng tập", detail="Truy cập phòng tập từ 6:00 - 22:00 hằng ngày",
                           package_id=1),
            PackageBenefit(name="Sử dụng tất cả thiết bị",
                           detail="Toàn bộ máy móc và khu vực tập luyện trong phòng gym", package_id=1),
            PackageBenefit(name="Phòng thay đồ & tắm", detail="Tiện nghi cơ bản cho thành viên sau khi tập luyện",
                           package_id=1),
            PackageBenefit(name="Wi-Fi không giới hạn",
                           detail="Kết nối internet tốc độ cao trong toàn khu vực phòng tập", package_id=1),
            PackageBenefit(name="Nước uống miễn phí", detail="Cung cấp nước uống cơ bản trong mỗi buổi tập",
                           package_id=1)
        ]
        classic_plus_benefits = [
            PackageBenefit(name="Truy cập 24/7", detail="Tập luyện bất cứ thời điểm nào trong ngày", package_id=2),
            PackageBenefit(name="Tất cả quyền lợi của CLASSIC", detail="Bao gồm toàn bộ ưu đãi trong gói CLASSIC",
                           package_id=2),
            PackageBenefit(name="Phòng sauna & phục hồi", detail="Thư giãn và phục hồi thể lực sau buổi tập",
                           package_id=2),
            PackageBenefit(name="1 buổi PT/tháng miễn phí", detail="Một buổi huấn luyện viên cá nhân mỗi tháng",
                           package_id=2)
        ]
        royal_benefits = [
            PackageBenefit(name="Truy cập 24/7", detail="Không giới hạn thời gian sử dụng phòng tập", package_id=3),
            PackageBenefit(name="4 buổi PT cá nhân/tháng", detail="Huấn luyện viên cá nhân theo sát mục tiêu tập luyện",
                           package_id=3),
            PackageBenefit(name="Tư vấn dinh dưỡng", detail="Xây dựng chế độ ăn phù hợp với thể trạng và mục tiêu",
                           package_id=3),
            PackageBenefit(name="Kiểm tra thân hình định kỳ",
                           detail="Đo inbody và đánh giá kết quả luyện tập thường xuyên", package_id=3),
            PackageBenefit(name="Phòng thư giãn cao cấp", detail="Không gian thư giãn riêng sau khi tập luyện",
                           package_id=3),
            PackageBenefit(name="Ưu tiên đặt lịch PT", detail="Dễ dàng chọn giờ đẹp với huấn luyện viên yêu thích",
                           package_id=3)
        ]
        signature_benefits = [
            PackageBenefit(name="Tất cả quyền lợi gói ROYRAL",
                           detail="Bao gồm truy cập 24/7, PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.",
                           package_id=4),
            PackageBenefit(name="8 buổi PT cá nhân/tháng",
                           detail="Lịch tập 1–1 với huấn luyện viên cá nhân, trung bình 2 buổi/tuần (tối đa 8 buổi/tháng).",
                           package_id=4),
            PackageBenefit(name="Huấn luyện viên riêng",
                           detail="Một huấn luyện viên theo sát, xây dựng giáo trình và điều chỉnh bài tập riêng cho bạn.",
                           package_id=4),
            PackageBenefit(name="Phân tích cơ thể mỗi 2 tuần",
                           detail="Đo chỉ số cơ thể (như InBody) định kỳ 2 tuần/lần để theo dõi tiến độ và tối ưu giáo án.",
                           package_id=4),
            PackageBenefit(name="Ưu tiên máy & phòng tập",
                           detail="Ưu tiên đặt lịch sử dụng máy tập, phòng chức năng và các dịch vụ cao cấp trong giờ cao điểm.",
                           package_id=4)
        ]
        regulations = [
            Regulation(code='MAX DAY PRACTISE', name='Số ngày tập tối đa/tuần', value='6'),
            Regulation(code='GYM_RULE_SHIRT', name='Quy định trang phục', value='Không được cởi trần trong phòng tập'),
            Regulation(code='GYM_RULE_EQUIPMENT', name='Sử dụng thiết bị',value='Cất tạ về đúng vị trí sau khi sử dụng'),
            Regulation(code='GYM_RULE_SMOKE', name='Cấm chất kích thích', value='Hoàn toàn không hút thuốc trong khuôn viên tập luyện')
        ]
        db.session.add_all(regulations)
        db.session.add_all(coaches)
        db.session.add_all(members)
        db.session.add_all(others)
        db.session.add_all(exercises)
        db.session.add_all(packages)
        db.session.add_all(classic_benefits)
        db.session.add_all(classic_plus_benefits)
        db.session.add_all(signature_benefits)
        db.session.add_all(royal_benefits)
        regulation = Regulation(code='MAX_PRACTISE_DAY', name='Quy định số ngày tập tối đa', value='5')
        db.session.add(regulation)
        db.session.commit()

