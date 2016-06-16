#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,validators,RadioField,TextAreaField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required,Length,Email,Regexp


class PostForm(Form):
    body = PageDownField('问题：',validators=[Required()])
    submit = SubmitField('发布')

class AnswerForm(Form):
    body = PageDownField('',validators=[Required()])
    submit = SubmitField('提交')

class EditProfileForm(Form):
    location = StringField('居住地',validators=[Length(0,64)])
    gender = RadioField('性别',choices=[('1','男'),('0','女')])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('确认修改')
