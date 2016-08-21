#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask.ext.wtf import Form

from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱：',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('密码：',validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('邮箱：',validators=[Required(),Length(1,64),Email()])
    username = StringField('姓名：',validators=[Required(),Length(1,64),
            Regexp(u"^[\u4e00-\u9fa5_A-Za-z0-9]{1,14}$",0,'用户名只能包含汉字、字母、数字和下划线')])
    password = PasswordField('密码：',validators=[Required(),EqualTo('password2',message='两次密码输入不一致')])
    password2 = PasswordField('确认密码：',validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise  ValidationError('该用户名已被注册')


class ChangeEmailForm(Form):
    email = StringField('新邮箱地址:',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('密码:',validators=[Required()])
    submit = SubmitField('提交')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱地址已被注册')

class PasswordRequestForm(Form):
    email = StringField('邮箱地址：',validators=[Required(),Length(1,64),Email()])
    submit = SubmitField('重设密码')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码：',validators=[Required()])
    password = PasswordField('新密码：',validators=[Required(),EqualTo('password2',
               message = '确认密码不一致')])
    password2 = PasswordField('确认密码：',validators=[Required()])
    submit = SubmitField('提交')


class PasswordResetForm(Form):
    email = StringField('邮箱地址：',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('新密码：',validators=[Required(),EqualTo('password2',
               message='确认密码不一致')])
    password2 = PasswordField('确认密码：',validators=[Required()])
    submit = SubmitField('提交')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知的邮箱地址')



