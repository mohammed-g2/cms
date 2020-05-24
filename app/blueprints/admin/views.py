from flask import render_template
from flask_login import login_required
from app.decorators import permission_required, admin_required
from app.models import Permission
from . import admin


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    return render_template('admin/dashboard.html')


@admin.route('/mod')
@login_required
@permission_required(Permission.MODERATE)
def mod_page():
    return render_template('admin/mod.html')