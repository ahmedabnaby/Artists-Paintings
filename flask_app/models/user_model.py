from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import painting_model 
from flask_app import app
from flask import flash
import re
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod 
    def register(cls, data):
        query = """
        INSERT INTO users (first_name, last_name, email, password)
        VALUES(%(first_name)s, %(last_name)s, %(email)s, %(password)s);
        """
        return connectToMySQL('paintings').query_db(query,data)

    @classmethod
    def get_by_id(cls, data):
        query = '''
        SELECT * FROM users
        WHERE users.id = %(id)s;
        '''
        user = connectToMySQL('paintings').query_db(query, data)
        return cls(user[0])

    @classmethod
    def get_by_email(cls, data):
        query = '''
        SELECT * FROM users
        WHERE users.email = %(email)s;
        '''
        
        user = connectToMySQL('paintings').query_db(query, data)
        if len(user) > 0:
            return cls(user[0])
        return False

    @classmethod
    def get_all_users(cls):
        query = "SELECT * FROM users;"
        users_from_db = connectToMySQL('paintings').query_db(query)
        users_list = []
        for each_user in users_from_db:
            users_list.append(cls(each_user))
        return users_list

    @classmethod
    def get_all_paintings_user_has_purchased(cls,data):
        query = """
        SELECT *
        FROM users
        JOIN user_has_painting
        ON users.id = user_has_painting.user_id
        JOIN paintings
        ON user_has_painting.painting_id = paintings.id
        WHERE users.id = %(id)s;
        """
        results = connectToMySQL('paintings').query_db(query,data)
        if not results:
            return False

        all_purchases = []
        for row in results:
            print("START OF ROW---------")
            print(row)
            print("END OF ROW-----------")
            this_purchase = cls(row)
            painting_data ={
                **row,
                'id':row['paintings.id'],
                'created_at':row['paintings.created_at'],
                'updated_at':row['paintings.updated_at']
            }
            this_painting = painting_model.Painting(painting_data)
            print("THIS PAINTING'S CREATOR")
            creator_data = {
                'id' : row['paintings.user_id']
            }
            this_purchase.painting_bought = this_painting
            this_painting.creator = User.get_by_id(creator_data)
            all_purchases.append(this_purchase)

        print("THIS IS ALL THE PURCHASES\n", all_purchases)
        return all_purchases




    @staticmethod
    def validate_user(data):
        is_valid = True

        if len(data['first_name']) <2:
            flash("First name needs to be at least 2 characters.")
            is_valid = False

        if len(data['last_name']) <2:
            flash("Last name needs to be at least 2 characters.")
            is_valid = False

        if len(data['email']) <2:
            flash("Email field is required.")
            is_valid = False            
        elif not EMAIL_REGEX.match(data['email']): 
            flash("Invalid email address! Try again!")
            is_valid = False
        else:
            #check if the email provided is unique
            user_data = {
                'email':data['email']
            }
            potential_user = User.get_by_email(user_data)
            if potential_user:
                flash('Email already in the system. Use another email or log in.')
                is_valid = False

        if len(data['password']) <8:
            flash("Password needs to be at least 8 characters.")
            is_valid = False
        elif not data['password'] == data['confirm_password']:
            flash('Passwords must match.')
            is_valid = False

        return is_valid