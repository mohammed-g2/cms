from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from app.models import Role, User


class EditAccountAdminForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Length(max=64), Email()])
    username = StringField('username', validators=[DataRequired(), Length(max=64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 
            'username must have only letters, numbers, dots or underscore')])
    confirmed = BooleanField('confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('name', validators=[Length(max=64)])
    location = StringField('location', validators=[Length(max=64)])
    about_me = TextAreaField('about me')
    submit = SubmitField('submit')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = \
            [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
            User.query.filter_by(email=field.data).first():
            raise ValidationError('email already used')
    
    def validate_username(self, field):
        if field.data != self.user.username and \
            User.query.filter_by(username=field.data).first():
            raise ValidationError('username already used')
