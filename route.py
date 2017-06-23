from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_paginate import Pagination
from flask_pymongo import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from form import *
from application import login_manager, mongo, redis_store, mqAdaptor, proto, Blueprint, config
from models import User, PlayerInfo
from proto import gmCmdPro_pb2
from proto.encrypt import encode
import datetime
import demjson

bluePrint = Blueprint('blue_print', __name__, static_folder='static', template_folder='templates')


@bluePrint.route('/gm')
def index():
    if current_user.is_authenticated:
        return render_template('server_overview.html')
    else:
        return render_template('index.html')


@bluePrint.route('/gm/about')
def about():
    return render_template('about.html')


@bluePrint.route('/gm/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout()
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.gm_users.find_one({'userName': form.userName.data})
        if user is not None and check_password_hash(user['password'], form.password.data):
            login_user(User(user), form.rememberMe.data)
            return redirect(request.args.get('next') or url_for('.server_console'))
        else:
            flash('login: wrong user or password')
    return render_template("login.html", form=form)


@bluePrint.route('/gm/logout')
def logout():
    logout_user()
    flash('logout')
    return redirect(url_for('.index'))


@bluePrint.route('/gm/server_console')
def server_console():
    return redirect(url_for('.server_console_overview'))


@bluePrint.route('/gm/server_console/overview')
@login_required
def server_console_overview():
    return render_template('server_overview.html')


@bluePrint.route('/gm/server_console/report')
@login_required
def server_report():
    return render_template('server_report.html')


@bluePrint.route('/gm/gmtools')
@login_required
def gm_tools():
    return redirect(url_for('.gm_tools_overview'))


@bluePrint.route('/gm/gmtools/overview', methods=['GET', 'POST'])
@login_required
def gm_tools_overview():
    notice = Notice()
    if notice.validate_on_submit():
        if notice.markdown.data != '':
            gmNoticeNtf = gmCmdPro_pb2.GmNoticeNtf()
            gmNoticeNtf.notice = notice.markdown.data
            mqAdaptor.send(encode(gmCmdPro_pb2.GmNoticeNtf, gmNoticeNtf.SerializeToString()), '/topic/GmTopic')
    return render_template('gm_tools_overview.html', form=notice)


@bluePrint.route('/gm/gmtools/systemmail', methods=['GET', 'POST'])
@login_required
def gm_tools_system_mail():
    system_mail_form = SystemMailForm()
    if system_mail_form.validate_on_submit():
        playerList = list()
        content = dict()
        if system_mail_form.toWhere.data == 'all':
            zoneList = [111111, 222222, 333333]
        else:
            zoneList = system_mail_form.toWhere.data.split(',')
        if system_mail_form.toWhom.data != 'all':
            nameList = system_mail_form.toWhom.data.split(',')
            for name in nameList:
                for player in query_player(name):
                    playerList.append(player.uuid)
        if system_mail_form.content.data != 'none':
            content = demjson.decode(system_mail_form.content.data)
        mail_info = {
            'template': int(system_mail_form.template.data),
            'content': content,
            'createAt': datetime.datetime.now(),
            'toWhichZone': zoneList,
            'toWhom': playerList
        }
        info_string = demjson.encode(mail_info, encoding='utf-8')
        add_system_mail(mail_info)
        pullSystemMailNtf = gmCmdPro_pb2.PullSystemMailNtf()
        # data = pullSystemMailNtf.SerializeToString()
        # hex_id = '{0:04x}'.format(proto.msg_dict[gmCmdPro_pb2.PullSystemMailNtf])
        # buf = binascii.unhexlify(hex_id) + data
        # mqAdaptor.send(buf, 'GameServerQueue_4001')
        mqAdaptor.send(encode(gmCmdPro_pb2.PullSystemMailNtf, pullSystemMailNtf.SerializeToString()),
                       '/topic/GmTopic')
        flash('yeah! send a system mail: ' + info_string)
    return render_template('gm_tools_system_mail.html', system_mail_form=system_mail_form)


@bluePrint.route('/gm/gmtools/controls', defaults={'page': 1}, methods=['GET', 'POST'])
@bluePrint.route('/gm/gmtools/controls/page/<int:page>')
@login_required
def gm_tools_controls(page):
    search_form = SearchForm()
    player_list = list()
    if search_form.validate_on_submit():
        if search_form.searchInfo.data == 'none':
            flash('search:please enter search info')
        else:
            player_list = query_player(search_form.searchInfo.data)
    pagination = Pagination(page=page, total=player_list.__len__(), per_page=getattr(config['default'], 'PAGE_SIZE'),
                            bs_version='3')
    return render_template('gm_tools_controls.html', pagination=pagination, search_form=search_form,
                           playerlist=player_list)


@bluePrint.route('/gm/gmtools/profile/<uuid>')
@login_required
def gm_tools_controls_profile(uuid):
    profile = dict()
    profile['redis_info'] = query_player_from_redis(uuid)
    return render_template('controls_profile.html')


@bluePrint.route('/gm/gmtools/kick/<uuid>')
@login_required
def gm_tools_controls_kick(uuid):
    kickPlayerNtf = gmCmdPro_pb2.KickPlayerNtf()
    kickPlayerNtf.id = uuid
    mqAdaptor.send(encode(gmCmdPro_pb2.KickPlayerNtf, kickPlayerNtf.SerializeToString()), '/topic/GmTopic')
    return redirect(url_for('.gm_tools_controls'))


@bluePrint.route('/gm/gmtools/manage', methods=['GET', 'POST'], defaults={'page': 1})
@bluePrint.route('/gm/gmtools/manage/page/<int:page>')
@login_required
def gm_tools_account_manage(page):
    edit_user_form = EditUserForm()
    pageSize = getattr(config['default'], 'PAGE_SIZE')
    if current_user.is_authenticated and current_user.authority == 'admin':
        if edit_user_form.validate_on_submit():
            if edit_user_form.authority.data == 'none':
                if edit_user_form.password.data != edit_user_form.confirm_pwd.data:
                    flash('signup: please confirm your password')
                if not add_user(edit_user_form.userName.data, edit_user_form.password.data, 'gm_1'):
                    flash('signup: create user failed')
            else:
                if edit_user_form.password.data != edit_user_form.confirm_pwd.data:
                    flash('edit user: please confirm your password')
                else:
                    if not edit_user(edit_user_form.userName.data, edit_user_form.password.data,
                                     edit_user_form.authority.data):
                        flash('edit user: cannot find this user')
    page_user_list = list(user_collect_without_me(current_user.userName, (page - 1) * pageSize, pageSize))
    pagination = Pagination(page=page, total=total_user(), per_page=pageSize, bs_version='3')
    return render_template('gm_tools_account_manage.html', edit_account_form=edit_user_form, pagination=pagination,
                           page_user_list=page_user_list)


@bluePrint.route('/gm/delete/<userId>', methods=['GET', 'POST'])
@login_required
def delete_user(userId):
    if current_user.is_authenticated and current_user.authority == 'admin':
        delete_user(userId)
        flash('delete success')
        # return redirect(request.args.get('next') or url_for('gm_tools_account_manage'))
        return redirect(url_for('.gm_tools_account_manage'))
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/test/redis', methods=['GET'])
def test_redis():
    v = redis_store.hget('11936634706769_d', 'name')
    return v


@bluePrint.route('/gm/test/mq', methods=['GET'])
def test_mq():
    return proto.msg_dict[gmCmdPro_pb2.GmOnlineNtf()]
    # gmOnlineNtf = gmCmdPro_pb2.GmOnlineNtf()
    # gmOnlineNtf.id = 2222
    #
    # data = gmOnlineNtf.SerializeToString()
    # hex_id = '{0:04x}'.format(10108)
    # buf = binascii.unhexlify(hex_id) + data
    # mqAdaptor.send(buf, 'GameServerQueue_4001')
    # return 'success'


@bluePrint.route('/gm/test/mail', methods=['GET'])
def send_mail():
    content = {'1': 1, '2': 2}
    dic = {
        'template': 0,
        'content': content,
        'createAt': datetime.datetime.now(),
        'toWhichZone': [60001],
        'toWhom': []
    }
    add_system_mail(dic)
    return 'success'


@bluePrint.route('/gm/test/task', methods=['GET'])
def add_task():
    # from tasks import test, celery_app
    # result = add.delay(4, 4)
    # result.ready()
    return 'success'


@login_manager.user_loader
def load_user(user_id):
    me = mongo.db.gm_users.find_one({'_id': ObjectId(user_id)})
    if me:
        return User(me)
    else:
        return None


def add_system_mail(dic):
    return mongo.db.systemMail.insert_one(dic)


def add_user(user_name, password, authority):
    if mongo.db.gm_users.find_one({'userName': user_name}):
        return False
    else:
        mongo.db.gm_users.insert_one(
            {'userName': user_name, 'password': generate_password_hash(password), 'authority': authority})
    return True


def total_user():
    return mongo.db.gm_users.count()


def delete_user(user_id):
    mongo.db.gm_users.delete_one({'_id': ObjectId(user_id)})


def user_collect_without_me(my_name, skip_num, page_size):
    return mongo.db.gm_users.find({'userName': {'$ne': my_name}}).skip(skip_num).limit(page_size)


def edit_user(user_name, new_password, new_authority):
    if not mongo.db.gm_users.find_one({'userName': user_name}):
        return False
    else:
        mongo.db.gm_users.update_one({'userName': user_name}, {
            '$set': {'password': generate_password_hash(new_password), 'authority': new_authority}})
        return True


def query_player(search_info):
    result = list()
    for p in PlayerInfo.query.filter_by(userDesc=search_info):
        # v = dict()
        # v['userDesc'] = p.userDesc
        # v['uuid'] = p.uuid
        # v['suspensionExpiredDate'] = p.suspensionExpiredDate
        result.append(p)
    return result


def query_player_from_mysql(uuid):
    mysql_info = dict()
    p = PlayerInfo.query.filter_by(uuid=uuid)
    mysql_info['userDesc'] = p.userDesc
    mysql_info['uuid'] = p.uuid
    mysql_info['suspensionExpiredDate'] = p.suspensionExpiredDate


def query_player_from_redis(uuid):
    redis_info = dict()
    static_key = uuid + '_s'
    dynamic_key = uuid + '_d'
    redis_info['name'] = redis_store.hget(static_key, 'name')
    redis_info['division'] = redis_store.hget(static_key, 'division')
    redis_info['subDivision'] = redis_store.hget(static_key, 'subDivision')
    redis_info['level'] = redis_store.hget(static_key, 'level')
    redis_info['headShow'] = redis_store.hget(static_key, 'headShow')
    redis_info['gender'] = redis_store.hget(static_key, 'gender')
    redis_info['gameServerId'] = redis_store.hget(dynamic_key, 'gameServerId')
    redis_info['online'] = redis_store.hget(dynamic_key, 'online')
    return redis_info
