from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
#from flask_babel import _, lazy_gettext as _l

class NewSecretariatForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    opening_hours = StringField('Opening Hours', validators=[DataRequired()])
    submit = SubmitField('Register')

class SecretKeyForm(FlaskForm):
    secret_key = StringField('Secret Key', validators=[DataRequired()])
    submit = SubmitField('Validate User')