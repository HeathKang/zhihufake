#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required,Length,Email,Regexp


class PostForm(Form):
    body = PageDownField('问题：',validators=[Required()])
    submit = SubmitField('提交')

class AnswerForm(Form):
    body = PageDownField('',validators=[Required()])
    submit = SubmitField('提交')