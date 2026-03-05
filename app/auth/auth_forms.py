from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError
import sqlalchemy as sqla

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField('Sign In')

