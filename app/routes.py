from flask import render_template, redirect, request, url_for
from flask import flash, send_file, send_from_directory
from .forms import LoginForm, LogoutForm, HomeForm, RegisterForm, AdminForm, AddEventsForm, ViewEventsForm, AttendanceForm, viewAttendanceForm, AddtoEventsForm
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Event, Attendance

import base64

from app import myapp_obj
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from io import BytesIO
from . import db
from datetime import datetime
from flask_moment import Moment
from flask import Response

import threading
import cv2
from .facial_recognition.utils import poll_rfid, display_camera, encode_image
from .facial_recognition.global_vars import end_event

from .facial_recognition.rfid_handler import poll_rfid_once
import serial

@myapp_obj.route("/", methods=['GET', 'POST'])
@myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        # flash("You are already logged in!")
        return redirect('/index')
    form = LoginForm()
    # if form inputs are valid
    if form.register.data:
       return redirect('/register') 
    # clicked on register button
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            #print saying not registered and empty sign in fields
            flash('That username is not registered!')
            flash('To register, click the Register button below.')
            return redirect('/')
        elif not user.check_password(form.password.data):
            flash('Incorrect password!')
            return redirect('/')
        elif user.email != form.email.data:
            flash('That email does not match the username!')
            flash('To register a new account, click the Register button below.')
            return redirect('/')
        else:
            login_user(user)
            return redirect('/index')
    return render_template('login.html', form=form)

