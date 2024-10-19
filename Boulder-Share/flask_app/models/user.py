from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import boulders
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
class User: #This defines a Python class called User. A class is a blueprint for creating objects(instances) that have specific properties and methods
    DB = 'users_and_boulders_schema' #This is a class attribute, this is used when connecting to our MySQL database
    def __init__(self, data):  # the init is a constructor method which is automatically called when a new instance of the User class is created. This initializes the attributes(variables) of the new instance based on the data passed in.
        self.id = data['id'] # These lines assign values from the data dictionary passed in to the instance attributes.
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.boulders = [] #this is used to store boulder objects that are related to the user which we will populate in our class methods. 

    @classmethod
    def save(cls, data):
        query = """
            INSERT INTO users (first_name, last_name, email, password, created_at, updated_at)
            VALUES (%(fname)s, %(lname)s, %(email)s, %(password)s, NOW(), NOW());"""
        user_id = connect_to_mysql(cls.DB).query_db(query, data)
        return user_id
    
    @classmethod
    def get_by_email(cls, data):
        print(data)
        query = """
        SELECT *
        FROM users
        WHERE email = %(email)s;"""
        results = connect_to_mysql(cls.DB).query_db(query, data)
        print(results)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_by_id(cls, data):
        print(data)
        query = """
        SELECT *
        FROM users
        WHERE id = %(id)s;"""
        results = connect_to_mysql(cls.DB).query_db(query, data)
        print(results)
        # check if results is empty before attempting to create an instance of a class
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_user_with_boulders(cls, data):
        query = """
            SELECT * 
            FROM users 
            LEFT JOIN boulders 
            ON boulders.user_id = users.id
            WHERE users.id = %(id)s"""
        results = connect_to_mysql(cls.DB).query_db(query, data)
        this_climber = cls(results[0])
        for join_dict in results:
            print(join_dict)
            boulder_data = {
                'id' : join_dict['boulders.id'],
                'name' : join_dict['name'],
                'url' : join_dict['url'],
                'grade' : join_dict['grade'],
                'rating' : join_dict['rating'],
                'location' : join_dict['location'],
                'description' : join_dict['description'],
                'created_at' : join_dict['boulders.created_at'],
                'updated_at' : join_dict['boulders.updated_at'],
                'user_id' : join_dict['user_id']
            }
            this_climber.boulders.append(boulders.Boulder(boulder_data))
            print(this_climber.boulders)
        return this_climber
    
        #Registration Validations
    @staticmethod
    def is_valid(form_data):
        is_valid = True
        #first name field validation
        if not form_data['fname'].strip(): #if name field is blank the strip removes the whitespace in the field so like if someone presses the spacebar a bunch it removes the empty spaces
            is_valid = False
            flash('First Name Required*', 'Registration') # flash is how we display the error messages, it sends a short message to the client so our html page and there we access them and display them.
        elif len(form_data['fname']) < 2:
            is_valid = False
            flash('First Name 2 Character Minimum*', 'Registration')
        # Last name field validation
        if not form_data['lname'].strip():
            is_valid = False
            flash('Last Name Required*', 'Registration')
        elif len(form_data['lname']) < 2:
            is_valid = False
            flash('Last Name 2 Character Minimum*', 'Registration')
        # Email validations
        if not form_data['email'].strip():
            is_valid = False
            flash('Email Required*', 'Registration')
        elif not EMAIL_REGEX.match(form_data['email']):
            is_valid = False
            flash('Invalid email address!*', 'Registration')
        elif User.get_by_email(form_data):
            is_valid = False
            flash('Email in Use', 'Registration')
        # Password validations
        if not form_data['password'].strip():
            is_valid = False
            flash('Password Required', 'Registration')
        elif len(form_data['password']) < 8:
            is_valid = False
            flash('8 Character minimum', 'Registration')
        elif not re.search(r'[A-Z]', form_data['password']):
            is_valid = False
            flash('Password must contain at least one uppercase letter', 'Registration')
        elif not re.search(r'[a-z]', form_data['password']):
            is_valid = False
            flash('Password must contain at least one lowercase letter', 'Registration')
        elif not re.search(r'[0-9]', form_data['password']):
            is_valid = False
            flash('Password must contain at least one number', 'Registration')
        elif form_data['password'] != form_data['confirm_password']:
            is_valid = False
            flash("Passwords do not match!", 'Registration')

        return is_valid
    
    