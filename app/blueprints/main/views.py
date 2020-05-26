from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Permission, Post
from app.decorators import permission_required
from app.util import flash_form_errors
from . import main
from .forms import PostForm


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
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    flash_form_errors(form)
    return render_template('main/posts.html', form=form, posts=posts)


@main.route('/edit-post/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
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
