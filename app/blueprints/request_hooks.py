from flask import request, redirect, url_for, current_app
from flask_sqlalchemy import get_debug_queries
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


@main.after_app_request
def after_request(response):
    """log slow database queries during request"""
    for query in get_debug_queries():
        if query.duration >= current_app.config['SHOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                f'Slow query: { query.statement }\n'
                f'Parameters: { query.parameters }\n'
                f'Duration: { query.duration }\n'
                f'Context: { query.context }\n')
    
    return response
