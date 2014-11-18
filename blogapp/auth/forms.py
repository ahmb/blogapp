from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
import wtforms
from wtforms.validators import Required, Length, Email
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    username = StringField('Username', validators=[Required()])
    about_me = StringField('About_Me', validators=[Length(min=0, max=140)])

    def __init__(self, original_username = None, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        user = User.query.filter_by(nickname=self.username.data).first()
        if user is not None:
            self.username.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class SearchForm(Form):
    search = StringField('search', validators=[Required()])