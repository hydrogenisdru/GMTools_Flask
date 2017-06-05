import datetime
import re

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired, Length

AUTHORITY_LIST = [('none', 'none'), ('admin', 'admin'), ('gm_1', 'gm_1'), ('gm_2', 'gm_2'), ('gm_3', 'gm_3')]


class LoginForm(FlaskForm):
    userName = StringField('userName', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    rememberMe = BooleanField('remember-me')
    submit = SubmitField('login')


# class SignUpForm(FlaskForm):
#     userName = StringField('userName', validators=[DataRequired(), Length(1, 64)])
#     password = PasswordField('password', validators=[DataRequired()])
#     confirm_pwd = PasswordField('confirm_pwd', validators=[DataRequired()])
#     submit = SubmitField('signup')


class EditUserForm(FlaskForm):
    userName = StringField('userName', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_pwd = PasswordField('confirm_pwd', validators=[DataRequired()])
    authority = SelectField('authority', choices=AUTHORITY_LIST, validators=[DataRequired()])
    submit = SubmitField('apply')


class SearchForm(FlaskForm):
    searchInfo = StringField('searchInfo', validators=[DataRequired(), Length(1, 64)])
