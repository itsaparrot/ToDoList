from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor

from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user

import os

from forms import ToDoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SQL_ALCHEMY_KEY']
ckeditor = CKEditor(app)
Bootstrap(app)

# connect to database, use postgresQL when available
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
db = SQLAlchemy(app)


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
    # tracking user id to call todos items later
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    todo_author = relationship("User", back_populates="todo")


# db.create_all()
temp_todo_list = []


@app.route('/', methods=['GET', 'POST'])
def home():
    todo_lists = ToDo.query.all()
    todo_form = ToDoForm()
    print(temp_todo_list)
    if todo_form.validate_on_submit():
        item = request.form.get('text')
        temp_todo_list.append(item)
        return redirect(url_for('home'))

    return render_template('index.html', todos=todo_lists, temp_todo=temp_todo_list, form=todo_form)


if __name__ == '__main__':
    app.run(debug=True)
