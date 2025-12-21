import hashlib
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.model import InlineFormAdmin
from flask_login import logout_user, current_user
from flask import redirect, request
from markupsafe import Markup

from gymapp import app, db, dao
from gymapp.dao import active_member_stats
from gymapp.models import UserRole, User, Member, Coach, Exercise, Package, Regulation, PackageBenefit


class AdminView(ModelView):

    def list_thumbnail(view, context, model, name):
        if not model.avatar:
            return ''
        return Markup(
            f'<img src="{model.avatar}" width="40" height="40" class="rounded-circle" style="object-fit: cover;" />')

    column_formatters = {
        'avatar': list_thumbnail
    }

    def on_model_change(self, form, model, is_created):
        if hasattr(form, 'password') and form.password.data:
            raw_password = form.password.data
            model.password = str(hashlib.md5(raw_password.strip().encode('utf-8')).hexdigest())

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UserView(AdminView):
    column_list = ['id', 'name', 'username', 'user_role', 'is_active', 'avatar', 'email']
    form_columns = ['name', 'username', 'password','user_role', 'phone', 'email', 'gender' ,'avatar', 'dob']
    column_searchable_list = ['name', 'username']
    column_filters = ['user_role', 'gender']

    create_modal = True
    edit_modal = True


class MemberView(AdminView):
    column_list = ['id', 'name', 'username', 'phone', 'gender', 'packages']
    column_searchable_list = ['name', 'phone']
    form_columns = ['name', 'username', 'password', 'phone', 'gender' ,'avatar', 'dob']
    create_modal = True
    edit_modal = True
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-user'


class CoachView(AdminView):
    column_list = ['id', 'name', 'username', 'phone', 'gender']
    form_columns = ['name', 'username', 'password', 'phone', 'gender', 'avatar', 'dob']
    create_modal = True
    edit_modal = True
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-dumbbell'

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.user_role = UserRole.COACH
        super().on_model_change(form, model, is_created)


class ExerciseView(AdminView):
    column_list = ['id', 'name', 'description', 'image']
    column_searchable_list = ['name']
    create_modal = True
    edit_modal = True
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-running'

    def list_img(view, context, model, name):
        if not model.image:
            return ''
        return Markup(f'<img src="{model.image}" width="80" class="img-thumbnail" />')

    column_formatters = {
        'image': list_img
    }

class PackageBenefitInline(InlineFormAdmin):
    form_label = 'Quyền lợi'
    form_columns = ['id', 'detail']

class PackageView(AdminView):
    column_list = ['name', 'duration', 'price', 'description', 'image']
    form_columns = ['name', 'duration', 'price', 'description', 'image']
    inline_models = (PackageBenefitInline(PackageBenefit),)
    create_modal = True
    edit_modal = True
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-box-open'

    def format_price(view, context, model, name):
        return "{:,.0f}".format(model.price)

    def list_img(view, context, model, name):
        if not model.image:
            return ''
        return Markup(f'<img src="{model.image}" width="50" />')

    column_formatters = {
        'price': format_price,
        'image': list_img
    }

class RegulationView(AdminView):
    column_list = ['name', 'value', 'code']
    can_create = True
    can_delete = True
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-gavel'

class LogoutView(BaseView):
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-sign-out-alt'
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/')

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class StatsRevenueViewByMonth(BaseView):
    @expose('/')
    def index(self):
        revenue_times = dao.stats_revenue_by_month("month")
        revenue_quarters = dao.stats_by_quarter()

        return self.render('admin/stats_revenue_by_month.html', revenue_times= revenue_times, quarterly_stats=revenue_quarters)

class StatsView(BaseView):
    menu_icon_type = 'fa'
    menu_icon_value = 'fa-chart-pie'
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        stats = dao.active_member_stats(kw=kw)

        return self.render('admin/stats.html', active_stats = stats)

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class StatsMemberViewByMonth(BaseView):
    @expose('/')
    def index(self):

        member_stats = dao.count_members_by_time()

        return self.render('admin/stats_member_by_month.html',
                           member_stats=member_stats)

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        cards_stats = {
            'members': dao.count_members(),
            'coaches': dao.count_coaches(),
            'packages': dao.count_packages(),
            'revenue': dao.get_total_revenue_month()
        }
        pkg_stats = dao.stats_revenue_package_usage()
        return self.render('admin/index.html', stats=cards_stats,pkg_stats=pkg_stats)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin = Admin(app=app, name="GYM Management", template_mode='bootstrap4', index_view=MyAdminIndexView(), base_template='admin/master.html',)

admin.add_view(UserView(User, db.session, name='Tài khoản hệ thống', category='Quản lý người dùng'))
admin.add_view(MemberView(Member, db.session, name='Hội viên', category='Quản lý người dùng'))
admin.add_view(CoachView(Coach, db.session, name='Huấn luyện viên', category='Quản lý người dùng'))
admin.add_view(ExerciseView(Exercise, db.session, name='Bài tập'))
admin.add_view(PackageView(Package, db.session, name='Gói dịch vụ'))
admin.add_view(RegulationView(Regulation, db.session, name='Quy định'))
admin.add_view(StatsRevenueViewByMonth(name='Thống kê doanh thu theo tháng'))
admin.add_view(StatsMemberViewByMonth(name='Thống kê hội viên theo tháng'))
admin.add_view(StatsView(name='Thống kê hội viên hoạt động'))
admin.add_view(LogoutView(name='Đăng xuất'))