from flask_login import UserMixin
from gm_application import mysql_db


class User(UserMixin, dict):
    def __init__(self, userDict):
        dict.__init__(self, userDict)

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    def get_id(self):
        return str(self._id)


class PlayerInfo(mysql_db.Model):
    __tablename__ = 'user_detail'
    id = mysql_db.Column(mysql_db.BigInteger, primary_key=True)
    uuid = mysql_db.Column(mysql_db.BigInteger, unique=True)
    userDesc = mysql_db.Column(mysql_db.String(255))
    suspensionExpiredDate = mysql_db.Column(mysql_db.Date,default=None)
