from flask import render_template, abort, flash, redirect, url_for
from flask_login import login_required
from app import db
from app.decorators import permission_required, admin_required
from app.models import Permission, User
from . import admin
from .forms import EditAccountAdminForm


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin .route('/edit-user/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditAccountAdminForm(user)

    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('profile has been updated')
        return redirect(url_for('user.profile', username=user.username))
    
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me

    return render_template('admin/edit-user-account.html', form=form, user=user)