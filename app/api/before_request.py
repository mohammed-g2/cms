from flask import g
from . import api
from .authentication import auth
from .errors import forbidden


@api.before_request
@auth.login_required
def before_request():
    """check if current user is confirmed"""
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('unconfirmed account')