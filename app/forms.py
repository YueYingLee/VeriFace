from flask_wtf import FlaskForm
from flask import render_template
from wtforms import StringField, PasswordField, SubmitField, FileField, validators
from wtforms.validators import DataRequired, EqualTo
from wtforms.fields import DateField, TimeField, SelectField
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "guest_1"})
    email = StringField('Email', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "guest@sjsue.com"})
    password = PasswordField('Password', validators=[DataRequired(), validators.Length(max=32)])
    submit = SubmitField('Sign In')
    register = SubmitField('Register')

class LogoutForm(FlaskForm):
    submit = SubmitField("Logout")

class HomeForm(FlaskForm):
    # maybe edit profile?
    edit = SubmitField('Edit')

class RegisterForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "first_name"})
    lname = StringField('Last Name', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "last_name"})
    username = StringField('Username', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "guest_1"})
    email = StringField('Email', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "guest@sjsu.com"})
    #reg_role  = StringField('Role', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "guest"})
    reg_role = SelectField(
        'Role',
        validators=[DataRequired()],
        choices=[
            ('admin', 'Admin'),
            ('staff', 'Staff'),
            ('professor', 'Professor'),
            ('student', 'Student'),
            ('guest', 'Guest')
        ]
    )
    #check if new password and confirm password are equal to each other
    password = PasswordField('New Password', [DataRequired(), EqualTo('confirm', message='Passwords must match'), validators.Length(max=32)])
    file = FileField('Choose File')
    confirm  = PasswordField('Confirm Password', [DataRequired(), EqualTo('password', message='Passwords must match'), validators.Length(max=32)])
    # add image upload later
    submit = SubmitField('Submit')
    sign = SubmitField('Sign In')

class AdminForm(FlaskForm):
    #for editing roles
    edit = SubmitField('Edit')

class AddEventsForm(FlaskForm):
    eventName = StringField('Event Name', validators=[DataRequired(), validators.Length(max=32)], render_kw={"placeholder": "Event A"})
    date = DateField('Date', format='%Y-%m-%d', default=datetime.now() )
    time = TimeField('Time', format='%H:%M', default=datetime.now())
    submit = SubmitField('Submit')

class ViewEventsForm(FlaskForm):
    edit = SubmitField('Edit')

class AttendanceForm(FlaskForm):
    start = SubmitField('Start') #start scanning -> facial
    stop = SubmitField('Stop')