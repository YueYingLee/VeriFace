### IF THIS FILE IS MODIFIED, RUN tables.py TO RECREATE TABLES
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True) #maybe check if it ends with @sjsu.edu
    username = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    fname = db.Column(db.String(150))
    lname = db.Column(db.String(150))
    file = db.Column(db.String(50), nullable = False)
    data = db.Column(db.LargeBinary, nullable = False)
    # profile_picture = db.Column(db.LargeBinary)
    # add one to see if profile picture uploaded is the same as the face of the person being scanned
    # add to check for image upload approvable on admin view
    picApprove = db.Column(db.Integer)
    roleApprove = db.Column(db.Integer)
    reg_role = db.Column(db.String(32), nullable=False)
    act_role = db.Column(db.String(32), nullable=False)


    rfid = db.Column(db.String(32), nullable=False, unique=True)
    events = db.relationship('Event', secondary='user_events', back_populates='users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<user {self.id}: {self.username}>'

class Event(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    hostId = db.Column(db.Integer, nullable = False)
    eventName = db.Column(db.String(32), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    time = db.Column(db.Time, default=datetime.utcnow)
    # time = db.Column(db.DateTime, default=datetime.utcnow)
    #add one for time of class/event

    users = db.relationship('User', secondary='user_events', back_populates='events')

    def __repr__(self):
        return f'<user {self.id}>'
    
user_events = db.Table(
    'user_events',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    