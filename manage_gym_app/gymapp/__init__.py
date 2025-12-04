from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)
app.secret_key = 'JKHJHJK786575ghjghjg78675HJGJHGF^&$%$^*%*&^%&^&*%^&'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/gymdb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

cloudinary.config(cloud_name='dpl8syyb9',
                  api_key='423338349327346',
                  api_secret='zfwveRcXlclSOKM7mqSU2j0421c')