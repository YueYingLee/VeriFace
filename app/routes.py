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
from .facial_recognition.utils import poll_rfid, display_camera, encode_image
from .facial_recognition.global_vars import end_event

from .facial_recognition.rfid_handler import read_rfid

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
        current_user.events.append(event) ## ADDED
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
        if attendance is not None:
            events = Event.query.filter_by(id = attendance.eventID).all()
        else:
            events = Event.query.filter_by(id = '0').all()
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

@myapp_obj.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if request.method == "POST":
        if current_user.act_role == 'admin': #User can only delete user if they are admin. Else, error message will be popped out
          user = User.query.get(user_id)
          if user: #if the user is found in database, delete the user and commit the change of the session
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully!", category = 'success')
          else:
            flash("User not found!", category ='error')
        else:
             flash('You do not have permission to delete users.' , category ='error')
    return redirect(url_for("index"))

@myapp_obj.route("/change_user_role/<int:user_id>", methods=["GET", "POST"])
def change_user_role(user_id):
    if request.method == "POST":
        if current_user.act_role != 'admin':
            flash('You do not have permission to change user roles.', category='error')
            return redirect(url_for("admin"))

        user = User.query.get(user_id)
        if not user:
            flash("User not found!", category='error')
            return redirect(url_for("admin"))

        new_role = request.form.get("new_role")
        if not new_role:
            flash('No new role provided.', category='error')
            return redirect(url_for("admin"))

        if new_role == user.act_role:
            flash("New role is the same as the current role.", category='error')
            return redirect(url_for("admin"))

        # Update the user role
        user.act_role = new_role
        db.session.commit()
        flash("User role updated successfully!", category='success')

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
                    picApprove = 1,
                    roleApprove = 1, #0 is true and 1 is false
                    reg_role = form.reg_role.data,
                    act_role = 'guest',
                    rfid = None # to be set later by admin
                )
                new.set_password(form.password.data)
                db.session.add(new)
                db.session.commit()
                return redirect('/')

            except ValueError as e:
                flash(str(e))

    return render_template('register.html', form=form)

@myapp_obj.route('/trigger_rfid/<int:user_id>', methods=['POST'])
@login_required
def trigger_rfid(user_id):
    print(f"Trigger RFID endpoint hit for user ID: {user_id}")

    # Verify admin privileges
    if current_user.act_role != "admin":
        print("Permission denied: Non-admin user attempted to scan RFID.")
        return {"success": False, "message": "Permission denied."}, 403

    try:
        # Wait for the RFID tag
        print("Waiting for RFID scan...")
        rfid_data = read_rfid(timeout=10)  # Call the read_rfid function
        print(f"RFID Data from Reader: {rfid_data}")

        if not rfid_data:
            print("No RFID tag detected within the timeout period.")
            return {"success": False, "message": "No RFID tag detected. Please try again."}, 400

        # Check if the RFID tag is already assigned to another user
        existing_user = User.query.filter_by(rfid=rfid_data).first()
        if existing_user:
            if existing_user.id == user_id:
                print(f"RFID tag {rfid_data} is already assigned to this user ({existing_user.username}).")
                return {"success": False, "message": "RFID tag is already assigned to this user."}, 400
            else:
                print(f"RFID tag {rfid_data} is already assigned to another user ({existing_user.username}).")
                return {
                    "success": False,
                    "message": f"RFID tag is already assigned to {existing_user.username}."
                }, 400

        # Assign the RFID tag to the current user
        user = User.query.get_or_404(user_id)
        print(f"Assigning RFID tag {rfid_data} to user {user.username}.")
        user.rfid = rfid_data

        # Commit the database transaction
        db.session.commit()
        print(f"RFID tag {rfid_data} successfully assigned to user {user.username}.")
        return {"success": True, "rfid_tag": rfid_data}, 200

    except Exception as e:
        print(f"Error during RFID assignment: {e}")
        db.session.rollback()  # Roll back the transaction in case of error
        return {"success": False, "message": "Error during RFID assignment."}, 500

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
    rfid_thread = threading.Thread(target=poll_rfid, args=(users_in_event,id), daemon=True)
    
    camera_thread.start()
    rfid_thread.start()
    #link these both to start button and create stop functions for both

    return Response(display_camera(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@myapp_obj.route('/stop-attendance')
def stop_attendance():
    end_event.set()
    return redirect('/viewEvents')