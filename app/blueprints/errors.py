from flask import render_template, request, jsonify
from .main import main


@main.app_errorhandler(404)
def page_not_found(e):
    # return json format to api clients
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404


@main.app_errorhandler(505)
def internal_server_error(e):
    # return json format to api clients
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 505
        return response
    return render_template('errors/500.html'), 500


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403
