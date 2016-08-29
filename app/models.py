#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import hashlib
from flask import request,current_app
from flask.ext.login import UserMixin,AnonymousUserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
import flask_whooshalchemyplus
from jieba.analyse import ChineseAnalyzer
from flask_sqlalchemy import Pagination

from . import db,login_manager


agrees = db.Table('agrees',
                  db.Column('users_id',db.Integer,db.ForeignKey('users.id')),
                  db.Column('answers_id',db.Integer,db.ForeignKey('answers.id')))
answerd = db.Table('answerd',
                   db.Column('users_id',db.Integer,db.ForeignKey('users.id')),
                   db.Column('posts_id',db.Integer,db.ForeignKey('posts.id')))


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS =0x08
    ADMINISTER = 0x80


class Follow(db.Model):
    _tablename_ = 'follows'
    follower_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer,db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)


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
    __searchable__ = ['body']
    __analyzer__ = ChineseAnalyzer()
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    answers = db.relationship('Answer',backref='post',lazy='dynamic')

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em',
                        'i','li','ol','pre','strong','ul','h1','h2','h3','p','u']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                       tags=allowed_tags,strip=True))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()
    def is_answerd_by(self,user):
        return self.usersss.filter_by(id=user.id).first() is not None


db.event.listen(Post.body,'set',Post.on_changed_body)


class Answer(db.Model):
    __searchable__ = ['body']
    __analyzer__ = ChineseAnalyzer()
    __tablename__ = 'answers'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    pure_body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer,db.ForeignKey('posts.id'))
    agree = db.Column(db.Integer,default=0)
    disagree = db.Column(db.Integer,default=0)
    comments = db.relationship('Comment',backref='answer',lazy='dynamic')

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a','abbr','acronym','b','blockquote','code','em',
                        'i','li','ol','pre','strong','ul','h1','h2','h3','p','u','span']
        target.body_html = bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                        tags=allowed_tags,strip=True))
        pure_allowed_tags = []
        target.pure_body = bleach.linkify(bleach.clean(markdown(value,output_format='html'),
                                                        tags=pure_allowed_tags,strip=True))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        post_count = Post.query.count()
        user_count = User.query.count()
        for i in range(count):
            p = Post.query.offset(randint(0, post_count - 1)).first()
            u = User.query.offset(randint(0, user_count - 1)).first()
            a = Answer(body=forgery_py.lorem_ipsum.sentences(randint(1, 10)),
                     timestamp=forgery_py.date.date(True),
                     agree = randint(1,100),
                     post=p,
                     author=u)
            db.session.add(a)
            db.session.commit()

    def is_agreed_by(self,user):
        return self.userss.filter_by(id=user.id).first() is not None


db.event.listen(Answer.body,'set',Answer.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    answer_id = db.Column(db.Integer,db.ForeignKey('answers.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        answer_count = Answer.query.count()
        user_count = User.query.count()
        for i in range(count):
            a = Answer.query.offset(randint(0, answer_count - 1)).first()
            u = User.query.offset(randint(0, user_count - 1)).first()
            c = Comment(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     answer=a,
                     author=u)
            db.session.add(c)
            db.session.commit()


class User(UserMixin,db.Model):
    __searchable__ = ['username']
    __analyzer__ = ChineseAnalyzer()
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean,default=False)
    posts = db.relationship('Post',backref='author',lazy='dynamic')
    answers = db.relationship('Answer',backref='author',lazy='dynamic')
    angrees = db.Column(db.Integer,default=0)                #users sum of agrees
    comments = db.relationship('Comment',backref='author',lazy='dynamic')
    avatar_hash = db.Column(db.String(32))
    location = db.Column(db.String(64))
    gender = db.Column(db.Boolean,default=True)
    about_me = db.Column(db.Text())
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower',lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all,delete-orphan')
    agrees = db.relationship('Answer',
                             secondary=agrees,
                             backref=db.backref('userss',lazy='dynamic'),
                             lazy='dynamic')
    answerd = db.relationship('Post',
                              secondary=answerd,
                              backref=db.backref('usersss',lazy='dynamic'),
                              lazy='dynamic')

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()#give admin role
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first() #give default role
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed,randint
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     angrees=randint(100,200),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence())
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    @property
    def password(self):
        raise AttributeError('密码值不可读！')

    @property
    def followed_posts(self):
        posts = Post.query.\
            join(Follow,Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)
        return posts

    @property
    def followed_answers(self):
        answers = Answer.query.\
            join(Follow, Follow.followed_id == Answer.author_id).filter(Follow.follower_id == self.id)
        return answers

    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})

    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

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

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self,user):
        if not self.is_following(user):
            f = Follow(follower=self,followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self,user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,hash=hash,size=size,default=default,rating=rating
        )

    @property
    def followed_answers(self):
        return Answer.query.join(Follow,Follow.followed_id == Answer.author_id).filter(Follow.follower_id==self.id)


class AnonymousUser(AnonymousUserMixin):

    def can(self,permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def paginate1(query, page, per_page=20, error_out=True):
    if error_out and page < 1:
        abort(404)
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    if not items and page != 1 and error_out:
        abort(404)
    # No need to count if we're on the first page and there are fewer
    # items than we expected.
    if page == 1 and len(items) < per_page:
        total = len(items)
    else:
        total = query.order_by(None).count()
    return Pagination(query, page, per_page, total, items)






