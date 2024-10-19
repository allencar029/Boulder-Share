from flask_app.config.mysqlconnection import connect_to_mysql
from flask_app.models import user
from flask import session, flash

class Boulder:
    DB = 'users_and_boulders_schema'
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.url = data['url']
        self.grade = data['grade']
        self.rating = data['rating']
        self.location = data['location']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        self.climber = None

    #this is for creating a boulder
    @classmethod
    def create_boulder(cls, form_data):
        query = """
            INSERT INTO boulders (name, url, grade, rating, location, description, user_id)
            VALUES (%(name)s, %(url)s, %(grade)s, %(rating)s, %(location)s, %(description)s, %(user_id)s );"""
        # creates a copy of the data being passed 
        form_data = form_data.copy()
        # assigns the user_id key value stored in session to the data dictionary user_id key
        form_data['user_id'] = session['user_id']
        boulder_id = connect_to_mysql(cls.DB).query_db(query, form_data)
        return boulder_id
    
    #this is for displaying boulders and their climber
    @classmethod
    def get_boulders_and_climber(cls):
        query = """
            SELECT * 
            FROM boulders
            JOIN users
            ON boulders.user_id = users.id
            ORDER BY boulders.id DESC;"""
        results = connect_to_mysql(cls.DB).query_db(query)
        print(results)
        boulders = [] #create an empty list of boulders that we will add the boulder object to which will also contain its corresponding climber data
        for join_dict in results: #loops through each row of the query results.
            one_boulder = cls(join_dict) #this creates an instance of the Boulder class by passing the row data(join_dict) to the class constructor. This will initialize a Boulder object with the fields from the boulders table in the current row and stores the Boulder object in a variable. 
            climber_data = { #this dictionary is created to hold the data for the user associated with the current boulder. 
                'id' : join_dict['users.id'], #these keys correspond to the fields from the users table and extracts them using the join_dict to access the keys
                'first_name' : join_dict['first_name'],
                'last_name' : join_dict['last_name'],
                'email' : join_dict['email'],
                'password' : None, #left blank for security
                'created_at' : join_dict['users.created_at'],
                'updated_at' : join_dict['users.updated_at'],
            }
            climber = user.User(climber_data)#creates an instance of the User class by passing in the climber_data dictionary. Creates a user object that represents a climber and then stores it in a variable
            one_boulder.climber = climber #this assigns the climber object to the climber attribute of the current Boulder object. This creates a relationship between the Boulder and User objects similar to how they are related in the db.
            boulders.append(one_boulder) #adds the fully populated boulder object(with its associated climber) to the boulders list
        return boulders #this returns the boulders list which contains multiple boulder objects, each with its associated climber after the loop has processed all rows in the query results 
    
    #this is for updating a boulder
    @classmethod
    def update_boulder(cls, data):
        query = """
            UPDATE boulders
            SET name=%(name)s, url=%(url)s, grade=%(grade)s, rating=%(rating)s, location=%(location)s, description=%(description)s
            WHERE id = %(id)s;"""
        return connect_to_mysql(cls.DB).query_db(query, data)
    
    #this is for deleting a boulder
    @classmethod
    def delete(cls, boulder_id):
        print(boulder_id)
        query = """
            DELETE FROM boulders
            WHERE id = %(id)s"""
        return connect_to_mysql(cls.DB).query_db(query, {"id": boulder_id}) #delete from the boulders table the boulder we are identifying by passing in the boulder_id, we pass it in by using a key value pair to the %(id)s place holder, this helps prevent sql injection but also it is required by the library to pass it in like that.
    
