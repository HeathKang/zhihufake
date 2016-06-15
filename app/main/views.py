#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import render_template,abort,redirect,url_for,flash,request,current_app,make_response,jsonify
from flask.ext.login import login_required,current_user
from . import main
from .forms import PostForm,AnswerForm
from ..models import Post,User,Answer,Permission,Role
from .. import db
from ..decorators import admin_required,permission_required


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
    #form = AnswerForm()
    '''
    form2 = PostForm()
    if form2.validate_on_submit():
        post = Post(body=form2.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))  ##指向哪里的页面
    '''
    '''
    if form.validate_on_submit():
        answer = Answer(body=form.body.data,
                        post=post,
                        author=current_user._get_current_object())
        db.session.add(answer)
        db.session.commit()
        flash('您的答案已成功发布！')
        return redirect(url_for('.post',id=post.id,page=-1))#return to the post and last(-1) answer'''
    form = request.form.get("content")
    if form:
        answer = Answer(body=form,
                        post=post,
                        author=current_user._get_current_object())
        db.session.add(answer)
        db.session.commit()
        flash('您的答案已成功发布！')
        return redirect(url_for('.post', id=post.id, page=-1))  # return to the post and last(-1) answer
    page = request.args.get('page',1,type=int)
    if page == -1:
        page = (post.answers.count() - 1) / \
                current_app.config['FLASKY_ANSWERS_PER_PAGE'] + 1
    pagination = post.answers.order_by(Answer.timestamp.asc()).paginate(
            page,per_page=current_app.config['FLASKY_ANSWERS_PER_PAGE'],
            error_out=False)
    answers = pagination.items
    return render_template('post.html',post=post,form=form,
                            answers=answers,pagination=pagination)#[post] only one post,because id


@main.route('/_add_agree')
def _add_agree():
    answer = Answer.query.filter_by(id=request.args.get('answer_id')).first()
    user = current_user._get_current_object()
    if answer.is_agreed_by(user):
        answer.agree -= 1
        answer.userss.remove(user)

    else:
        answer.userss.append(user)
        answer.agree += 1
    db.session.add(answer)
    db.session.commit()
    return jsonify({'agree_count' : answer.agree})

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = Post.query.filter_by(author_id=user.id).all()
    answers = Answer.query.filter_by(author_id=user.id).all()
    return render_template('user.html',user=user,posts=posts,answers=answers)

@main.route('/_follow')
@login_required
@permission_required(Permission.FOLLOW)
def _follow():
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    return jsonify({'followers_count' : user.followers.count()})

@main.route('/_unfollow')
@login_required
@permission_required(Permission.FOLLOW)
def _unfollow():
    username=request.args.get('username')
    user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    return jsonify({'followers_count': user.followers.count()})

@main.route('/_search')
def _search():
    key = request.args.get('key')
    posts = Post.query.whoosh_search(key).all()
    users = User.query.whoosh_search(key).all()
    answers = Answer.query.whoosh_search(key).all()
    user2,post2,answer2 = [],[],[]
    url,user_urls,answers_urls = [],[],[]
    if posts or answers or users:
        user2 = [user.username for user in users ]
        post2 = [post.body for post in posts]
        answer2 = [answer.post.body for answer in answers if answer.post not in posts]
        answers_urls = [url_for('.post', id=answer1.post.id, _external=True) for answer1 in answers]
        url = [ url_for('.post', id=post1.id, _external=True) for post1 in posts]
        user_urls = [ url_for('.user',username=user1.username,_external=True) for user1 in users]
    else:
        post2 = '对不起！查不到您想要的！'
        url = 'None'
    return jsonify({'post': post2,
                    'url': url,
                    'user':user2,
                    'user_urls':user_urls,
                    'answer':answer2,
                    'answers_urls':answers_urls
                    })

@main.route('/edit_answer/<int:id>',methods=['GET','POST'])
@login_required
def edit_answer(id):
    answer= Answer.query.get_or_404(id)
    post = Post.query.get_or_404(answer.post_id)
    form = request.form.get("content")
    if form:
        answer.body = form
        db.session.add(answer)
        db.session.commit()
        flash('您的答案已更新！')
        return redirect(url_for('.post', id=post.id, page=-1))  # return to the post and last(-1) answer
    return render_template('edit_answer.html',post=post,answer=answer)#[post] only one post,because id
