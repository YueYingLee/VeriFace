from flask import render_template
from flask import redirect, request, url_for
from flask import flash
from .forms import LoginForm, LogoutForm, HomeForm, RegisterForm
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


# # Define allowed files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

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
    form = HomeForm()
    return render_template('index.html', form = form)

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
        if request.method == "POST":
            file = request.files['file']
            
            #approve = 1 initally so all users registered need to be approved
            new = User(fname = form.fname.data, lname = form.lname.data, username = form.username.data, email = form.email.data, file = file.filename, data=file.read())
            new.set_password(form.password.data)
            db.session.add(new)
            db.session.commit()
        # login_user(user)
            # flash("Account created!")
            return redirect('/')
    return render_template('register.html', form=form)