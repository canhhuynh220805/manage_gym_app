import hashlib
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user
from flask import redirect
from markupsafe import Markup

from gymapp import app, db, dao
from gymapp.models import UserRole, User, Member, Coach, Exercise, Package, Regulation

class AdminView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class UserView(AdminView):
    column_list = ['id', 'name', 'username', 'user_role', 'is_active', 'avatar']
    column_searchable_list = ['name', 'username']
    column_filters = ['user_role', 'gender']

    create_modal = True
    edit_modal = True

    def _list_thumbnail(view, context, model, name):
        if not model.avatar:
            return ''
        return Markup(
            f'<img src="{model.avatar}" width="40" height="40" class="rounded-circle" style="object-fit: cover;" />')

    column_formatters = {
        'avatar': _list_thumbnail
    }

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data
        if raw_password:
            model.password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())

class MemberView(AdminView):
    column_list = ['id', 'name', 'username', 'phone', 'gender', 'packages']
    column_searchable_list = ['name', 'phone']
    create_modal = True
    edit_modal = True

    def _list_packages(view, context, model, name):
        package_names = [mp.package.name for mp in model.packages if mp.package]
        return ", ".join(package_names)

    column_formatters = {
        'packages': _list_packages
    }

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data
        if raw_password:
            model.password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())

class CoachView(AdminView):
    column_list = ['id', 'name', 'username', 'phone', 'gender']
    create_modal = True
    edit_modal = True

    def on_model_change(self, form, model, is_created):
        raw_password = form.password.data
        if raw_password:
            model.password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())
        if is_created:
            model.user_role = UserRole.COACH

class ExerciseView(AdminView):
    column_list = ['id', 'name', 'description', 'image']
    column_searchable_list = ['name']
    create_modal = True
    edit_modal = True

    def _list_img(view, context, model, name):
        if not model.image:
            return ''
        return Markup(f'<img src="{model.image}" width="80" class="img-thumbnail" />')

    column_formatters = {
        'image': _list_img
    }

class PackageView(AdminView):
    column_list = ['name', 'duration', 'price', 'description', 'image']
    form_columns = ['name', 'duration', 'price', 'description', 'image']
    create_modal = True
    edit_modal = True

    def _format_price(view, context, model, name):
        return "{:,.0f}".format(model.price)

    def _list_img(view, context, model, name):
        if not model.image:
            return ''
        return Markup(f'<img src="{model.image}" width="50" />')

    column_formatters = {
        'price': _format_price,
        'image': _list_img
    }

class RegulationView(AdminView):
    column_list = ['name', 'value']
    can_create = False
    can_delete = False

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin = Admin(app=app, name="GYM Management Admin",
              template_mode='bootstrap4',
              index_view=MyAdminIndexView())

admin.add_view(UserView(User, db.session, name='Tài khoản hệ thống', category='Quản lý người dùng'))
admin.add_view(MemberView(Member, db.session, name='Hội viên', category='Quản lý người dùng'))
admin.add_view(CoachView(Coach, db.session, name='Huấn luyện viên', category='Quản lý người dùng'))
admin.add_view(ExerciseView(Exercise, db.session, name='Bài tập'))
admin.add_view(PackageView(Package, db.session, name='Gói dịch vụ'))
admin.add_view(RegulationView(Regulation, db.session, name='Quy định'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))