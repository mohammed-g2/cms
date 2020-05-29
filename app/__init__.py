from flask import Flask, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import config


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    config_setting = config[config_name]

    # create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_setting)
    config_setting.init_app(app)

    # configure extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    # attach blueprints
    from app.blueprints import main, auth, user, admin
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(admin, url_prefix='/admin')
    # api
    from app.api import api
    app.register_blueprint(api, url_prefix='/api/v1')

    # make Permission class available for templates
    @app.context_processor
    def make_context():
        from app.models import Permission
        return dict(Permission=Permission)


    # for testing
    @app.route('/shutdown')
    def server_shutdown():
        """shutdown route for testing"""
        if not app.testing:
            abort(404)
        shutdown = request.environ.get('werkzeug.server.shutdown')
        if not shutdown:
            abort(500)
        shutdown()
        return 'shutting down...'
    
    return app
