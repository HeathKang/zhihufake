#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import render_template,abort,redirect,url_for,flash,request,current_app,make_response
from flask.ext.login import login_required,current_user
from . import main
from .forms import PostForm
from ..models import Post
from .. import db


@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data)
        db.session.add(post)
        return redirect(url_for('.index'))##指向哪里的页面
    page = request.args.get('page',1,type=int)
    ##all（）换成paginate（）显示每页的数据
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination)

