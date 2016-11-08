#!/usr/bin/python
# -*- coding: utf-8 -*-



from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,validators,RadioField,TextAreaField,BooleanField,SelectField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import Required,Length,Email,Regexp
from wtforms import ValidationError

from ..models import Role,User


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


class EditProfileAdminForm(Form):
    email = StringField('邮箱：', validators=[Required(), Length(1, 64), Email()])
    username = StringField('姓名：', validators=[Required(), Length(1, 64),
                                              Regexp(u"^[\u4e00-\u9fa5_A-Za-z0-9]{1,14}$", 0, '用户名只能包含汉字、字母、数字和下划线')])
    confirmed = BooleanField('确认')
    role = SelectField('权限',coerce=int)
    location = StringField('居住地',validators=[Length(0, 64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('确认')


    def __init__(self,user,*args,**kwargs):
        super(EditProfileAdminForm,self).__init__(*args,**kwargs)
        self.role.choices =[(role.id,role.name)
							for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self,field):
        if field.data != self.user.email and \
				User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册.')

    def validate_username(self,field):
        if field.data != self.user.username and \
				User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已存在.')


