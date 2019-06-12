from flask_wtforms import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validors=[DataRequired()])
    submit = SubmitField('Submit')
