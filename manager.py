#!/usr/bin/env python
import os

from flask_script import Manager, Shell
from gm_tools_application import create_app

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

from route import *

manager = Manager(app)


def make_shell_context():
    return dict(app=app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.option('-u', '--userName', dest='userName', default=app.config['DEFAULT_USER'])
@manager.option('-p', '--password', dest='password', default=app.config['DEFAULT_PWD'])
@manager.option('-a', '--authority', dest='authority', default=app.config['DEFAULT_AUTH'])
def create_user(userName, password, authority):
    mongo.db.users.remove({"userName": userName})
    mongo.db.users.insert({'userName': userName, 'password': generate_password_hash(password), 'authority': authority})


if __name__ == '__main__':
    manager.run()
