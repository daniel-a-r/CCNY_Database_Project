from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(max=32)])
    confirm_password = PasswordField('Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AlbumSearchForm(FlaskForm):
    album_name = StringField('Album Name', validators=[DataRequired()])
    submit = SubmitField('Search')
    

class UpdateNameForm(FlaskForm):
    update_name = StringField('New Name', validators=[DataRequired()])
    submit = SubmitField('Update Name')


class UpdateEmailForm(FlaskForm):
    update_email = StringField('New Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Email')


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(max=32)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')
    