#this will be for prepopulating fields for editing a boulder
    @classmethod
    def get_boulder_by_id(cls, boulder_id): #this exists so we can prepopulate fields when a user wants to edit a boulder
        query = """
            SELECT * FROM boulders
            WHERE id = %(id)s;"""
        #store the result of the query in a variable
        this_boulder = connect_to_mysql(cls.DB).query_db(query, {'id': boulder_id})
        return cls(this_boulder[0])
    
    # this will be used for displaying a boulder and its data. we will use its id in the url(route) to access the boulder via passing the id from the front end via the route to our class method which is here in the back end.
    # class method to get one boulder with its climber. using just a join means that if any of the fields don't match on the join it won't return anything. We only want it to return something if it exists. The Join ensures that it will always have a climber associated with it.(which in this case it should)
    @classmethod
    def get_boulder_with_climber(cls, boulder_id): #method declaration, the cls allows us to access the DB attribute which contains the database schema which we then pass in to connect to our sql database to send the query and get the results
        query = """
            SELECT * FROM boulders
            JOIN users
            ON boulders.user_id = users.id 
            WHERE boulders.id = %(id)s;""" # ON is where we perform the join on in this case we join the tables on the user_id field in the boulders table and the id field is the users table. It will then fetch all columns from both tables and return something if the users.id exists.
        results = connect_to_mysql(cls.DB).query_db(query, {'id': boulder_id}) #we store the result of the above query. the .query_db executes the above sql query passing in the boulder_id dynamically to the %(id)s placeholder.
        boulder = cls(results[0]) # This creates an instance of the Boulder class with the first row in results(which is the boulder's data and some initial user information(via the join)) 
        for join_dict in results:
            boulder_climber_data = { #this dictionary is constructed to hold the user(cliber) data from the current row.
                'id' : join_dict['users.id'], #these are the fields from the JOIN result.
                'first_name' : join_dict['first_name'],
                'last_name' : join_dict['last_name'],
                'email' : join_dict['email'],
                'password' : None, #this is none because we do not want to include the users actual password when fetching boulder data. 
                'created_at' : join_dict['users.created_at'],
                'updated_at' : join_dict['users.updated_at'],
            }
            climber = user.User(boulder_climber_data) #this creates an instance of the User class passing in the climber's data from the boulder_climber_data dictionary. we then store the newly created user object in the climber variable
            boulder.climber = climber #this assigns the climber(the user object) to the boulder object, associating the user (climber) with the boulder. This makes it possible to access the climbers information when working witht the boulder object. 
        return boulder 
    
    #boulder validations
    @staticmethod
    def is_valid(form_data): # we define our is_valid static method here and it takes in a single argument form data which will be an object containing all the data we are submitting when we submit a form. 
        is_valid = True #set is_valid to true so that if a validation fails it will set it to false
        #name field validation
        if not form_data['name'].strip(): #this checks whether the stripped name field is empty. if it is empty or contains just whitespace it will equal true.
            is_valid = False #if the field is empty or full of white space it makes the field not valid by setting it to false
            flash('Name Required*', 'Boulder') #this sends the error to the client, the first part is the message and the second is the category of the error which we have defined as boulder.
        elif len(form_data['name']) < 1: #this checks is the length of the name field (which we grab by using the form_data dictionary that is passed in when the form is submitted and then accessing that dictionaries name field)
            is_valid = False # if the field is less than one character it makes the field not valid by setting it to false
            flash('Name 1 Character Minimum*', 'Boulder') #this sends the error to the client

        # #url validations
        # if form_data['url'] == '':
        #     is_valid = False
        #     flash('Image not selected, Image Required*', 'Boulder')

        #grade validations
        if not form_data['grade'].strip():
            is_valid = False
            flash('Grade Required*', 'Boulder')
        elif len(form_data['grade']) < 1:
            is_valid = False
            flash('Grade 1 Character Minimum*', 'Boulder')

        #rating validations
        if not form_data['rating'].strip():
            is_valid = False
            flash('Rating Required*', 'Boulder')
        elif int(form_data['rating']) < 0: #for this to work we need to convert the forms input to an integer that is why we wrap the form_data in int()
            is_valid = False
            flash('Rating must be between 0-5*', 'Boulder')
        elif int(form_data['rating']) > 5:
            is_valid = False
            flash('Rating must be between 0-5*', 'Boulder')

        #location validations
        if not form_data['location'].strip():
            is_valid = False
            flash('Location Required*', 'Boulder')
        elif len(form_data['location']) < 3:
            is_valid = False
            flash('Location 3 Character Minimum*', 'Boulder')

        #description validations
        if not form_data['description'].strip():
            is_valid = False
            flash('Description Required*', 'Boulder')
        elif len(form_data['description']) < 3:
            is_valid = False
            flash('Description 3 Character Minimum*', 'Boulder')

        return is_valid