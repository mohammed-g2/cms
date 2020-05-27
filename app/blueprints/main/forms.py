from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Post


class PostForm(FlaskForm):
    body = TextAreaField('what\'s in your mind?', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired(), Length(min=3, max=64)])
    submit = SubmitField('post')

    def __init__(self, post=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post = post

    def validate_title(self, filed):
        if self.post is not None and filed.data != self.post.title:
            if Post.query.filter_by(title=filed.data).first():
                raise ValidationError('title already used')


class CommentForm(FlaskForm):
    body = TextAreaField('write a comment', validators=[DataRequired()])
    submit = SubmitField('comment')
