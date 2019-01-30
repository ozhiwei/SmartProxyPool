from .views import ProxyView, SettingView, FetcherView, ProxyPoolAdminIndexView
from .model import ProxyModel, SettingModel, FetcherModel

from flask_mongoengine import MongoEngine

from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, forms 

from flask_mongoengine import MongoEngine

from .model import User, Role
from .forms import LoginForm

from flask_security.utils import hash_password
from flask import url_for

from flask_admin import AdminIndexView, helpers, expose

import flask_admin

def init_base_data(*args):
    create_roles(*args)
    create_admin_user(*args)

def create_roles(user_datastore, app):
    with app.app_context():
        if not user_datastore.find_role(role='user'):
            user_datastore.create_role(name='user')
        if not user_datastore.find_role(role='superuser'):
            user_datastore.create_role(name='superuser')

def create_admin_user(user_datastore, app):
    with app.app_context():    
        if user_datastore.get_user("admin"):
            pass
        else:
            user_role = user_datastore.find_role(role='user')
            super_user_role = user_datastore.find_role(role='superuser')
            user_datastore.create_user(name='admin', email='admin', password=hash_password('admin'), roles=[user_role, super_user_role])

def init_security(user_datastore, app, admin):
    security = Security(app, user_datastore, login_form=LoginForm)

    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=helpers,
            get_url=url_for
        )

def init_app(app):
    admin = flask_admin.Admin(app=app, name='ProxyPool Admin', base_template="admin/master_base.html", index_view=ProxyPoolAdminIndexView(), template_mode='bootstrap3')
    admin.add_view(ProxyView(ProxyModel))
    admin.add_view(SettingView(SettingModel))
    # admin.add_view(ProxyPoolView(ProxyPoolModel))
    admin.add_view(FetcherView(FetcherModel))

    db = MongoEngine()
    db.init_app(app)

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    init_security(user_datastore, app, admin)

    init_base_data(user_datastore, app)

