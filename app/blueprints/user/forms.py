from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class ChangeEmailForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField('change')


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
