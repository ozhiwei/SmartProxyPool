import math
import time
from flask import request
from flask_security import current_user

import flask_admin
from flask import Flask, jsonify, url_for, redirect, render_template, request
from flask_admin.contrib.mongoengine import ModelView
from flask_admin import expose

from Notify.NotifyManager import dispatch_notify

# project import
from Config.ConfigManager import config
from Manager.ProxyManager import proxy_manager

CUSTOM_COLUMN_FORMAT = {
    "proxy_type" : {
        "0": "未知代理",
        "1": "透明代理",
        "2": "匿名代理",
    },
    "https" : {
        "False": "不支持",
        "True": "支持",
    }
}

def ElapseTimeFormat(all_time):
    day = 24*60*60
    hour = 60*60
    min = 60
    if all_time <60:        
        return  "%d sec"%math.ceil(all_time)
    elif  all_time > day:
        days = divmod(all_time,day) 
        return "%d days, %s"%(int(days[0]),ElapseTimeFormat(days[1]))
    elif all_time > hour:
        hours = divmod(all_time,hour)
        return '%d hours, %s'%(int(hours[0]),ElapseTimeFormat(hours[1]))
    else:
        mins = divmod(all_time,min)
        return "%d mins, %d sec"%(int(mins[0]),math.ceil(mins[1]))

def LastSuccTimeFormat(last_time):
    if last_time:
        result = ElapseTimeFormat(int(time.time() - last_time))
    else:
        result = 0

    return result

class ProxyView(ModelView):
    name = "ProxyPool"

    column_list = ("proxy", "succ", "fail", "total", "proxy_type", "https", "last_status", "last_succ_time", "region_list")
    can_set_page_size = True
    can_create = False
    column_formatters = dict(
        proxy_type=lambda v, c, m, p: CUSTOM_COLUMN_FORMAT[p][str(m.proxy_type)],
        https=lambda v, c, m, p: CUSTOM_COLUMN_FORMAT[p][str(m.https)],
        last_succ_time=lambda v, c, m, p: LastSuccTimeFormat(m.last_succ_time),
    )

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        if current_user.is_authenticated:
            pass
        else:
            return redirect(url_for('security.login', next=request.url))

class SettingView(ModelView):
    name="Setting"

    can_set_page_size = True
    can_create = False
    can_delete = False
    can_view_details = True
    column_searchable_list = ['setting_name']
    column_editable_list = [ "setting_value", "setting_state"]

    def is_accessible(self):
        result = None
        if not current_user.is_active or not current_user.is_authenticated:
            result = False

        if current_user.has_role('superuser'):
            result = True

        return result

    def _handle_view(self, name, **kwargs):
        if current_user.is_authenticated:
            pass
        else:
            return redirect(url_for('security.login', next=request.url))

    def after_model_change(self, form, model, is_created):
        print("after_model_change", model.setting_group, model.setting_name, model.setting_value, is_created)
        dispatch_notify("reload_config_from_db")
        dispatch_notify(model.setting_name, job_id=model.setting_name)

class ProxyPoolAdminIndexView(flask_admin.AdminIndexView):

    @expose()
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('security.login'))
        return super(ProxyPoolAdminIndexView, self).index()
