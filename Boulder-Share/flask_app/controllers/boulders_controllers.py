from flask_app import app
from flask import render_template, redirect, request, session, flash, url_for
from flask_app.models.user import User
from flask_app.models.boulders import Boulder 
import os
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/dashboard')
def user_profile():
    if 'user_id' not in session: # checks to see if the user id is in session so that only a logged in user can view a page and if they aren't logged in then we display an error message. (route protection)
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    data = {'id': session['user_id']} # gets the user_id that was stored in session when a user registers or logs in and stores it in a variable so that it can be passed to the get user with boulder method so we are just getting that users boulders
    return render_template('dashboard.html', user_boulders = User.get_user_with_boulders(data), all_boulders = Boulder.get_boulders_and_climber())

#view one boulder
@app.route('/boulder/<int:boulder_id>')
def show_boulder_and_climber(boulder_id):
    if 'user_id' not in session:
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    return render_template('view_boulder.html', boulder = Boulder.get_boulder_with_climber(boulder_id))

#this route just displays the create a boulder page. 
@app.route('/create/boulder')
def create_post():
    if 'user_id' not in session: 
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    return render_template('create_boulder.html')#render template is how we render our html pages 

#when the form is submitted on the create boulder page it will execute this route and it's method for creating a boulder.
@app.route('/create/boulder/process', methods=['POST'])
def create_a_boulder():    
    if 'user_id' not in session:
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    file = request.files['url']
    if file.filename == '': # checks to see if the file field is empty and if it is it will display an error message
        flash('No file selected*', 'Boulder')
    if Boulder.is_valid(request.form) and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) #this saves the file submitted to the path we are creating by joining our uploads path to our filename path
        print('successful save')
        image_url = os.path.join('uploads', filename) #assign not the entire path but just the path to the image so that it can be stored in the db and then displayed to the user. 
        print(image_url)
        boulder_data = {
                'name' : request.form.get('name'),
                'url' : image_url,
                'grade' : request.form.get('grade'),
                'rating' : request.form.get('rating'),
                'location' : request.form.get('location'),
                'description' : request.form.get('description'),
            }
        Boulder.create_boulder(boulder_data)
        return redirect('/dashboard')
    flash('File format is not accepted*', 'Boulder')
    return redirect('/create/boulder')#if the validation is unsuccessful we will redirect back to the create boulder page and display the errors

#this displays the edit boulder page only if the current user has created that boulder and prepopulates the fields
@app.route('/boulder/edit/<int:boulder_id>')
def edit_boulder(boulder_id):
    if 'user_id' not in session:
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    boulder = Boulder.get_boulder_by_id(boulder_id)#gets the boulder by the boulder_id passed from the client and sets it to a variable(we use this to check if the user_id that is associated with it is the same as the user_id currently in session to ensure that only the creator of this boulder can edit it.)
    if session['user_id'] != boulder.user_id: #checks to see if the user_id in session is the same as the user_id associated with the boulder and if not it logs the user out
        session.clear()
        flash('You are not allowed to do that. Login again', 'error')
        return redirect('/')
    return render_template('edit_boulder.html', boulder = Boulder.get_boulder_by_id(boulder_id)) #the get query and assigning that to a variable is how we pass it back to the client so now we can access that variables values in our client side

#when the form is submitted it carries out this route.
@app.route('/boulder/edit/process', methods = ['POST'])
def update_recipe():
    if 'user_id' not in session:
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    boulder = Boulder.get_boulder_by_id(request.form.get('id'))
    file = request.files['url']
    if file.filename == '':
        flash('No file selected*', 'Boulder')
    if Boulder.is_valid(request.form) and allowed_file(file.filename):
        if boulder.url:
            old_img_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(boulder.url))
        if os.path.exists(old_img_path):
            os.remove(old_img_path)
        filename = secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('successful save')
        image_url = os.path.join('uploads', filename)
        print(image_url)
        boulder_data = {
                'id' : request.form.get('id'),
                'name' : request.form.get('name'),
                'url' : image_url,
                'grade' : request.form.get('grade'),
                'rating' : request.form.get('rating'),
                'location' : request.form.get('location'),
                'description' : request.form.get('description'),
            }
        Boulder.update_boulder(boulder_data)
        return redirect('/dashboard') #when creation is successful redirect the user to the dashboard page
    flash('File format is not accepted*', 'Boulder')
    return redirect(f'/boulder/edit/{request.form["id"]}') #when validations fail direct the user back to the edit page with the same information. 

#this is for deleting a boulder
@app.route('/boulder/delete/<int:boulder_id>')#boulder id is passed in using jinja from the front end. 
def delete_boulder(boulder_id):
    if 'user_id' not in session:
        flash('You are not authorized to view this page.', 'error')
        return redirect('/')
    boulder = Boulder.get_boulder_by_id(boulder_id)#gets the boulder by the boulder_id passed from the client and sets it to a variable
    if session['user_id'] != boulder.user_id: #checks to see if the user_id in session is the same as the user_id associated with the boulder and if not it logs the user out
        session.clear()
        flash('You are not allowed to do that. Login again', 'error')
        return redirect('/')
    Boulder.delete(boulder_id)
    return redirect('/dashboard')

#this is our catch-all route this catches all other routes that don't exist and displays our 404 page
@app.route('/<path:any_path>')
def catch_all(any_path):
    return render_template('/404.html', current_path = any_path)