#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import render_template,abort,redirect,url_for,flash,request,current_app,make_response
from flask.ext.login import login_required,current_user
from . import main
from .forms import PostForm,AnswerForm
from ..models import Post,User,Answer,Permission,Role
from .. import db


@main.route('/',methods=['GET','POST'])
def index():
    '''form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))##指向哪里的页面'''
    page = request.args.get('page',1,type=int)
    ##all（）换成paginate（）显示每页的数据
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    posts = pagination.items
    return render_template('index.html',posts=posts,pagination=pagination)


@main.route('/_question',methods=['POST'])
def _question():
    form = request.form.get("postform")
    if current_user.can(Permission.WRITE_ARTICLES):
        post = Post(body=form,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))##指向哪里的页面

@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = AnswerForm()
    '''
    form2 = PostForm()
    if form2.validate_on_submit():
        post = Post(body=form2.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))  ##指向哪里的页面
        '''
    if form.validate_on_submit():
        answer = Answer(body=form.body.data,
                        post=post,
                        author=current_user._get_current_object())
        db.session.add(answer)
        db.session.commit()
        flash('您的答案已成功发布！')
        return redirect(url_for('.post',id=post.id,page=-1))#return to the post and last(-1) answer
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.answers.count() - 1) / \
                current_app.config['FLASKY_ANSWERS_PER_PAGE'] + 1
    pagination = post.answers.order_by(Answer.timestamp.asc()).paginate(
            page,per_page=current_app.config['FLASKY_ANSWERS_PER_PAGE'],
            error_out=False)
    answers = pagination.items
    return render_template('post.html',posts=[post],form=form,
                            answers=answers,pagination=pagination)

