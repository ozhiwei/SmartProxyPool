import mongoengine
from flask_mongoengine import Document
from flask_security import UserMixin, RoleMixin

class ProxyModel(Document):
    meta = {'collection': 'useful_proxy'}

    proxy = mongoengine.StringField(required=True, max_length=40)
    last_status = mongoengine.StringField(max_length=40)
    last_succ_time = mongoengine.DateTimeField()
    succ = mongoengine.IntField(default=0)
    fail = mongoengine.IntField(default=0)
    total = mongoengine.IntField(default=0)
    proxy_type = mongoengine.IntField(default=0)
    https = mongoengine.BooleanField(default=False)
    region_list = mongoengine.ListField(mongoengine.StringField(max_length=20))

    def __unicode__(self):
        return self.name

class SettingModel(Document):
    meta = {'collection': 'setting'}

    setting_group = mongoengine.StringField(required=True, max_length=40)    
    setting_name = mongoengine.StringField(required=True, unique=True, max_length=40)
    setting_value = mongoengine.StringField(required=True, max_length=40)
    setting_state = mongoengine.BooleanField(default=True)

class Role(Document, RoleMixin):
    name = mongoengine.StringField(max_length=80, unique=True)
    description = mongoengine.StringField(max_length=255)

class User(Document, UserMixin):
    email = mongoengine.StringField(max_length=255)
    name = mongoengine.StringField(max_length=255)
    password = mongoengine.StringField(max_length=255)
    active = mongoengine.BooleanField(default=True)
    confirmed_at = mongoengine.DateTimeField()
    roles = mongoengine.ListField(mongoengine.ReferenceField(Role), default=[])