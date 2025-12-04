import hashlib
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, String, Enum, DateTime, Integer, ForeignKey, Double, Text
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

#trạng thái hóa đơn
class StatusInvoice(enum.Enum):
    PENDING = 0
    PAID = 1
    FAILED = 2

#trạng thái gói tập
class StatusPackage(enum.Enum):
    ACTIVE = 1
    EXPIRED = 0

# Ngày trong tuần
class DayOfWeek(enum.Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


# Người dùng
class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2
    COACH = 3
    RECEPTIONIST = 4
    CASHER = 5

#Giới tính
class Gender(enum.Enum):
    MALE = 0
    FEMALE = 1

class User(BaseModel, UserMixin):
    avatar = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    join_date = Column(DateTime, default=datetime.now)
    dob = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    gender = Column(Enum(Gender), default=Gender.MALE)

    type = Column(String(50), nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __str__(self):
        return self.name


class Member(User):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    packages = relationship('MemberPackage', backref='package', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'member',
    }


class Coach(User):
    id = Column(Integer, ForeignKey(User.id), primary_key=True)
    workout_plans = relationship("WorkoutPlan", backref="coach", lazy=True)
    assigned_packages = relationship('MemberPackage', backref='assigned_coach', lazy=True)
    __mapper_args__ = {
        'polymorphic_identity': 'trainer',
    }


# Tập luyện

class Exercise(BaseModel):
    description = Column(String(100), nullable=False)
    workout_plans = relationship('PlanDetail', backref='workout_plan')


class WorkoutPlan(BaseModel):
    exercises = relationship('PlanDetail', backref='exercise', cascade='all, delete-orphan')
    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=False)


class PlanDetail(BaseModel):
    workout_plan_id = Column(Integer, ForeignKey(WorkoutPlan.id), primary_key=True)
    exercise_id = Column(Integer, ForeignKey(Exercise.id), primary_key=True)
    reps = Column(Integer, nullable=False)
    sets = Column(Integer, nullable=False)
    note = Column(String(100), nullable=True)
    exercise_schedules = relationship('ExerciseSchedule', backref='plan_detail', lazy=True,
                                      cascade='all, delete-orphan')
    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=False)


class ExerciseSchedule(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_detail_id = Column(Integer, ForeignKey(PlanDetail.id), nullable=False)

    day = Column(Enum(DayOfWeek), nullable=False)


#Hóa đơn, gói tập
package_plan_ssignment = db.Table('package_plan_ssignment',
                                   Column('workout_plan_id', Integer, ForeignKey(WorkoutPlan.id), nullable=False),
                                   Column('member_package_id', Integer, ForeignKey('member_package.id'), nullable=False))

class Package(BaseModel):
    duration = Column(Integer, nullable=False)
    price = Column(Double, nullable=False)
    description = Column(Text, nullable=False)
    members = relationship('MemberPackage', backref='member', lazy=True)

class MemberPackage(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    package_id = Column(Integer, ForeignKey(Package.id), nullable=False)

    startDate = Column(DateTime, nullable=False)
    endDate = Column(DateTime, nullable=False)
    status = Column(Enum(StatusPackage), default=StatusPackage.ACTIVE)

    coach_id = Column(Integer, ForeignKey(Coach.id), nullable=True)
    workout_plans = relationship(WorkoutPlan, secondary=package_plan_ssignment, lazy='subquery',
                                 backref=backref('member_packages', lazy=True))
    invoice_details = relationship('InvoiceDetail', backref='member_package', lazy=True)


class Invoice(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey(Member.id), nullable=False)
    status = Column(Enum(StatusInvoice), default=StatusInvoice.PENDING)
    total_amount = Column(Double, nullable=False)
    payment_date = Column(DateTime, default=datetime.now)

    invoice_details = relationship('InvoiceDetail', backref='invoice', lazy=True)

class InvoiceDetail(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)

    invoice_id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    amount = Column(Double, nullable=False)
    quantity = Column(Integer, default=1)
    member_package_id = Column(Integer, ForeignKey(MemberPackage.id), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()
        # u = User(name='admin', username='admin', password = str(hashlib.md5("12346".encode('utf-8')).hexdigest()), user_role=UserRole.ADMIN,
        #          avatar="https://res.cloudinary.com/dpl8syyb9/image/upload/v1764237405/ecjxy41wdhl7k03scea8.jpg")
        # db.session.add(u)
        # db.session.commit()
        pass