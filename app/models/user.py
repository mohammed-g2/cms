from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from .role import Role, Permission


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password in not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self, expiration=3600, **kwargs) -> str:
        """generate a serialized token, all added arguments will be appended to the token"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        data = {'user_id': self.id}
        if kwargs:
            for key, val in kwargs.items():
                data[key] = val
        return s.dumps(data).decode('utf-8')

    @staticmethod
    def decode_token(token) -> dict:
        """
            check if the token is valid and return dict that contain the user id plus any 
            values stored in the token, else return None
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        # decode the token
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return
        return data

    def confirm(self, token) -> bool:
        """if token is valid return true and set user confirmed, else return false"""
        user_id = self.decode_token(token).get('user_id')
        if user_id != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, permission) -> bool:
        """check if user has permission"""
        return self.role is not None and self.role.has_permission(permission)

    def is_admin(self) -> bool:
        return self.can(Permission.ADMIN)

    def ping(self):
        """update user last_seen"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False
    
    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)