from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user_model
from flask_app import app
from flask import flash
import re

class Painting:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.price = data['price']
        self.quantity = data['quantity']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def create(cls, data):
        query = """
        INSERT INTO paintings (title, description, price, quantity, user_id)
        VALUES(%(title)s, %(description)s, %(price)s, %(quantity)s, %(user_id)s);
        """
        return connectToMySQL('paintings').query_db(query,data)

    @classmethod
    def delete(cls,data):
        query = """
        DELETE FROM paintings
        WHERE id = %(id)s;
        """
        return connectToMySQL('paintings').query_db(query, data)

    @classmethod
    def show_one_painting(cls, data):
        query = """
        SELECT * 
        FROM paintings
        JOIN users
        ON users.id = paintings.user_id
        WHERE paintings.id = %(id)s;
        """
        results = connectToMySQL('paintings').query_db(query, data)
        if len(results)<1:
            return False
        this_painting = cls(results[0])
        user_data = {
            **results[0],
            'id':results[0]['users.id'],
            'created_at': results[0]['users.created_at'],
            'updated_at': results[0]['users.updated_at']
        }

        this_user = user_model.User(user_data)
        this_painting.creator = this_user
        return this_painting

    @classmethod
    def update(cls, data):
        query = """
        UPDATE paintings
        SET title=%(title)s, description=%(description)s, price=%(price)s, quantity=%(quantity)s, user_id=%(user_id)s
        WHERE id = %(id)s; 
        """
        return connectToMySQL('paintings').query_db(query, data)

    @classmethod
    def get_all_paintings_with_users(cls):
        query = """
        SELECT * 
        FROM paintings
        JOIN users
        ON users.id = paintings.user_id;
        """
        results = connectToMySQL('paintings').query_db(query)
        all_paintings = []
        if results:
            for row in results:
                this_painting = cls(row)
                user_data = {
                    **row,
                    'id':row['users.id'],
                    'created_at':row['users.created_at'],
                    'updated_at':row['users.updated_at']
                }
                this_user = user_model.User(user_data)
                this_painting.creator = this_user
                all_paintings.append(this_painting)
        return all_paintings

    @classmethod
    def insert_into_join_table(cls, data):
        query = """
        INSERT INTO user_has_painting (user_id, painting_id)
        VALUES(%(user_id)s, %(painting_id)s);
        """
        return connectToMySQL('paintings').query_db(query,data)

    @classmethod
    def get_how_many_times_painting_has_been_purchased(cls,data):
        query = """
        SELECT *
        FROM paintings
        JOIN user_has_painting
        ON paintings.id = user_has_painting.painting_id
        WHERE paintings.id = %(id)s;
        """
        results = connectToMySQL('paintings').query_db(query,data)
        return len(results)

    @staticmethod
    def validate_painting(data):
        is_valid = True

        if len(data['title']) <1:
            flash("Title is required")
            is_valid = False
        elif len(data['title']) <2:
            flash("Title must be > 2 characters long")
            is_valid = False

        if len(data['description']) <1:
            flash("Description is required")
            is_valid = False
        elif len(data['description']) <10:
            flash("Description must be > 10 characters long")
            is_valid = False
        
        if not (data['price']):
            flash("Price required")
            is_valid = False
        elif int((data['price'])) < 1:
            flash("Price must be greater than 0")
            is_valid = False
        
        if not (data['quantity']):
            flash("Quantity required")
            is_valid = False
        elif int((data['quantity'])) < 1:
            flash("Quantity must be greater than 0")
            is_valid = False

        return is_valid
