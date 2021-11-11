from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField


class ToDoForm(FlaskForm):
    text = CKEditorField("Write a reminder here: ", validators=[DataRequired()])
    submit = SubmitField("Ok")
