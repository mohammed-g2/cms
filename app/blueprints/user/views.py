from flask import render_template, request, redirect, url_for, flash, abort, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Post, Permission
from app.util import send_email, flash_form_errors
from app.decorators import permission_required
from . import user
from .forms import ChangePasswordForm, ChangeEmailForm, EditInfoForm


@user.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('user/profile.html', user=user, posts=posts, pagination=pagination)


@user.route('/newsfeed')
@login_required
def newsfeed():
    # uses template from main blueprint
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('main/posts.html', posts=posts, pagination=pagination, 
        title='Newsfeed', endpoint='user.newsfeed')


@user.route('/edit-account', methods=['GET', 'POST'])
@login_required
def edit_account():
    change_password_form = ChangePasswordForm()
    
    change_email_form = ChangeEmailForm()
    change_email_form.email.data = current_user.email
    
    edit_info_form = EditInfoForm()
    edit_info_form.name.data = current_user.name
    edit_info_form.location.data = current_user.location
    edit_info_form.about_me.data = current_user.about_me
    
    return render_template('user/edit-account.html', 
        change_password_form=change_password_form, change_email_form=change_email_form,
        edit_info_form=edit_info_form)


@user.route('/edit-account-info', methods=['POST'])
@login_required
def edit_account_info():
    form = EditInfoForm(request.form)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data

        db.session.add(current_user._get_current_object())
        db.session.commit()
    flash('your profile has been updated')
    flash_form_errors(form)
    return redirect(url_for('user.profile', username=current_user.username))


@user.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('password has been changed')
    
    flash_form_errors(form)
    return redirect(url_for('user.edit_account'))
    

@user.route('/change-email', methods=['POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm(request.form)
    if form.validate_on_submit():
        token = current_user.generate_token(email=form.email.data)
        send_email([current_user.email],
        'change email address',
        'user/email/change-email',
        token=token, user=user)
        flash('a message has been sent to your email to confirm the changes')
    flash_form_errors(form)
    return redirect(url_for('user.edit_account'))


@user.route('/change-email/<token>')
@login_required
def change_email(token):
    user_id = User.decode_token(token).get('user_id')
    user = User.query.get_or_404(user_id)
    if user.change_email(token):
        db.session.commit()
        flash('email has been changed')
    return redirect(url_for('main.index'))


@user.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    current_user.follow(user)
    db.session.commit()
    flash(f'you are now following { username }')
    return redirect(url_for('user.profile', username=username))


@user.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    current_user.unfollow(user)
    db.session.commit()
    flash(f'you unfollowed { username }')
    return redirect(url_for('user.profile', username=username))


@user.route('/followers/<username>')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'since': item.timestamp} for item in pagination.items]
    return render_template('user/follows.html', user=user, pagination=pagination, 
        follows=follows, endpoint='user.followers', title='followers')


@user.route('/following/<username>')
@login_required
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.followed, 'since': item.timestamp} for item in pagination.items]
    return render_template('user/follows.html', user=user, pagination=pagination, 
        follows=follows, endpoint='user.followed_by', title='following')