@myapp_obj.route("/index", methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    current_user_role = current_user.act_role
    if current_user.act_role == 'admin':
        return redirect('/admin')
    ''' #if current_user.act_role == 'professor' or current_user.act_role == 'staff':
    #     return redirect('/addEvents')

    # made it so when student logs in they auto get checked into event 1 --> for testing and causes duplicates 
    # so when we do actual attendance we need to query and make sure user has not registered for event and then add to db, if they already in event then dont add/do anything
   
    if current_user.act_role == 'student':
        attendance = Attendance(eventID=1, userID=current_user.id, status='absent')
        db.session.add(attendance)
        db.session.commit()
    '''
    form = HomeForm()
    return render_template('index.html', form = form, current_user_role = current_user_role)

@myapp_obj.route("/admin", methods=['GET', 'POST'])
def admin():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    form = AdminForm()
    users = User.query.filter_by() 
    return render_template('admin.html', form = form , users = users)

@myapp_obj.route("/addEvents", methods=['GET', 'POST'])
def addEvents():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')

    #Only professors and staff can add events; validations checks here 
    if current_user.act_role not in ['professor', 'staff']:
        flash("You do not have permission to add events.")
        return redirect('/index')
    form = AddEventsForm()
   
    #query users who can be registed to events 
    users = User.query.filter(User.act_role.in_(['student', 'guest'])).all()
    form.users.choices = [(user.id, user.username) for user in users]  # Populate users field dynamicallyrm
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        new = Event(hostId = user.id, eventName = form.eventName.data, date = form.date.data, time = form.time.data, code = form.code.data)

        selected_users_id = form.users.data
        selected_users = User.query.filter(User.id.in_(selected_users_id)).all()
        new.users.extend(selected_users)  #scroll
        db.session.add(new)
        db.session.commit()

        for selected_user_id in selected_users_id:
            attend = Attendance.query.filter_by(eventID= new.id, userID=selected_user_id).first() 
            if attend is None: #check if user is not added then add them to attendance table
                attendance = Attendance(eventID=new.id, userID=selected_user_id, status='absent')
                db.session.add(attendance)
                db.session.commit()

        return redirect("/viewEvents")
    return render_template('addEvents.html', form = form)

@myapp_obj.route("/addtoEvents", methods=['GET', 'POST'])
def addtoEvents():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')

    #Students and guests can add themselves to the event via code
    form = AddtoEventsForm()

    if form.validate_on_submit():
        event = Event.query.filter_by(code =form.code.data).first()
        # attend = Attendance.query.filter_by(eventID= event.id, userID=current_user.id).all() 
        # if attend is None: #check if user is not added then add them to attendance table
        attendance = Attendance(eventID=event.id, userID=current_user.id, status='absent')
        db.session.add(attendance)
        db.session.commit()

        return redirect("/index")
    return render_template('addtoEvents.html', form = form)



@myapp_obj.route("/viewEvents", methods=['GET', 'POST'])
def viewEvents():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    form = ViewEventsForm()
    current_user_role = current_user.act_role
    if current_user.act_role == 'student' or current_user.act_role == 'guest':
        attendance = Attendance.query.filter_by(userID=current_user.id).first()
        events = Event.query.filter_by(id = attendance.eventID).all()
    if current_user.act_role == 'professor':
        events = Event.query.filter_by(hostId=current_user.id) 
    return render_template('viewEvents.html', form = form , events = events, current_user_role = current_user_role)

@myapp_obj.route("/attendance/<int:id>", methods=['GET', 'POST'])
def attendance(id):
    # if not current_user.is_authenticated: 
    #     flash("You aren't logged in yet!")
    #     return redirect('/')
    # event = Event.query.get(id) 
    # return redirect('/start/<int:id>', event = event)
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    form = AttendanceForm()
    event = Event.query.get(id) 
    user = User.query.filter_by(username=current_user.username).first()
    return render_template('attendance.html', form = form, user = user, event = event)

@myapp_obj.route("/viewAttendance/<int:id>", methods=['GET', 'POST'])
def viewAttendance(id):
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    form = viewAttendanceForm()
    event = Event.query.get(id)
    a = Attendance.query.filter_by(eventID = event.id) #for getting attendance times when user gets scanned
    attendances = Attendance.query.filter_by(eventID=event.id).all() 

    users = [User.query.get(attendance.userID) for attendance in attendances] 
    
    return render_template('viewAttendance.html', form = form, users = users, a = a)

@myapp_obj.route("/ApprovePicture/<int:id>", methods=["POST"])
def ApprovePicture(id): #get user id of the user is getting approved
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
        if request.method == "POST":
            if current_user.act_role == 'admin': 
                user = User.query.get(id)
                if user and user.picApprove == 1:
                    user.picApprove= 0 
                    db.session.commit()
                    flash("User picture approved successfully!" ,category = 'success')
                else:
                    flash("User picture not found or already approved!" , category ='error')
            else:
                flash('You do not have permission to approve users picture.' , category ='error')
    return redirect("/index")

@myapp_obj.route("/UnPicture/<int:id>", methods=["POST"])
def UnPicture(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
        if request.method == "POST":
            user = User.query.get(id)
            if current_user.act_role == 'admin':   
                if user and user.picApprove == 0:
                    user.picApprove=1 
                    db.session.commit()
                    flash("User picture approved successfully!" ,category = 'success')
                else:
                    flash("User picture already unapproved!" , category ='error')
            else:
                flash('You do not have permission to unapprove users picture.' , category ='error')
    return redirect("/index")

@myapp_obj.route("/ApproveUser/<int:id>", methods=["POST"])
def ApproveUser(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
        if request.method == "POST":
            if current_user.act_role == 'admin': 
                user = User.query.get(id)
                if user and user.roleApprove == 1:
                    user.roleApprove = 0 #change the approved to true so that the registered user can now access the website
                    user.act_role = user.reg_role
                    db.session.commit() #commit changes after editing
                    flash("User approved successfully!" ,category = 'success')
                else:
                    flash("User not found or already approved!" , category ='error')
            else:
                flash('You do not have permission to approve users.' , category ='error')
    return redirect("/index")

@myapp_obj.route("/UnapproveUser/<int:id>",  methods=["POST"])
def UnapproveUser(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
        if request.method == "POST":
            user = User.query.get(id)
            if current_user.act_role == 'admin': #Only admin can reject the user. Once rejected, the user will need to register again to be reconsidered
                if user and user.roleApprove== 0:
                    user.roleApprove=1 
                    user.act_role= 'guest'
                    db.session.commit()
                    flash("User unapproved successfully!", category = 'success')
                else:
                        flash("User already unapproved!", category ='error')
            else:
                flash('You do not have permission to unapprove users.' , category ='error')
    return redirect("/index")

@myapp_obj.route("/change_user_role/<int:user_id>", methods=["GET", "POST"])
def change_user_role(user_id):
    if request.method == "POST":
        if current_user.act_role == 'admin': #only admin can change the role fo user
          user = User.query.get(user_id)
          if user:
            new_role = request.form.get("new_role")
            if new_role:
              if new_role != user.act_role:
                  user.act_role = new_role #update the user role to new role 
                  db.session.commit() #commit changes of the session 
                  flash("User role updated successfully!", category = 'success')
              else:
                 flash("New role is the same as the current role.",category ='error')
            else:
               flash ('No new roles are provided.',category ='error')
          else:
            flash("User not found!",category ='error')
        else:
          flash('You do not have permission to change user roles.' ,category ='error')
    return redirect(url_for("admin"))

# logout button only appears when logged in
@myapp_obj.route("/logout", methods=['POST', 'GET'])
def logout():
    if not current_user.is_authenticated: 
        flash("You're already logged out!")
        return redirect('/')
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        return redirect("/")
    return render_template('logout.html', title = 'Logout Confirmation', form = form)

@myapp_obj.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: 
        flash("You are already logged in!")
        return redirect('/index')
    form = RegisterForm()

    # if form inputs are valid and they clicked the signin button
    if form.sign.data:
       return redirect('/')
    
    checkUsername = User.query.filter_by(username=form.username.data).first()
    if checkUsername is not None: # if user already registered, then redirect
       flash('That username already exists')
       return redirect ('/register')
    
    checkEmail = User.query.filter_by(email=form.email.data).first()
    if checkEmail is not None: # if user already registered, then redirect
       flash('That email already exists')
       return redirect ('/register')
    

    if form.validate_on_submit():
        if form.reg_role.data != 'admin' and form.reg_role.data != 'student' and form.reg_role.data != 'professor'  and form.reg_role.data != 'guest':
                flash("Invalid role!")
                return redirect ('/register')
        
        if request.method == "POST":
            file = request.files['file']

            # file image must be validated before registering is complete
            try:
                encode = encode_image(file)
                new = User (
                    fname = form.fname.data,
                    lname = form.lname.data,
                    username = form.username.data,
                    email = form.email.data,
                    file = file.filename,
                    data=encode,
                    picApprove = 0,
                    roleApprove = 0,
                    reg_role = form.reg_role.data,
                    act_role = 'guest',
                    rfid = None #manually set this for now
                )
                new.set_password(form.password.data)
                db.session.add(new)
                db.session.commit()
                return redirect('/')

            except ValueError as e:
                flash(str(e))

    return render_template('register.html', form=form)

 
@myapp_obj.route('/assign_rfid_to_user/<int:user_id>', methods=['POST'])
def assign_rfid_to_user(user_id):
    data = request.get_json()
    rfid_tag = data.get("rfid_tag")

    if not rfid_tag:
        return {"success": False, "message": "No RFID tag provided."}, 400

    user = User.query.get_or_404(user_id)

    # Check if the RFID tag is already assigned
    existing_user = User.query.filter_by(rfid=rfid_tag).first()
    if existing_user:
        return {"success": False, "message": f"RFID tag is already assigned to {existing_user.username}."}, 400

    # Assign the RFID tag to the user
    user.rfid = rfid_tag
    db.session.commit()

    return {"success": True}


@myapp_obj.route('/download/<int:id>')
def download(id):
    img = User.query.filter_by(id=id).first()
    return send_file(BytesIO(img.data),
                     download_name=img.file, as_attachment=False) #change to true if want it to be downloaded auto; false rn to display on browser

'''

@myapp_obj.route('/download/<int:id>')
def download(id):
    img = User.query.filter_by(id=id).first()

    if not img or not img.data:
        return "Image not found", 404

    # Determine MIME type dynamically based on file extension
    mimetype, _ = guess_type(img.file)
    mimetype = mimetype or "application/octet-stream"  # Fallback MIME type

    return send_file(
        BytesIO(img.data),
        mimetype=mimetype,
        download_name=img.file if img.file else f"user_{id}.jpg",
        as_attachment=False
    )
 
The idea is:
    - constantly poll for RFID scans
    - if nothing is scanned, camera just stays on and does nothing
    - once there is a scan, stop scanning for any more RFID
        - check if that ID is registered for this current event
        - using that ID, start the facial recognition process to only look for the user associated with that ID
            - if it takes too long, we can make it timeout so they have to scan RFID again (prevents infinite loop if no face matches)
        - if face verified, mark attendance, and break out of facial recognition function, and go back to polling for RFID scans
            - camera stays on the whole time until admin quits
'''
@myapp_obj.route('/start-attendance/<int:id>')
def start_attendance(id):
    users_in_event = User.query.filter(User.events.any(id=id)).all()
    # Initialize and start threads
    camera_thread = threading.Thread(target=display_camera, daemon=True)
    rfid_thread = threading.Thread(target=poll_rfid, args=(users_in_event,), daemon=True)
    
    camera_thread.start()
    rfid_thread.start()
    #link these both to start button and create stop functions for both

    return Response(display_camera(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@myapp_obj.route('/stop-attendance')
def stop_attendance():
    end_event.set()
    return redirect('/viewEvents')

latest_rfid_tag = None

def poll_rfid_background():
    """
    Background thread to continuously poll the RFID reader and store the latest tag.
    """
    global latest_rfid_tag
    try:
        RFID_PORT = '/dev/ttyUSB0'
        BAUD_RATE = 9600
        ser = serial.Serial(RFID_PORT, BAUD_RATE, timeout=1)  # Adjust port and baudrate as needed
        print("Starting background RFID polling...")
        while True:
            rfid_data = ser.readline().decode('utf-8').strip()
            if rfid_data:
                latest_rfid_tag = rfid_data  # Update the latest RFID tag
                print(f"RFID Tag detected: {rfid_data}")
    except Exception as e:
        print(f"Error in RFID polling: {e}")

# Start the background RFID polling thread
threading.Thread(target=poll_rfid_background, daemon=True).start()

@myapp_obj.route('/get_latest_rfid', methods=['GET'])
def get_latest_rfid():
    """
    Route to fetch the latest scanned RFID tag.
    """
    global latest_rfid_tag
    tag = latest_rfid_tag
    latest_rfid_tag = None  # Reset after fetching
    return {"rfid_tag": tag}  # Return as JSON

@myapp_obj.route('/rfid_scan_popup', methods=['GET'])
def rfid_scan_popup():
    return render_template('rfid_scan.html')  # Save the polling HTML as rfid_scan.html
