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
from .forms import LoginForm,RegistrationForm,ChangeEmailForm
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

@auth.route('/setting',methods=['GET','POST'])
@login_required
def setting():
    email_form = ChangeEmailForm()
    if email_form.validate_on_submit():
        if current_user.verify_password(email_form.password.data):
            new_email = email_form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, '请确认您的新邮件地址',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('确认新邮箱地址的邮件已发往您的新邮箱')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱地址或密码错误')
    return render_template('auth/setting.html',email_form=email_form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash('你的E-mail地址已更新')
	else:
		flash('无效的请求')
	return redirect(url_for('main.index'))


@auth.route('/logout')
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('main.index'))

