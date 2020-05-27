from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Permission, Post, Comment
from app.decorators import permission_required
from app.util import flash_form_errors
from . import main
from .forms import PostForm, CommentForm


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/posts', methods=['GET', 'POST'])
@login_required
def posts():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object(), 
            title=form.title.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.posts'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    flash_form_errors(form)
    return render_template('main/posts.html', form=form, posts=posts, pagination=pagination,
        endpoint='main.posts', title='Posts')


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = None

    if current_user.is_authenticated and current_user.can(Permission.COMMENT):
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(body=form.body.data, author=current_user, post=post)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('main.post', id=id))
        flash_form_errors(form)
        
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page,
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items

    return render_template('main/post.html', post=post, pagination=pagination, 
        comments=comments, endpoint='main.post', form=form)


@main.route('/delete-comment/<int:comment_id>/<int:post_id>', methods=['POST'])
@login_required
def delete_comment(comment_id, post_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.is_admin() \
        or current_user.can(Permission.MODERATE) \
        or current_user == comment.author:
        db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('main.post', id=post_id))


@main.route('/edit-post/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm(post)

    if form.validate_on_submit():
        post.body = form.body.data
        post.title = form.title.data
        db.session.add(post)
        db.session.commit()
        flash('post has been edited')
        return redirect(url_for('main.posts'))
    
    form.title.data = post.title
    form.body.data = post.body
    
    flash_form_errors(form)
    return render_template('main/edit-post.html', form=form)
