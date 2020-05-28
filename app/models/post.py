from datetime import datetime
from flask import url_for
from app import db
from app.exceptions import ValidationError


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    title = db.Column(db.String(64), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def to_json(self) -> dict:
        post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'title': self.title,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id, _external=True),
            'comments_url': url_for('api.get_post_comments', id=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return post

    @staticmethod
    def from_json(json_post: dict) -> object:
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have body')
        return Post(body=body)
    
    def __repr__(self):
        return f'<Post { self.id }>'