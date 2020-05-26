from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Permission, Post
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
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.posts'))
    posts = Post.query.order_gy(Post.timestamp.desc()).all()
    return render_template('main/posts.html', form=form, posts=posts)


