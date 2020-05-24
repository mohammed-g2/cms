from email_validator import validate_email, EmailNotValidError
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from app import db
from app.models import User
from app.util import send_email
from . import user
from .forms import ChangePasswordForm, ChangeEmailForm


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
    return render_template('user/edit-account.html', 
        change_password_form=change_password_form, change_email_form=change_email_form)


@user.route('/change-password', methods=['POST'])
@login_required
def change_password():
    password = request.form.get('password')
    repeat_password = request.form.get('repeat_passsword')
    if password and len(password) >= 6:
        if password == repeat_password:
            current_user.password = password
            db.session.add(current_user)
            db.session.commit()
            flash('password has been changed')
        else:
            flash('unmatched password')
    else:
        flash('password can not be less than 6 characters long')
    return redirect(url_for('user.edit_account'))
    

@user.route('/change-email', methods=['POST'])
@login_required
def change_email_request():
    try:
        email = validate_email(request.form.get('email')).email
    except EmailNotValidError:
        flash('invalid email')
        return redirect(url_for('user.edit_account'))
    
    if User.query.filter_by(email=email).first() == None:
        token = current_user.generate_token(email=email)
        send_email([current_user.email],
        'change email address',
        'user/email/change-email',
        token=token, user=user)
        flash('a message has been sent to your email to confirm the changes')
    else:
        flash('please use another email')
    return redirect(url_for('user.edit_account'))


@user.route('/change-email/<token>')
@login_required
def change_email(token):
    email = User.decode_token(token).get('email')
    if not email:
        flash('request expired')
    else:
        current_user.email = email
        db.session.add(current_user)
        db.session.commit()
        flash('email has been changed')
    return redirect(url_for('main.index'))
