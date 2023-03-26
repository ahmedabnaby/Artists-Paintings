from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.user_model import User
from flask_app.models.painting_model import Painting 
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/create_link')
def create_link():
    if 'user_id' not in session:
        return redirect('/')
    else:
        return redirect('/create')

#--------------------------------------------------------------------

@app.route('/create')
def create():
    data = {
        'id': session['user_id']
    }
    user = User.get_by_id(data)
    return render_template('create.html', user = user)

#--------------------------------------------------------------------

@app.route('/new', methods = ['POST'])
def new():
    if 'user_id' not in session:
        return redirect('/')

    if not Painting.validate_painting(request.form):
        return redirect('/create')

    data = {
        'title': request.form['title'],
        'description': request.form['description'],
        'price': request.form['price'],
        'quantity': request.form['quantity'],
        'user_id': session['user_id']
    }

    Painting.create(data)
    
    return redirect('/dashboard')

#--------------------------------------------------------------------
@app.route('/show/<int:painting_id>')
def show(painting_id):
    user_data = {
        'id' : session['user_id']
    }

    data = {
        'id' : painting_id
    }
    user = User.get_by_id(user_data)
    painting = Painting.show_one_painting(data)

    num_purchased = Painting.get_how_many_times_painting_has_been_purchased(data)


    return render_template("show.html", painting=painting, user=user, num_purchased = num_purchased)

#--------------------------------------------------------------------
@app.route('/purchase/<int:painting_id>')
def purchase(painting_id):
    data = {
        'user_id':session['user_id'],
        'painting_id':painting_id
    }

    Painting.insert_into_join_table(data)
    return redirect('/dashboard')

#--------------------------------------------------------------------


@app.route('/edit/<int:painting_id>')
def link_to_edit(painting_id):
    data = {
        'id': painting_id
    }

    user_data = {
        'id': session['user_id']
    }

    user = User.get_by_id(user_data)
    painting = Painting.show_one_painting(data)

    return render_template('update.html', painting = painting, user=user)

# #--------------------------------------------------------------------

@app.route('/update/<int:painting_id>', methods = ['POST'])
def update(painting_id):
    if 'user_id' not in session:
        return redirect('/')
    if not Painting.validate_painting(request.form):
        return redirect(f'/edit/{painting_id}')
    
    data = {
        'id':painting_id,
        'title':request.form['title'],
        'description':request.form['description'],
        'price':request.form['price'],
        'quantity':request.form['quantity'],
        'user_id':session['user_id']
    }

    Painting.update(data)
    return redirect('/dashboard')

# #--------------------------------------------------------------------

@app.route('/delete/<int:painting_id>')
def delete(painting_id):
    data = {
        'id' : painting_id
    }

    Painting.delete(data)
    return redirect ('/dashboard')
