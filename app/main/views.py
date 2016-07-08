#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')  #fix unicode problem


from flask import render_template,abort,redirect,url_for,flash,request,current_app,make_response,jsonify,get_template_attribute
from flask.ext.login import login_required,current_user
from . import main
from .forms import PostForm,AnswerForm,EditProfileForm,EditProfileAdminForm
from ..models import Post,User,Answer,Permission,Role,Comment
from .. import db,moment
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

@main.route('/_load_questions', methods=['POST'])
def _load_questions():
    """加载问题HTML"""
    page = request.args.get('page', type=int, default=1)
    query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
    )
    macro = get_template_attribute("_add_questions.html", "render_posts")
    posts = pagination.items
    return jsonify({'result': True,
                    'html': macro(posts),
                    'posts':[post.timestamp for post in posts],
                    'post_id':[post.id for post in posts]
                    })

@main.route('/_comment', methods=['GET','POST'])
def _comment():
    """加载评论HTML"""

    id = request.args.get('answer_id')
    answer = Answer.query.get_or_404(id)
    page = request.args.get('page', type=int, default=1)
    comment =request.args.get('comment')
    if current_user.can(Permission.COMMENT) and comment is not None:
        comment = Comment(body=comment,
                          author=current_user._get_current_object(),
                          answer_id=id)
        db.session.add(comment)
        db.session.commit()
        page = -1
    if page == -1:
        page = answer.comments.count() / 2
    pagination = Comment.query.order_by(Comment.timestamp).filter_by(answer_id=id).paginate(
        page,per_page=2,error_out=False
    )
    macro_comment = get_template_attribute("_comments.html", "render_comments")
    macro_page = get_template_attribute("_page.html", "render_page")
    comments = pagination.items
    return jsonify({'result': True,
                    'comment_html': macro_comment(comments),
                    'page_html':macro_page(pagination),
                    'comments_timestamp':[comment.timestamp for comment in comments],
                    'comments_id':[comment.id for comment in comments]
                    })

@main.route('/_add_comment', methods=['GET','POST'])
def _add_comment():
    """添加评论HTML"""

    id = request.args.get('answer_id')
    answer = Answer.query.get_or_404(id)
    comment =request.args.get('comment')
    answers = Answer.query.get_or_404(id)
    page = 1
    result= False
    if current_user.can(Permission.COMMENT):
        comment = Comment(body=comment,
                          author=current_user._get_current_object(),
                          answer_id=id)
        db.session.add(comment)
        db.session.commit()
        page = (answer.comments.count()-1)/2 + 1
        result=True
    pagination = Comment.query.order_by(Comment.timestamp).filter_by(answer_id=id).paginate(
        page,per_page=2,error_out=False
    )
    macro_comment = get_template_attribute("_comments.html", "render_comments")
    macro_page = get_template_attribute("_page.html", "render_page")
    comments = pagination.items
    return jsonify({'result': result,
                    'comment_html': macro_comment(comments),
                    'page_html': macro_page(pagination),
                    'comments_timestamp': [comment.timestamp for comment in comments],
                    'comments_id': [comment.id for comment in comments]
                    })


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
        post.usersss.append(current_user)
        db.session.add(answer)
        db.session.add(post)
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
                            answers=answers,pagination=pagination,page=page)#[post] only one post,because id


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
    posts = Post.query.order_by(Post.timestamp.desc()).filter_by(author_id=user.id).all()
    answers = Answer.query.order_by(Answer.timestamp.desc()).filter_by(author_id=user.id).all()
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

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在该用户')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False
    )
    followers =[item.follower for item in pagination.items ]
    return render_template('followers.html',user=user,pagination=pagination,followers=followers)

@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('不存在该用户')
        return redirect(url_for('.index'))
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(
        page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False
    )
    followers =[item.followed for item in pagination.items ]
    return render_template('followed.html',user=user,pagination=pagination,followers=followers)

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

@main.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.location = form.location.data
        current_user.gender = form.gender.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('您的资料已更新')
        return redirect(url_for('.user',username=current_user.username))
    form.location.data = current_user.location
    form.gender.data = current_user.gender
    return render_template('edit_profile.html',form=form)

@main.route('/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def disable(id):
    answer = Answer.query.get_or_404(id)
    answer.disabled = True
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('.post',id=answer.post_id,page=request.args.get('page',1,type=int)))

@main.route('/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def enable(id):
    answer = Answer.query.get_or_404(id)
    answer.disabled = False
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('.post',id=answer.post_id,page=request.args.get('page',1,type=int)))

@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.location = form.location.data
        user.about_me =form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('该用户资料已完成修改.')
        return redirect(url_for('.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form,user=user)
