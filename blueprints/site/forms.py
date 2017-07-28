#!/usr/bin/python3
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, HiddenField, FieldList, FormField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired

class FormUserLogin(FlaskForm):
	username = StringField('username', validators=[DataRequired()])
	password = StringField('password', validators=[DataRequired()])

class FormFileUpload(FlaskForm):
	upload = FileField(validators=[FileRequired()])

class FormUserDel(FlaskForm):
	id = HiddenField('id')

class FormFileSearch(FlaskForm):
	search = StringField('search', validators=[DataRequired()])
	search_view = SelectField('all')
	view = HiddenField('view')