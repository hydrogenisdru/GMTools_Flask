from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_paginate import Pagination
from flask_pymongo import DESCENDING
from flask_pymongo import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from form import *
from manager import app
from gm_application import login_manager, mongo
from models import User


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('server_overview.html')
    else:
        return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'userName': form.userName.data})
        if user is not None and check_password_hash(user['password'], form.password.data):
            login_user(User(user), form.rememberMe.data)
            return redirect(request.args.get('next') or url_for('server_console'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('already logout.')
    return redirect(url_for('index'))


@app.route('/server_console')
def server_console():
    return redirect(url_for('server_console_overview'))


@app.route('/server_console/overview')
@login_required
def server_console_overview():
    return render_template('server_overview.html')


@app.route('/server_console/report')
@login_required
def server_report():
    return render_template('server_report.html')


@app.route('/gmtools')
@login_required
def gm_tools():
    return redirect(url_for('gm_tools_overview'))


@app.route('/gmtools/overview')
@login_required
def gm_tools_overview():
    return render_template('gm_tools_overview.html')


@login_manager.user_loader
def load_user(user_id):
    me = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if me:
        return User(me)
    else:
        return None
