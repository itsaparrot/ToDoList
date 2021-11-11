import flask
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_manager

import os

from forms import ToDoForm, RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SQL_ALCHEMY_KEY']
Bootstrap(app)

# connect to database, use postgresQL when available
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
db = SQLAlchemy(app)

# manages keeping user signed in
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# each user has many todos mapped to it
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))

    todo = relationship("ToDo", back_populates="todo_author")


# items are mapped as many todos to one user
class ToDo(db.Model):
    __tablename__ = 'todo'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(150))
    # tracking user id
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    todo_author = relationship("User", back_populates="todo")


# db.create_all()
temp_todo_list = []


@app.route('/', methods=['GET', 'POST'])
def home():
    todo_form = ToDoForm()
    saved_tasks = []
    if current_user.is_authenticated:
        if ToDo.query.filter_by(author_id=current_user.id).first():
            user_saved_tasks = ToDo.query.filter_by(author_id=current_user.id).all()
            for todo_object in user_saved_tasks:
                saved_tasks.append(todo_object)
    if todo_form.validate_on_submit():
        item = request.form.get('text')
        temp_todo_list.append(item)
        return redirect(url_for('home'))

    return render_template('index.html', temp_todo=temp_todo_list, todos=saved_tasks, form=todo_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # check if email is already in use
        if User.query.filter_by(email=request.form.get('email')).first():
            flask.flash('email already registered')
            return redirect(url_for('register'))
        # create salted and hashed password
        salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        # create new user, commit changes, then log them in
        new_user = User(email=form.email.data, password=salted_password, name=form.name.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # checks if user exits, sends warning
        if not user:
            flask.flash('User does not exist')
            return redirect(url_for('login'))
        # checks if password is correct
        elif not check_password_hash(user.password, form.password.data):
            flask.flash('That password is not correct')
            return redirect(url_for('login'))
        # if all good, login user, redirect to homepage
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/save-list', methods=['GET', 'POST'])
def save_list():
    if not current_user.is_authenticated:
        flask.flash('You must be logged in to save lists')
        return redirect(url_for('home'))
    elif temp_todo_list != '':
        tasks_to_add = []
        for text in temp_todo_list:
            tasks_to_add.append(ToDo(todo_author=current_user, text=text))
        for task in tasks_to_add:
            db.session.add(task)
        db.session.commit()
        temp_todo_list.clear()
        return redirect(url_for('home'))
    else:
        flask.flash('Your list is empty!')
        return redirect(url_for('home'))
    return redirect(url_for('home'))


# clears current temp list
@app.route('/new-list')
def clear_list():
    temp_todo_list.clear()
    if current_user.is_authenticated:
        all_saved_todo = ToDo.query.filter_by(author_id=current_user.id).all()
        for todo in all_saved_todo:
            db.session.delete(todo)
        db.session.commit()
    return redirect(url_for('home'))


# handles deleting single tasks
@app.route('/delete-task')
def delete_task():
    task_index = request.args.get('task_index')
    temp_todo_list.pop(int(task_index))
    return redirect(url_for('home'))


@app.route('/delete-saved-task')
def delete_saved_task():
    print('delet saved task in')
    task_id = request.args.get('task_id')
    print(task_id)
    task_to_delete = ToDo.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
