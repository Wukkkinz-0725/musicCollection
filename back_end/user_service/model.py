from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
import os

db = SQLAlchemy()

class Serializer(object):
    '''Base class for all models that adds a serialize method to output'''
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
    

class UserModel(db.Model, Serializer):
    __tablename__ = 'user'
    '''User model for the database'''
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    age = db.Column(db.Integer)
    description = db.Column(db.String(256))

    def __init__(self, email, username, password, age, description):
        self.email = email
        self.username = username
        self.password = password
        self.age = age
        self.description = description

    def serialize(self):
        d = Serializer.serialize(self)
        del d['password']
        return d

class CollectionModel(db.Model, Serializer):
    __tablename__ = 'collection'
    '''Collection model for the database'''
    colid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    sid = db.Column(db.Integer, nullable=False)
    song_name = db.Column(db.String(64), nullable=False)
    
    def __init__(self, uid, sid, song_name):
        self.uid = uid
        self.sid = sid
        self.song_name = song_name

    def serialize(self):
        d = Serializer.serialize(self)
        return d


class DBClient():
    '''Class for connecting to the database'''
    def __init__(self):
        self.user = os.environ.get("DBUSER")
        self.password = os.environ.get("DBPW")
        self.host = os.environ.get("DBHOST")
        self.port = str(os.environ.get('DBPORT'))
        self.db = os.environ.get("DBNAME")

    def get_uri(self):
        return 'mysql+pymysql://'+self.user+':'+self.password+'@'+self.host+'/'+self.db