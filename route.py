from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, login_user, logout_user, current_user
from flask_paginate import Pagination
from flask_pymongo import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from form import *
from application import login_manager, mongo, mongo_analysis, redis_store, mqAdaptor, proto, bluePrint, config, \
    a_updater
from models import User, PlayerInfo
from proto import gmCmdPro_pb2
from proto.encrypt import encode
import datetime
import demjson
from cStringIO import StringIO


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
    if current_user.is_authenticated:
        notice = Notice()
        if notice.validate_on_submit():
            if notice.markdown.data != '':
                gmNoticeNtf = gmCmdPro_pb2.GmNoticeNtf()
                gmNoticeNtf.notice = notice.markdown.data
                mqAdaptor.send(encode(proto.msg_dict[gmCmdPro_pb2.GmNoticeNtf], gmNoticeNtf.SerializeToString()),
                               '/topic/GmTopic')
        return render_template('gm_tools_overview.html', form=notice)
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/activity', methods=['GET', 'POST'])
@login_required
def gm_tools_activity():
    if current_user.is_authenticated:
        activity_form = Notice()
        if activity_form.validate_on_submit() and activity_form.markdown.data != '':
            activity = demjson.decode(activity_form.markdown.data)
            if activity['heroes'] and activity['guns']:
                update_period_free_info(activity['heroes'], activity['guns'])
                pullActivityConfigNtf = gmCmdPro_pb2.PullActivityConfigNtf()
                pullActivityConfigNtf.id = 1
                mqAdaptor.send(encode(proto.msg_dict[gmCmdPro_pb2.PullActivityConfigNtf],
                                      pullActivityConfigNtf.SerializeToString()), '/topic/GmTopic')
                flash('updated!')
            else:
                flash('failed to update!')
        return render_template('gm_tools_activity.html', activity_form=activity_form, active_pane='home')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/announcement', methods=['GET', 'POST'])
@login_required
def gm_tools_announcement():
    if current_user.is_authenticated:
        announcement_form = Notice()
        if announcement_form.validate_on_submit() and announcement_form.markdown.data != '':
            content = announcement_filestream_format(announcement_form.markdown.data)
            if a_updater.update(content):
                flash('updated!')
            else:
                flash('failed to update!')
        return render_template('gm_tools_announcement.html', announcement_form=announcement_form,
                               active_pane='announcement')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/check_announcement', methods=['GET', 'POST'])
@login_required
def gm_tools_check_announcement():
    if current_user.is_authenticated:
        text = a_updater.get_file()
        if text:
            return text
        else:
            return ''
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/sp_facility', methods=['GET', 'POST'])
@login_required
def gm_tools_sp_facility():
    if current_user.is_authenticated:
        sp_facility_form = Notice()
        if sp_facility_form.validate_on_submit() and sp_facility_form.markdown.data != '':
            sp_facility = demjson.decode(sp_facility_form.markdown.data)
            if sp_facility['items'] and sp_facility['defaultNoticeMsg']:
                update_emergency_brake_info(sp_facility['defaultNoticeMsg'], sp_facility['items'])
                pullActivityConfigNtf = gmCmdPro_pb2.PullActivityConfigNtf()
                pullActivityConfigNtf.id = 2
                mqAdaptor.send(encode(proto.msg_dict[gmCmdPro_pb2.PullActivityConfigNtf],
                                      pullActivityConfigNtf.SerializeToString()), '/topic/GmTopic')
                flash('updated!')
            else:
                flash('failed to update!')
        return render_template('gm_tools_sp_facility.html', sp_facility_form=sp_facility_form,
                               active_pane='sp_facility')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/check_sp_facility', methods=['GET', 'POST'])
@login_required
def gm_tools_check_sp_facility():
    if current_user.is_authenticated:
        emergency_brake_info = list(get_energency_brake_info())
        re = dict()
        re['items'] = list()
        if emergency_brake_info:
            re['defaultNoticeMsg'] = emergency_brake_info[0]['defaultNoticeMsg']
            for item in emergency_brake_info[0]['items']:
                re['items'].append(item)
        return demjson.encode(re, encoding='utf-8')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/check_activity', methods=['GET', 'POST'])
@login_required
def gm_tools_check_activity():
    if current_user.is_authenticated:
        periodfree_info = list(get_period_free_info())
        re = list()
        if periodfree_info:
            for hero in periodfree_info[0]['hero']:
                re.append(hero)
            for gun in periodfree_info[0]['gun']:
                re.append(gun)
        return demjson.encode(re, encoding='utf-8')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/check_servers', methods=['GET', 'POST'])
