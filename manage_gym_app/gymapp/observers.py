import threading
from gymapp import app, mail
from gymapp.models import User,Package
from flask_mail import Message

class RegistrationSubject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, user_id, package_id):
        for observer in self._observers:
            observer.update(user_id, package_id)

class Observer:
    def update(self, user_id, package_id):
        pass

class EmailNotificationObserver(Observer):
    def update(self, user_id, package_id):
        thread = threading.Thread(
            target=self.send_mail,
            kwargs={'member_id': user_id, 'package_id': package_id}
        )
        thread.start()

    def send_mail(self, member_id, package_id):
        with app.app_context():
            member = User.query.get(member_id)
            package = Package.query.get(package_id)

            msg = Message("Email xác nhận đăng kí thành công", recipients=[member.email])
            formatted_price = "{:,.0f}".format(package.price)
            msg.body = (f"Chào {member.name}, bạn đã đăng kí thành công gói {package.name}!\n"
                        f"Vui lòng chuẩn bị {formatted_price} VNĐ đến quầy thu ngân để thanh toán và kích hoạt gói.")
            mail.send(msg)