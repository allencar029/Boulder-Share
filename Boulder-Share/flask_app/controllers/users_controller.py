from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.controllers import boulders_controllers
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/create/user', methods=['POST'])
def register():
    print(f"request.form: {request.form}")
    if User.is_valid(request.form):
        data={
            "fname": request.form["fname"],
            "lname": request.form["lname"],
            "email": request.form["email"],
            "password": bcrypt.generate_password_hash(request.form['password'])
        }
        user_id = User.save(data)
        # store user id into session
        session['user_id'] = user_id
        print(session)
        return redirect('/dashboard')
    return redirect('/')

@app.route('/login/user', methods=['POST'])
def login():
    data = { "email" : request.form["email"] }
    user_in_db = User.get_by_email(data)
    if user_in_db:
        if bcrypt.check_password_hash(user_in_db.password, request.form['password']):
            session['user_id'] = user_in_db.id
            return redirect('/dashboard')
    flash("Invalid Email/Password", 'Login')
    return redirect('/')

@app.route('/logout')
def clear_session():
    session.clear()
    return redirect('/')