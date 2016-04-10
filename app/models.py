#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
from flask import request,current_app
from . import db,login_manager
from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS =0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)

    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'Users':(Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES, True),
            'Moderator':(Permission.FOLLOW |
                           Permission.COMMENT |
                           Permission.WRITE_ARTICLES |
                           Permission.MODERATE_COMMENTS,False),
            'Administrator':(0xff,False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()



class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em',
                        'i','li','ol','pre','strong','ul','h1','h2','h3','p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                       tags=allowed_tags,strip=True))

db.event.listen(Post.body,'set',Post.on_changed_body)


class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean,default=False)
    posts = db.relationship('Post',backref='author',lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))






