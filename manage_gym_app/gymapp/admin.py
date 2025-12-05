import hashlib

from flask import redirect
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user

from gymapp import app, db
from gymapp.models import UserRole, User, Member, Coach

admin = Admin(app=app, name='GYMApp')


class AuthenticatedModelView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class UserAdminView(AuthenticatedModelView):
    can_export = True
    column_list = ['id', 'name', 'user_role', 'gender', 'phone', 'is_active']
    form_columns = ['username', 'password', 'name', 'phone', 'gender', 'avatar', 'dob', 'user_role']
    page_size = 20
    column_searchable_list = ['name']
    column_filters = ['id', 'name', ]
    column_editable_list = ['name', 'dob', 'phone']
    edit_modal = True

    def get_query(self):
        return db.session.query(User).filter(User.type == 'user')

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data

        if raw_password:
            hashed_password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())
            model.password = hashed_password


class MemberView(AuthenticatedModelView):
    column_list = ['id', 'name', 'phone', 'gender', 'phone', 'packages']
    form_columns = ['username', 'password', 'name', 'phone', 'gender', 'avatar', 'dob']

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data

        if raw_password:
            hashed_password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())
            model.password = hashed_password


class CoachView(AuthenticatedModelView):
    column_list = ['id', 'name', 'phone', 'gender', 'phone']
    form_columns = ['username', 'password', 'name', 'phone', 'gender', 'avatar', 'dob']

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data

        if raw_password:
            hashed_password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())
            model.password = hashed_password
        if is_created:
            model.user_role = UserRole.COACH


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated


admin.add_view(UserAdminView(User, db.session))
admin.add_view(MemberView(Member, db.session))
admin.add_view(CoachView(Coach, db.session))
admin.add_view(LogoutView(name='Đăng xuất'))
