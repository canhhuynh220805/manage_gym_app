from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = 'JKHJHJK786575ghjghjg78675HJGJHGF^&$%$^*%*&^%&^&*%^&'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:nguyenvancong@localhost/gymdb?charset=utf8mb4"
# app.config['SQLALCHEMY_ECHO'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
app.config['MEMBER_RECEP'] = 4

#CẤU HÌNH GỦI MAIL
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nguyenvancong72033@gmail.com'
app.config['MAIL_PASSWORD'] = 'gsds nkxm lpeb qepo'
app.config['MAIL_DEFAULT_SENDER'] = ('Gym Center Support', 'nguyenvancong72033@gmail.com')


mail = Mail(app=app)
db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(cloud_name='dpl8syyb9',
                  api_key='423338349327346',
                  api_secret='zfwveRcXlclSOKM7mqSU2j0421c')