@login_required
def gm_tools_check_servers():
    if current_user.is_authenticated:
        try:
            load_balance_server_ids = [6]
            re = list()
            for id in load_balance_server_ids:
                server_overview_key = 'SERVER_TYPE_6_ID_' + str(id) + '_CACHED_GAME_SERVER_STAT_INFO'
                server_population_key = 'SERVER_TYPE_6_ID_' + str(id) + '_GAME_SERVER_POPULATION'
                v = redis_store.hgetall(server_overview_key)
                for k in v:
                    server_info = dict()
                    f = demjson.decode(v[k], encoding='utf-8')
                    server_info['serverId'] = k
                    server_info['ipAddress'] = f['ipAddress']
                    server_info['port'] = f['port']
                    server_info['status'] = f['serverStat']
                    population = redis_store.hget(server_population_key, k)
                    if population:
                        server_info['population'] = population
                    else:
                        server_info['population'] = 'UNKNOWN'
                    re.append(server_info)
            return demjson.encode(re, encoding='utf-8')
        except:
            abort(404)
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/systemmail', methods=['GET', 'POST'])
@login_required
def gm_tools_system_mail():
    if current_user.is_authenticated:
        system_mail_form = Notice()
        if system_mail_form.validate_on_submit() and system_mail_form.markdown.data != '':
            mails = demjson.decode(system_mail_form.markdown.data)
            for mail in mails:
                playerList = list()
                for name in mail['toWhom']:
                    for player in query_player(name):
                        playerList.append(player.uuid)
                mail_info = {
                    'template': mail['template'],
                    'content': mail['content'],
                    'params': mail['params'],
                    'createAt': datetime.datetime.utcnow(),
                    'toWhichZone': mail['toWhere'],
                    'toWhom': playerList
                }
                info_string = demjson.encode(mail_info, encoding='utf-8')
                if mail['toWhere'] == '' and playerList == '':
                    flash('no player to be send! ' + info_string)
                else:
                    add_system_mail(mail_info)
                    pullSystemMailNtf = gmCmdPro_pb2.PullSystemMailNtf()
                    mqAdaptor.send(
                        encode(proto.msg_dict[gmCmdPro_pb2.PullSystemMailNtf], pullSystemMailNtf.SerializeToString()),
                        '/topic/GmTopic')
                    flash('yeah! send a system mail: ' + info_string)
        return render_template('gm_tools_system_mail.html', system_mail_form=system_mail_form,
                               system_mail_list=None, active_pane='home')

    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/check_system_mail', methods=['GET', 'POST'])
@login_required
def check_system_mail():
    if current_user.is_authenticated:
        mail_list = list()
        for mail in list(check_system_mail_from_mongo()):
            info = dict()
            info['_id'] = str(mail['_id'])
            info['createAt'] = mail['createAt']
            info['toWhichZone'] = mail['toWhichZone']
            info['toWhom'] = mail['toWhom']
            info['content'] = demjson.encode(mail['content'], encoding='utf-8')
            mail_list.append(info)
        return demjson.encode(mail_list, encoding='utf-8')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/system_mail_delete', methods=['GET', 'POST'])
@login_required
def delete_system_mail():
    if current_user.is_authenticated:
        mailId = request.form['mailId']
        if mailId and delete_system_mail_from_mongo(mailId):
            return 'success delete mail ' + mailId
        else:
            return 'failed to delete mail ' + mailId
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/controls', defaults={'page': 1}, methods=['GET', 'POST'])
@bluePrint.route('/gm/gmtools/controls/page/<int:page>')
@login_required
def gm_tools_controls(page):
    if current_user.is_authenticated:
        search_form = SearchForm()
        player_list = list()
        if search_form.validate_on_submit():
            if search_form.searchInfo.data == 'none':
                flash('search:please enter search info')
            else:
                player_list = query_player(search_form.searchInfo.data)
        pagination = Pagination(page=page, total=player_list.__len__(),
                                per_page=getattr(config['default'], 'PAGE_SIZE'),
                                bs_version='3')
        return render_template('gm_tools_controls.html', pagination=pagination, search_form=search_form,
                               playerlist=player_list)
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/profile/<uuid>')
@login_required
def gm_tools_controls_profile(uuid):
    if current_user.is_authenticated:
        profile = dict()
        profile['redis_info'] = query_player_from_redis(uuid)
        return render_template('controls_profile.html')
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/kick/<uuid>')
@login_required
def gm_tools_controls_kick(uuid):
    if current_user.is_authenticated:
        kickPlayerNtf = gmCmdPro_pb2.KickPlayerNtf()
        kickPlayerNtf.id = uuid
        mqAdaptor.send(encode(gmCmdPro_pb2.KickPlayerNtf, kickPlayerNtf.SerializeToString()), '/topic/GmTopic')
        return redirect(url_for('.gm_tools_controls'))
    else:
        return redirect(url_for('.login'))


