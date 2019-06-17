from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username= StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username has been taken already.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email has already been registered.')

class ProductForm(FlaskForm):
    name = StringField('Name of Product', validators=[DataRequired()])
    price = DecimalField('Price', places=3, validators=
                        [DataRequired(), NumberRange(min=0.00, max=None)])
    stock = IntegerField('Stock Left',
                         validators=[DataRequired(), NumberRange(min=0, max=None)])
    submit = SubmitField('Submit')

class ReviewForm(FlaskForm):
    ratings = StringField('Rating (out of 5)', validators=[DataRequired()])
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit')
