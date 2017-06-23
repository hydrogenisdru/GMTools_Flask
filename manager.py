#!/usr/bin/env python
import os

from flask_script import Manager, Shell
from application import create_app, mongo
from route import bluePrint

print '1'

config_name = os.getenv('FLASK_CONFIG') or 'production'
app = create_app(config_name)
app.register_blueprint(bluePrint)


manager = Manager(app)


def make_shell_context():
    return dict(app=app.app)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.option('-u', '--userName', dest='userName', default=app.config['DEFAULT_USER'])
@manager.option('-p', '--password', dest='password', default=app.config['DEFAULT_PWD'])
@manager.option('-a', '--authority', dest='authority', default=app.config['DEFAULT_AUTH'])
def create_user(userName, password, authority):
    mongo.db.gm_users.delete_one({"userName": userName})
    mongo.db.gm_users.insert_one(
        {'userName': userName, 'password': mongo.generate_password_hash(password), 'authority': authority})


if __name__ == '__main__':
    manager.run()
