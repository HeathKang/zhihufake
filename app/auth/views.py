#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import render_template,redirect,url_for,request,flash
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm,RegistrationForm
from flask.ext.login import login_user,login_required,logout_user,current_user


@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        email_title =  user.username
        send_email(user.email,email_title,
                   'auth/email/confirm',user=user,token=token)
        flash('帐号确认邮件已发往您的邮箱！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)


@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名或密码')
    return render_template('auth/login.html',form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('您已经确认了你的帐号。谢谢！')
    else:
        flash('确认链接不可用或已经过期！')
    return redirect(url_for('main.index'))


@auth.route('/logout')
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('main.index'))

