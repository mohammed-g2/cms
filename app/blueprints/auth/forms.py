from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from wtforms import ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(max=64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('login')


class RegisterForm(FlaskForm):
    username = StringField(
        label='username', 
        validators=[
            DataRequired(), 
            Length(3, 64, message='username must be between 3 and 64 characters'), 
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
                'Usernames must have only letters, numbers, dots or underscores')
        ])
    email = StringField(
        label='email', 
        validators=[
            DataRequired(), 
            Email(), 
            Length(max=64, message='email can\'t have more than 64 characters')
        ])
    password = PasswordField(
        label='password', 
        validators=[
            DataRequired(), 
            Length(min=6, message='password must be at least 6 characters long'), 
            EqualTo('repeat_password', message='unmatched password')
        ])
    repeat_password = PasswordField('repeat password', validators=[DataRequired()])
    submit = SubmitField('sign up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('please use another email')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('please use another username')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField(
        label='new password', 
        validators=[
            DataRequired(), 
            Length(min=6, message='password must be at least 6 characters long'),
            EqualTo('repeat_password', message='unmatched password')
        ])
    repeat_password = PasswordField('repeat password', validators=[DataRequired()])
    submit = SubmitField('change')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField('reset')


class ChangeEmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField('change')
