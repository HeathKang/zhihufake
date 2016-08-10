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
from .forms import LoginForm,RegistrationForm,ChangeEmailForm,PasswordRequestForm,ChangePasswordForm,PasswordResetForm
from flask.ext.login import login_user,login_required,logout_user,current_user


@auth.before_app_request
def before_request():
	if current_user.is_authenticated  \
		and not current_user.confirmed \
		and request.endpoint[:5] != 'auth.' \
		and request.endpoint != 'static':
	    return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
	token = current_user.generate_confirmation_token()
	send_email(current_user.email,'确认您的账户',
			   'auth/email/confirm',user=current_user,token=token)
	flash('已给您的邮箱发送了一封新的确认邮件，请查收')
	return redirect(url_for('main.index'))


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
    password_form = ChangePasswordForm()
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

    if password_form.validate_on_submit():
        if current_user.verify_password(password_form.old_password.data):
            current_user.password = password_form.password.data
            db.session.add(current_user)
            flash('您的密码已更改')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码')
    return render_template('auth/setting.html',email_form=email_form,password_form=password_form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
	if current_user.change_email(token):
		flash('你的E-mail地址已更新')
	else:
		flash('无效的请求')
	return redirect(url_for('main.index'))

@auth.route('/reset',methods=['GET','POST'])
def reset():
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			token = user.generate_reset_token()
			send_email(user.email,'重置您的密码',
					   'auth/email/reset_password',
					   user=user,token=token,
					   next=request.args.get('next'))
		flash('已向您发送重设密码的邮件，请查收')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html',form=form)

@auth.route('/reset/<token>',methods=['GET','POST'])
def password_reset(token):
	if not current_user.is_anonymous:
		return redirect(url_for('main.index'))
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None:
			return redirect(url_for('main.index'))
		if user.reset_password(token,form.password.data):
			flash('您的密码已更新.')
			return redirect(url_for('auth.login'))
		else:
			return redirect(url_for('main.index'))
	return render_template('auth/reset_password.html',form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('main.index'))

