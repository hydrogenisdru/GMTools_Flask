import datetime
import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    userName = StringField('userName', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    rememberMe = BooleanField('remember-me')
    submit = SubmitField('login')


class SignUpForm(FlaskForm):
    userName = StringField('userName', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_pwd = PasswordField('confirm_pwd', validators=[DataRequired()])
    submit = SubmitField('signup')
