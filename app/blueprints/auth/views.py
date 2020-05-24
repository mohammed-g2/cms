from flask import render_template, request, redirect, flash, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import db
from app.models import User
from app.util import flash_form_errors, send_email
from . import auth
from .forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.is_submitted():
        if form.validate():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, form.remember_me.data)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)
        flash('invalid email or password')
    return render_template('auth/login.html', form=form)


@auth.route('logout')
@login_required
def logout():
    logout_user()
    flash('you have logged out')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, 
            username=form.username.data, 
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        # send confirmation email after the user is registered in the
        # database
        token = user.generate_token()
        send_email([user.email], 
            'Confirm your account', 
            'auth/email/confirm',
            user=user, token=token)
        flash('account created, you can login now')
        return redirect(url_for('auth.login'))
    flash_form_errors(form)
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('you have confirmed your account')
    else:
        flash('confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_email([current_user.email], 
        'Confirm your account', 
        'auth/email/confirm',
        user=current_user, token=token)
    flash('new confirmation email has been sent to you')
    return redirect(url_for('main.index'))
    

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_token()
            send_email([user.email], 
                'Reset password', 
                'auth/email/reset-password', 
                user=user, token=token)
        flash('a message has been sent to your email to reset your password')
        return redirect(url_for('auth.login'))
    flash_form_errors(form)
    return render_template('auth/reset-password-request.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_id = User.decode_token(token).get('user_id')
        user = User.query.get(user_id)
        user.password = form.new_password.data
        db.session.add(user)
        db.session.commit()
        flash('you can login now')
        return redirect(url_for('auth.login'))
    flash_form_errors(form)
    return render_template('auth/reset-password.html', form=form)

