from flask import render_template, abort, flash, redirect, url_for, request, current_app
from flask_login import login_required
from sqlalchemy.sql import func
from app import db
from app.decorators import permission_required, admin_required
from app.models import Permission, User, Comment
from app.util import flash_form_errors
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
        user.role_id = form.role.data
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
    form.role.data = user.role_id
    flash_form_errors(form)
    return render_template('admin/edit-user-account.html', form=form, user=user)


@admin.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    func.left()
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page=page, 
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('admin/moderate-comments.html', pagination=pagination, 
        comments=comments, endpoint='admin.moderate')
