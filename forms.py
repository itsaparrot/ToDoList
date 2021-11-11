from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired


class ToDoForm(FlaskForm):
    text = StringField("Write a reminder here: ", validators=[DataRequired()])
    submit = SubmitField("Add")


class RegisterForm(FlaskForm):
    name = StringField("Your Name:", validators=[DataRequired()])
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Create Account")


class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Sign In")
