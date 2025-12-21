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
        return self.code


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
    dob = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100),nullable=True)
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


class WorkoutPlan(BaseModel):
    exercises = relationship('PlanDetail', backref='workout_plan', cascade='all, delete-orphan', lazy=True)
    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=False)
    member_packages = relationship('PlanAssignment', backref='workout_plan', lazy=True)

    def __str__(self):
        return self.name


class PlanDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    workout_plan_id = Column(Integer, ForeignKey(WorkoutPlan.id), nullable=False)
    exercise_id = Column(Integer, ForeignKey(Exercise.id), nullable=False)
    reps = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    exercise_schedules = relationship('ExerciseSchedule', backref='plan_detail', lazy=True,
                                      cascade='all, delete-orphan')


class ExerciseSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_detail_id = Column(Integer, ForeignKey(PlanDetail.id), nullable=False)

    day = Column(Enum(DayOfWeek), nullable=False)


class PlanAssignment(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)

    workout_plan_id = Column(Integer, ForeignKey(WorkoutPlan.id), nullable=False)
    member_package_id = Column(Integer, ForeignKey('member_package.id'), nullable=False)

    start_date = Column(DateTime, default=datetime.now())
    end_date = Column(DateTime, nullable=True)


class Package(BaseModel):
    duration = Column(Integer, nullable=False)
    price = Column(Double, nullable=False)
    description = Column(Text, nullable=False)
    members = relationship('MemberPackage', backref='package', lazy=True,
                           cascade="all, delete-orphan")  # Co the dung is_active de xoa an toan hon
    benefits = db.relationship("PackageBenefit", backref="package", lazy=True, cascade="all, delete-orphan")
    image = Column(String(100))


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
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    with app.app_context():
        db.create_all()
        # u = User(name='admin', username='admin', password = str(hashlib.md5("1".encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN,
        #          avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
        # db.session.add(u)
        packages = [
            {
                "id": 1,
                "name": "CLASSIC",
                "duration": 1,
                "price": 300000,
                "description": "Gói cơ bản với đầy đủ thiết bị và tiện ích cần thiết cho người mới bắt đầu.",
                "image" : "https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png"
            },
            {
                "id": 2,
                "name": "CLASSIC-PLUS",
                "duration": 1,
                "price": 500000,
                "description": "Nâng cấp từ CLASSIC, thêm quyền truy cập 24/7 và các dịch vụ phục hồi.",
                "image": "https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157774/bac_ljtnva.png"
            },
            {
                "id": 3,
                "name": "ROYRAL",
                "duration": 1,
                "price": 1500000,
                "description": "Gói cao cấp với PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.",
                "image" : "https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vang_igx7ax.png"
            },
            {
                "id": 4,
                "name": "SIGNATURE",
                "duration": 1,
                "price": 5000000,
                "description": "Gói VIP với tất cả quyền lợi ROYRAL, PT riêng nhiều buổi và ưu tiên dịch vụ tối đa.",
                "image": "https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vip_xsz4c4.png"
            }
        ]

        for p in packages:
            db.session.add(Package(**p))

        classic_benefits = [
            {
                "name": "Truy cập phòng tập",
                "detail": "Truy cập phòng tập từ 6:00 - 22:00 hằng ngày",
                "package_id": 1
            },
            {
                "name": "Sử dụng tất cả thiết bị",
                "detail": "Toàn bộ máy móc và khu vực tập luyện trong phòng gym",
                "package_id": 1
            },
            {
                "name": "Phòng thay đồ & tắm",
                "detail": "Tiện nghi cơ bản cho thành viên sau khi tập luyện",
                "package_id": 1
            },
            {
                "name": "Wi-Fi không giới hạn",
                "detail": "Kết nối internet tốc độ cao trong toàn khu vực phòng tập",
                "package_id": 1
            },
            {
                "name": "Nước uống miễn phí",
                "detail": "Cung cấp nước uống cơ bản trong mỗi buổi tập",
                "package_id": 1
            }
        ]

        for b in classic_benefits:
            db.session.add(PackageBenefit(**b))

        classic_plus_benefits = [
            {
                "name": "Truy cập 24/7",
                "detail": "Tập luyện bất cứ thời điểm nào trong ngày",
                "package_id": 2
            },
            {
                "name": "Tất cả quyền lợi của CLASSIC",
                "detail": "Bao gồm toàn bộ ưu đãi trong gói CLASSIC",
                "package_id": 2
            },
            {
                "name": "Phòng sauna & phục hồi",
                "detail": "Thư giãn và phục hồi thể lực sau buổi tập",
                "package_id": 2
            },
            {
                "name": "1 buổi PT/tháng miễn phí",
                "detail": "Một buổi huấn luyện viên cá nhân mỗi tháng",
                "package_id": 2
            }
        ]

        for b in classic_plus_benefits:
            db.session.add(PackageBenefit(**b))

        royral_benefits = [
            {
                "name": "Truy cập 24/7",
                "detail": "Không giới hạn thời gian sử dụng phòng tập",
                "package_id": 3
            },
            {
                "name": "4 buổi PT cá nhân/tháng",
                "detail": "Huấn luyện viên cá nhân theo sát mục tiêu tập luyện",
                "package_id": 3
            },
            {
                "name": "Tư vấn dinh dưỡng",
                "detail": "Xây dựng chế độ ăn phù hợp với thể trạng và mục tiêu",
                "package_id": 3
            },
            {
                "name": "Kiểm tra thân hình định kỳ",
                "detail": "Đo inbody và đánh giá kết quả luyện tập thường xuyên",
                "package_id": 3
            },
            {
                "name": "Phòng thư giãn cao cấp",
                "detail": "Không gian thư giãn riêng sau khi tập luyện",
                "package_id": 3
            },
            {
                "name": "Ưu tiên đặt lịch PT",
                "detail": "Dễ dàng chọn giờ đẹp với huấn luyện viên yêu thích",
                "package_id": 3
            }
        ]


        for b in royral_benefits:
            db.session.add(PackageBenefit(**b))

        signature_benefits = [
            {
                "name": "Tất cả quyền lợi gói ROYRAL",
                "detail": "Bao gồm truy cập 24/7, PT cá nhân, tư vấn dinh dưỡng và dịch vụ chăm sóc toàn diện.",
                "package_id": 4
            },
            {
                "name": "8 buổi PT cá nhân/tháng",
                "detail": "Lịch tập 1–1 với huấn luyện viên cá nhân, trung bình 2 buổi/tuần (tối đa 8 buổi/tháng).",
                "package_id": 4
            },
            {
                "name": "Huấn luyện viên riêng",
                "detail": "Một huấn luyện viên theo sát, xây dựng giáo trình và điều chỉnh bài tập riêng cho bạn.",
                "package_id": 4
            },
            {
                "name": "Phân tích cơ thể mỗi 2 tuần",
                "detail": "Đo chỉ số cơ thể (như InBody) định kỳ 2 tuần/lần để theo dõi tiến độ và tối ưu giáo án.",
                "package_id": 4
            },
            {
                "name": "Ưu tiên máy & phòng tập",
                "detail": "Ưu tiên đặt lịch sử dụng máy tập, phòng chức năng và các dịch vụ cao cấp trong giờ cao điểm.",
                "package_id": 4
            }
        ]

        for b in  signature_benefits:
            db.session.add(PackageBenefit(**b))
        u1 = Coach(name='đăng béo', username='dangbeo', password = str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.COACH,
                 avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
        u2 = User(name='canh huynh', username='canh', password = str(hashlib.md5("123456".encode('utf-8')).hexdigest()), user_role=UserRole.CASHIER,
                 avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
        u3 = Member(name='cozgdeptrai', username='cozg', password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
                  user_role=UserRole.USER,
                  avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
        u3 = Coach(name= 'hợi gym', username='hoigym', password = str(hashlib.md5("123".encode('utf-8')).hexdigest()), user_role=UserRole.COACH,
                     avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765199333/Screenshot_2025-12-08_200923_qqbckv.png")
        u4 = Member(name='ronaldo', username='ronaldo', password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                   user_role=UserRole.USER,
                   avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765200160/xb2vpquxw3gv0mxi7bbk.png")
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        e1 = Exercise(name="Pull up", description="vào lưng, tăng sức bền", image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172002_mjx9mg.png")
        e2 = Exercise(name="Dumbbel Press", description="vào ngực giữa, tăng sức bền", image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172013_x4kl3z.png")
        e3 = Exercise(name="Bar bell", description="vào ngực giữa, tăng sức bền", image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-12-06_101255_flozvt.png")
        e4 = Exercise(name="Dip", description="vào ngực dưới vai, tăng sức bền", image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764992819/Screenshot_2025-12-06_104738_c2u0nw.png")
        db.session.add(e1)
        db.session.add(e2)
        u5 = Member(name='messi', username='messi', password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
                    user_role=UserRole.USER,
                    avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1762914467/xby2eoj58t4dsi3u6vdj.jpg")

        db.session.add(u5)
        member = Member.query.filter(Member.name.contains('messi')).first()
        coach = Coach.query.filter(Coach.name.contains('gym')).first()
        p = Package(name="Gói đồng", description="miễn phí nước khăn tập", price=300000, duration=30)
        db.session.add(p)
        p = Package.query.filter(Package.name.contains("Đồng")).first()
        member_package = MemberPackage(member=member, package=p, startDate=datetime.now(), endDate=datetime.now() + timedelta(days=30), coach=coach)
        db.session.add(member_package)
        db.session.commit()
        # pass

        # u_admin = User(name='admin', username='admin',
        #                password=str(hashlib.md5("1".encode('utf-8')).hexdigest()),
        #                user_role=UserRole.ADMIN, type='user')
        #
        # u_cashier = User(name='canh huynh', username='canh',
        #                  password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #                  user_role=UserRole.CASHIER, type='user')
        #
        # db.session.add_all([u_admin, u_cashier])
        #
        # c1 = Coach(name='đăng béo', username='dangbeo',
        #            password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        #            user_role=UserRole.COACH)
        # c2 = Coach(name='hợi gym', username='hoigym',
        #            password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        #            user_role=UserRole.COACH)
        # db.session.add_all([c1, c2])
        #
        # m1 = Member(name='cozgdeptrai', username='cozg',
        #             password=str(hashlib.md5("123456".encode('utf-8')).hexdigest()),
        #             user_role=UserRole.USER)
        # m2 = Member(name='ronaldo', username='ronaldo',
        #             password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        #             user_role=UserRole.USER)
        # m3 = Member(name='messi', username='messi',
        #             password=str(hashlib.md5("123".encode('utf-8')).hexdigest()),
        #             user_role=UserRole.USER)
        # db.session.add_all([m1, m2, m3])
        #
        # p1 = Package(name="CLASSIC", duration=1, price=300000, description="Gói cơ bản.",
        #              image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/dong_uwvxli.png")
        # p2 = Package(name="CLASSIC-PLUS", duration=1, price=500000, description="Gói nâng cấp.",
        #              image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157774/bac_ljtnva.png")
        # p3 = Package(name="ROYAL", duration=1, price=1500000, description="Gói cao cấp.",
        #              image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vang_igx7ax.png")
        # p4 = Package(name="SIGNATURE", duration=1, price=5000000, description="Gói VIP.",
        #              image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1765157775/vip_xsz4c4.png")
        # db.session.add_all([p1, p2, p3, p4])
        #
        # e1 = Exercise(name="Pull up", description="vào lưng",
        #               image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172002_mjx9mg.png")
        # e2 = Exercise(name="Dumbbel Press", description="vào ngực",
        #               image="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764990983/Screenshot_2025-11-30_172013_x4kl3z.png")
        # db.session.add_all([e1, e2])
        #
        # mp = MemberPackage(
        #     member=m3,
        #     package=p1,
        #     startDate=datetime.now(),
        #     endDate=datetime.now() + relativedelta(months=1),
        #     status=StatusPackage.ACTIVE,
        #     coach=c2
        # )
        # db.session.add(mp)
        #
        # inv = Invoice(
        #     member=m3,
        #     total_amount=p1.price,
        #     status=StatusInvoice.PAID,
        #     payment_date=datetime.now(),
        #     invoice_day_create=datetime.now(),
        #     member_package=mp
        # )
        # db.session.add(inv)
        # db.session.commit()
        # pass

