from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, forms 

from wtforms import fields, validators

class LoginForm(forms.LoginForm):
    name =  fields.StringField()
    email =  fields.StringField(label="Name or Email", validators=[validators.required()])
