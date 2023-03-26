from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.painting_model import Painting
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def home_page():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('home_page.html')

#--------------------------------------------------------------------

@app.route('/register', methods = ['POST'])
def register():
    # 1. validate the form
    if not User.validate_user(request.form):
        return redirect('/')
    
    #2. create the hashed password
    hashed_password = bcrypt.generate_password_hash(request.form['password'])

    #3 create the data dictionary with the hashed password as the password
    data = {
        'first_name' : request.form['first_name'],
        'last_name' : request.form['last_name'],
        'email' : request.form['email'],
        'password' : hashed_password
    }

    #create the new user using the register method and set it to session['user_id']
    session['user_id'] = User.register(data)
    
    return redirect('/dashboard')

#---------------------------------------------------------------

@app.route('/login', methods = ['POST'])
def login():
    data = {
        'email' : request.form['email']
    }

    user_in_database = User.get_by_email(data)

    if not user_in_database:
        flash("Invalid login information. Try again!")
        return redirect('/')

    if not bcrypt.check_password_hash(user_in_database.password, request.form['password']):
        flash("Invalid login information. Try again!")
        return redirect('/')
    session['user_id'] = user_in_database.id 

    return redirect('/dashboard')

#---------------------------------------------------------------
@app.route('/logout')
def logout():
    if'user_id' in session:
        del session['user_id']
        return redirect('/')

#---------------------------------------------------------------

@app.route('/dashboard')
def dashboard():
        #check if the user has logged in yet. if not, redirect them back to home page
    if 'user_id' not in session:
        return redirect('/')
        
    data = {
        'id' : session['user_id']
    }

    user = User.get_by_id(data)

    all_paintings = Painting.get_all_paintings_with_users()

    get_purchased_paintings = User.get_all_paintings_user_has_purchased(data)


    return render_template('dashboard.html', user = user, all_paintings = all_paintings,  get_purchased_paintings = get_purchased_paintings)

#-----------------------------------------------------------------