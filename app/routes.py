from flask import render_template
from flask import redirect, request, url_for
from flask import flash, send_file, send_from_directory
from .forms import LoginForm, LogoutForm, HomeForm, RegisterForm, AdminForm
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

from app import myapp_obj
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from werkzeug.utils import secure_filename
from io import BytesIO
from . import db

import threading
from .facial_recognition import facial_utils, recognition, start_attendance
from rfid import poll_rfid

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
    if current_user.act_role == 'admin':
        return redirect('/admin')
    form = HomeForm()
    return render_template('index.html', form = form)

@myapp_obj.route("/admin", methods=['GET', 'POST'])
def admin():
    if not current_user.is_authenticated: 
        flash("You aren't logged in yet!")
        return redirect('/')
    form = AdminForm()
    users = User.query.filter_by() 
    return render_template('admin.html', form = form , users = users)

@myapp_obj.route("/ApprovePicture/<int:id>")
def ApprovePicture(id): #get user id of the user is getting approved
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
         user = User.query.get(id)
         user.picApprove=0 
         db.session.commit()
         return redirect("/index")
    #no need to render when approving

@myapp_obj.route("/UnPicture/<int:id>")
def UnPicture(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
         user = User.query.get(id)
         user.picApprove=1 
         db.session.commit()
         return redirect("/index")

@myapp_obj.route("/ApproveUser/<int:id>")
def ApproveUser(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
         user = User.query.get(id)
         user.roleApprove=0 
         db.session.commit()
         return redirect("/index")

@myapp_obj.route("/UnapproveUser/<int:id>")
def UnapproveUser(id):
    if not current_user.is_authenticated:
        flash("You aren't logged in yet!")
        return redirect('/')
    else: 
         user = User.query.get(id)
         user.roleApprove=1 
         db.session.commit()
         return redirect("/index")

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
                encode = facial_utils.encode_image(file)
                new = User (
                    fname = form.fname.data,
                    lname = form.lname.data,
                    username = form.username.data,
                    email = form.email.data,
                    file = file.filename,
                    data=encode,
                    picApprove = 1,
                    roleApprove = 1,
                    reg_role = form.reg_role.data,
                    act_role = 'guest'
                )
                new.set_password(form.password.data)
                db.session.add(new)
                db.session.commit()
                return redirect('/')

            except ValueError as e:
                flash(e)

    return render_template('register.html', form=form)

@myapp_obj.route('/download/<int:id>')
def download(id):
    img = User.query.filter_by(id=id).first()
    return send_file(BytesIO(img.data),
                     download_name=img.file, as_attachment=False) #change to true if want it to be downloaded auto; false rn to display on browser

@myapp_obj.route('/start-attendance/<int:hostId>')
def start_attendance(hostId):
    # while True:
        # poll for RFID scans here
        '''
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

    # Initialize and start threads
    rfid_thread = threading.Thread(target=poll_rfid, daemon=True)
    recognition_thread = threading.Thread(target=start_attendance, daemon=True)
    
    rfid_thread.start()
    recognition_thread.start()