@bluePrint.route('/gm/gmtools/manage', methods=['GET', 'POST'], defaults={'page': 1})
@bluePrint.route('/gm/gmtools/manage/page/<int:page>')
@login_required
def gm_tools_account_manage(page):
    if current_user.is_authenticated:
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
    else:
        return redirect(url_for('.login'))


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


@bluePrint.route('/gm/server/create_report/dau/<days>', methods=['GET', 'POST'])
@login_required
def create_dau_report(days):
    if current_user.is_authenticated:
        try:
            attr = []
            daily_create = []
            daily_login = []
            for i in reversed(range(1, int(days))):
                collect_date = datetime.datetime.now() - datetime.timedelta(days=i)
                collect_date_string = datetime.datetime.strftime(collect_date, "%Y-%m-%d")
                collection_name = 'log_date.' + collect_date_string
                attr.append(collect_date_string)
                daily_login.append(mongo_analysis.db[collection_name].find({'type': 'daily_login'}).count())
                daily_create.append(mongo_analysis.db[collection_name].find({'type': 'create_new_character'}).count())
            return demjson.encode(
                {'title': 'DAU', 'type': 'bar', 'attr': attr, 'daily_create': daily_create, 'daily_login': daily_login},
                encoding='utf-8')
        except:
            abort(404)
    else:
        redirect(url_for('.login'))


@bluePrint.route('/gm/server/create_report/dpu/<days>', methods=['GET', 'POST'])
@login_required
def create_dpu_report(days):
    if current_user.is_authenticated:
        try:
            attr = []
            dpu = []
            for i in reversed(range(1, int(days))):
                collect_date = datetime.datetime.now() - datetime.timedelta(days=i)
                collect_date_string = datetime.datetime.strftime(collect_date, "%Y-%m-%d")
                collection_name = 'log_date.' + collect_date_string
                attr.append(collect_date_string)
                paying_players = set()
                payments = list(mongo_analysis.db[collection_name].find({'type': 'payment'}))
                for info in payments:
                    if info['playerId'] not in paying_players:
                        paying_players.add(info['playerId'])
                dpu.append(paying_players.__len__())
            return demjson.encode({'title': 'DPU', 'type': 'bar', 'attr': attr, 'dpu': dpu}, encoding='utf-8')
        except:
            abort(404)
    else:
        redirect(url_for('.login'))


@bluePrint.route('/gm/server/create_report/dpur/<days>', methods=['GET', 'POST'])
@login_required
def create_dpur_report(days):
    if current_user.is_authenticated:
        try:
            attr = []
            dpur = []
            for i in reversed(range(1, int(days))):
                collect_date = datetime.datetime.now() - datetime.timedelta(days=i)
                collect_date_string = datetime.datetime.strftime(collect_date, "%Y-%m-%d")
                collection_name = 'log_date.' + collect_date_string
                attr.append(collect_date_string)
                paying_players = set()
                payments = list(mongo_analysis.db[collection_name].find({'type': 'payment'}))
                for info in payments:
                    if info['playerId'] not in paying_players:
                        paying_players.add(info['playerId'])
                dpu = paying_players.__len__()
                dau = mongo_analysis.db[collection_name].find({'type': 'daily_login'}).count()
                if dau == 0:
                    dpur.append(0)
                else:
                    dpur.append(float('%.2f' % (dpu * 100.0 / dau)))
            return demjson.encode({'title': 'DPUR', 'type': 'line', 'attr': attr, 'dpur': dpur}, encoding='utf-8')
        except:
            abort(404)
    else:
        redirect(url_for('.login'))


@bluePrint.route('/gm/server/create_report/income/<days>', methods=['GET', 'POST'])
@login_required
def create_income_report(days):
    if current_user.is_authenticated:
        try:
            attr = []
            income = []
            for i in reversed(range(1, int(days))):
                collect_date = datetime.datetime.now() - datetime.timedelta(days=i)
                collect_date_string = datetime.datetime.strftime(collect_date, "%Y-%m-%d")
                collection_name = 'log_date.' + collect_date_string
                attr.append(collect_date_string)
                payments = list(mongo_analysis.db[collection_name].find({'type': 'payment'}))
                cnt = 0
                for info in payments:
                    cnt += int(info['rmb'])
                income.append(cnt)
            return demjson.encode({'title': 'INCOME', 'type': 'line', 'attr': attr, 'income': income}, encoding='utf-8')
        except:
            abort(404)
    else:
        redirect(url_for('.login'))


