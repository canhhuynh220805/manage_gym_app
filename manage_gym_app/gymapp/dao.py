import hashlib
from datetime import datetime

import cloudinary

from gymapp import db, app
from gymapp.models import User, Member, UserRole, Exercise, Invoice, InvoiceDetail, MemberPackage, StatusInvoice, \
    StatusPackage


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
