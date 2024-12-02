from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
from flask_login import UserMixin
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
    # 0 = true, 1 = false
    picApprove = db.Column(db.Integer)
    roleApprove = db.Column(db.Integer)
    reg_role = db.Column(db.String(32), nullable=False)
    act_role = db.Column(db.String(32), nullable=False)

    rfid = db.Column(db.String(32), unique=True)

    events = db.relationship('Event', secondary='user_events', back_populates='users')

    # events = db.relationship('Event', backref='user')
    # students = db.relationship('Attendance', backref='user')
    

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<user {self.id}: {self.username}>'

class Event(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    hostId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    eventName = db.Column(db.String(32), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    time = db.Column(db.Time, default=datetime.utcnow)

    # attendances = db.relationship('Attendance', backref='event')
     
    users = db.relationship('User', secondary='user_events', back_populates='events')
    # time = db.Column(db.DateTime, default=datetime.utcnow)
    #add one for time of class/event

    def __repr__(self):
        return f'<user {self.id}>'
 
#associate table for user_events 
class UserEvents(db.Model, UserMixin):
    __tablename__ = 'user_events'  # Explicitly define the table name

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)

class Attendance(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    eventID = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable= False, default= "absent")  # "present" or "absent"
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<attendance {self.id}>'
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))