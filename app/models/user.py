import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from .role import Role, Permission
from .post import Post


class Follow(db.Model):
    __tablename__ = 'follow'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)


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
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    followed = db.relationship('Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')

    followers = db.relationship('Follow',
        foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def password(self):
        raise AttributeError('password in not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
            .filter(Follow.follower_id == self.id)

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

    def change_email(self, token) -> bool:
        """return true if email given in token have not match"""
        new_email = User.decode_token(token).get('email')
        if User.query.filter_by(email=new_email).first() or\
            self.email == new_email:
            return False
        self.email = new_email
        self.avatar_hash = self.gravatar_hash()
        db.session.add(self)
        return True
    
    def gravatar_hash(self):
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def avatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://gravatar.com/avatar'
        
        hash = self.avatar_hash or self.gravatar_hash()
        return f'{ url }/{ hash }?s={ size }&d={ default }&r={ rating }'

    def follow(self, user: object):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    
    def unfollow(self, user: object):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    
    def is_following(self, user: object) -> bool:
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user: object) -> bool:
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
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
