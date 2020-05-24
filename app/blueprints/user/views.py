from email_validator import validate_email, EmailNotValidError
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.util import send_email, flash_form_errors
from . import user
from .forms import ChangePasswordForm, ChangeEmailForm, EditInfoForm


@user.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template('user/profile.html', user=user)


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
    email = User.decode_token(token).get('email')
    if User.query.filter_by(email=email).first():
        abort(403)
    if not email:
        flash('request expired')
    else:
        current_user.email = email
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('email has been changed')
    return redirect(url_for('main.index'))