@bluePrint.route('/gm/server/create_report/retention/<days>', methods=['GET', 'POST'])
@login_required
def create_retention_report(days):
    if current_user.is_authenticated:
        try:
            attr = []
            paying_retention = []
            retention = []
            for i in reversed(range(1, int(days))):
                collect_date = datetime.datetime.now() - datetime.timedelta(days=i)
                collect_date_string = datetime.datetime.strftime(collect_date, "%Y-%m-%d")
                attr.append(collect_date_string)
                if mongo_analysis.db['retention'].find_one({'end_date': collect_date_string, 'retention_type': 1}):
                    retention.append(mongo_analysis.db['retention'].find_one({'end_date': collect_date_string
                                                                                 , 'retention_type': 1})
                                     ['retention_people'].__len__())
                if mongo_analysis.db['paying_player_retention'].find_one(
                        {'end_date': collect_date_string, 'retention_type': 1}):
                    paying_retention.append(
                        mongo_analysis.db['paying_player_retention'].find_one(
                            {'end_date': collect_date_string, 'retention_type': 1})
                        ['retention_people'].__len__())
            return demjson.encode({'title': 'RETENTION', 'type': 'line', 'attr': attr, 'retention': retention,
                                   'paying_retention': paying_retention}, encoding='utf-8')
        except:
            abort(404)
    else:
        redirect(url_for('.login'))


# @bluePrint.route('/gm/test/mq', methods=['GET'])
# def test_mq():
#     return proto.msg_dict[gmCmdPro_pb2.GmOnlineNtf()]
# gmOnlineNtf = gmCmdPro_pb2.GmOnlineNtf()
# gmOnlineNtf.id = 2222
#
# data = gmOnlineNtf.SerializeToString()
# hex_id = '{0:04x}'.format(10108)
# buf = binascii.unhexlify(hex_id) + data
# mqAdaptor.send(buf, 'GameServerQueue_4001')
# return 'success'

# @bluePrint.route('/gm/test/scheduler_start', methods=['GET'])
# def scheduler_start():
#     scheduler.start()
#     # from tasks import test, celery_app
#     # result = add.delay(4, 4)
#     # result.ready()
#     return 'success'
#
#
# @bluePrint.route('/gm/test/scheduler_stop', methods=['GET'])
# def scheduler_stop():
#     scheduler.shutdown()
#     # from tasks import test, celery_app
#     # result = add.delay(4, 4)
#     # result.ready()
#     return 'success'
#
#
# @bluePrint.route('/gm/test/scheduler_add_job', methods=['GET'])
# def scheduler_add_job():
#     scheduler.add_job(id='job2', func='tasks:minus', args=(2, 1), trigger='interval', seconds=10)
#     # from tasks import test, celery_app
#     # result = add.delay(4, 4)
#     # result.ready()
#     return 'success'


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


def get_period_free_info():
    return mongo.db.cfg_periodfree.find({})


def get_energency_brake_info():
    return mongo.db.EmergencyBrake.find({})


def update_period_free_info(heroes, guns):
    mongo.db.cfg_periodfree.delete_many({})
    mongo.db.cfg_periodfree.insert_one({'hero': heroes, 'gun': guns})


def update_emergency_brake_info(msg, items):
    mongo.db.EmergencyBrake.delete_many({})
    mongo.db.EmergencyBrake.insert_one({'defaultNoticeMsg': msg, 'items': items})
    # info = list(mongo.db.cfg_periodfree.find({}))
    # if not info:
    #     return False
    # else:
    #     objectId = info[0]['_id']
    #     mongo.db.cfg_periodfree.upate_one({'_id': objectId}, {
    #         '$set': {'hero': heroes, 'gun': guns}
    #     })
    #     return True


def check_system_mail_from_mongo():
    return mongo.db.systemMail.find({})


def delete_system_mail_from_mongo(objId):
    if mongo.db.systemMail.find({'_id': ObjectId(objId)}):
        mongo.db.systemMail.delete_one({'_id': ObjectId(objId)})
        return True
    else:
        return False


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


def announcement_filestream_format(raw):
    announcement = dict()
    announcement['BoardDesc'] = dict()
    infos = demjson.decode(raw, encoding='utf-8')
    for i in range(0, infos.__len__()):
        announcement['BoardDesc'][str(i)] = infos[i]
    return StringIO(demjson.encode(announcement, encoding='utf-8'))
