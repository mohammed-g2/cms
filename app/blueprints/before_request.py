from flask import request, redirect, url_for
from flask_login import current_user
from .main import main

@main.before_app_request
def before_request():
    """
        redirect logged-in unconfirmed users to unconfirmed page and
        update user last_seen
    """
    if current_user.is_authenticated:
        current_user.ping()
        if request.blueprint != 'auth' \
            and request.endpoint != 'static'\
            and not current_user.confirmed:
            return redirect(url_for('auth.unconfirmed'))
