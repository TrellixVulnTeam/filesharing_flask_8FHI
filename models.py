from __main__ import db
from datetime import datetime
#
# ORM models for flask_sqlalchemy extension generated tables 
# 
class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nickname = db.Column(db.String(120), index=True, unique=True)
	password = db.Column(db.String(255))
	## 1>n relationship to class File, allow file to backref user
	files = db.relationship('File',backref='user',lazy='dynamic')
	rank_id = db.Column(db.Integer, db.ForeignKey('rank.id'))
	mb_used = db.Column(db.Integer)

	########## uses flask_login extension
	@property
	def is_authenticated(self):
		return True
	@property
	def is_active(self):
		return True
	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self.id)

	def __repr__(self):
		return 'User %r' % (self.nickname)
	##########

class File(db.Model):
	id = db.Column(db.Integer(),primary_key=True)
	owner = db.Column(db.Integer(),db.ForeignKey('user.id'),index=True)
	name = db.Column(db.String(255),index=True)
	size = db.Column(db.Integer,index=True)
	fext = db.Column(db.String(20),index=True)
	datetime = db.Column(db.DateTime)
	public = db.Column(db.Boolean,default=False)
	public_key = db.Column(db.String(255),index=True)

	def __init__(self,owner=None,name=None,size=None,fext=None,public=None,public_key=None):
		self.datetime = datetime.utcnow()
		self.owner = owner
		self.name = name
		self.size = size
		self.fext = fext
		self.public = public
		self.public_key = public_key

class Rank(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(25))
	level = db.Column(db.Integer)
	mb_limit = db.Column(db.Integer)
	users = db.relationship('User', backref = 'rank', lazy='dynamic')




