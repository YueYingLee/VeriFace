### IF THIS FILE IS MODIFIED, RUN tables.py TO RECREATE TABLES
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    rfid_tag = db.Column(db.String (30), nullable = False, unique = True)
    events = db.relationship('Event', backref='user')
    students = db.relationship('Attendance', backref='user')

    def __repr__(self):
        return f'<user {self.id}: {self.username}>'

class Event(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    #hostId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    eventName = db.Column(db.String(32), nullable=False)
    #date = db.Column(db.Date, default=datetime.utcnow)
    time = db.Column(db.Time, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='event')
    # time = db.Column(db.DateTime, default=datetime.utcnow)
    #add one for time of class/event

    def __repr__(self):
        return f'<user {self.id}>'
    
class Attendance(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    eventID = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #status = db.Column(db.String(50), nullable=False)  # "present" or "absent"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<attendance {self.id}>'
    
