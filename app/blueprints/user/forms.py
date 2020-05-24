from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class ChangeEmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField('change')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('please use another email')


class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        label='new password', 
        validators=[
            DataRequired(), 
            Length(min=6, message='password must be at least 6 characters long'),
            EqualTo('repeat_password', message='unmatched password')
        ])
    repeat_password = PasswordField('repeat password', validators=[DataRequired()])
    submit = SubmitField('change')


class EditInfoForm(FlaskForm):
    name = StringField('name', validators=[Length(max=64, message='name cannot be longer than 64 caracters')])
    location = StringField('location', validators=[Length(max=64, message='location cannot be longer than 64 caracters')])
    about_me = TextAreaField('about me')
    submit = SubmitField('submit')
