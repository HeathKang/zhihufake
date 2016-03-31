#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField,SubmitField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required,Length,Email,Regexp


class PostForm(Form):
    body = PageDownField('问题：',validators=[Required()])
    submit = SubmitField('submit')