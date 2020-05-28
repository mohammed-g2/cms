from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from app.models import User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
        return true if credentials are valid (email or token), else false
        if token used set g.token_used = true, else set to false,
        store user in g.current_user

        returning false while result in an error, handled by auth_error
        
    """
    if email_or_token == '':
        return False
    if password == '':
        user_id = User.decode_token(email_or_token).get('user_id')
        if user_id is None:
            return False
        g.current_user = User.query.get(user_id)
        g.token_used = True
        return g.current_user is not None
    
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    
    g.current_user = user
    g.token_used = False
    return user.check_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('invalid credentials')


@api.route('/token', methods=['POST'])
def get_token():
    """return token if g.token_used is set to true"""
    if g.token_used:
        return unauthorized('invalid credentials')
    return jsonify({
        'token': g.current_user.generate_token(experation=3600),
        'expiration': 3600})