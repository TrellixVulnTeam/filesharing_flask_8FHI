from flask import Blueprint
from __main__ import app,db,lm
from flask import send_from_directory,render_template,request,session,url_for,g,redirect
from flask_login import login_user,logout_user,current_user,login_required
from werkzeug.utils import secure_filename
from models import *
from blueprints.site.forms import FormUserLogin,FormFileUpload,FormUserDel,FormFileSearch
from argon2 import *
from sqlalchemy import desc
from uuid import uuid4
from multi_key_dict import multi_key_dict
import time,os,re,datetime


site = Blueprint(
	'site',
	__name__,
	template_folder='templates',
)

## User views
##
@site.route('/')
@site.route('/index/')
@login_required
def index():
	return render_template("site/main.html",form_file_upload=FormFileUpload())

@site.route('/fileBrowser/<int:page>/',methods=['POST','GET'], defaults={'view':'all'})
@site.route('/fileBrowser/<view>/', methods=['POST','GET'], defaults={'page':1})
@site.route('/fileBrowser/<view>/<int:page>/', methods=['POST','GET'])
@site.route('/fileBrowser/',methods=['POST','GET'], defaults={'view':'all','page':1})

@login_required
def fileBrowser(view,page):
	file_extensions = multi_key_dict()
	file_extensions['.mp3','.flac'] = 'audio'
	file_extensions['.mp4','.mkv','.mpeg','.wmv'] = 'videos'
	file_extensions['.png','.jpg','.jpeg'] = 'photos'
	file_types = {v:k for k,v in file_extensions.items()}
	file_type_html = {
		'audio': """
		 <audio controls style="display:block;">
  	      <source src="{0}" type="audio/webm">
         </audio>
    	""",

    	'videos':"""
		 <video controls class="FIThumb_content">
	  	  <source src="{0}" type="video/webm">
		  Your browser does not support the video tag.
		 </video>
		""",

		'photos':"""
		 <img src="{0}" class="FIThumb_content">
		""",

		'default': """<img class="FIThumb_content" src="/static/images/unknown.png">""",
	}
	form = FormFileSearch(view='search')
	form.search_view.choices = [(k,k.title()) for k in file_types]
	form.search_view.choices.append(tuple(['all','All']))

	if form.validate_on_submit():
		session['search'] = form.search.data
		session['search_view'] = form.search_view.data
		return redirect(url_for('site.fileBrowser',view='search',page=1))
	if view != 'all' and view in file_types:
		pagination = g.user.files.filter(File.fext.in_(file_types[view])).paginate(page,10)
	elif view == 'search':
		baseq = g.user.files.filter(File.name.contains(session['search']))
		if session['search_view'] == 'all':
			pagination = baseq.order_by(desc(File.datetime)).paginate(page,10)
		else:
			pagination = baseq.filter(File.fext.in_(file_types[session['search_view']])).paginate(page,10)
	else:
		pagination = g.user.files.order_by(desc(File.datetime)).paginate(page,10)
	files = pagination.items

	return render_template(
		"site/filebrowser.html",
		form_file_upload= FormFileUpload(),
		form_file_search = form,
		files= files,
		file_extensions = file_extensions,
		file_type_html = file_type_html,
		file_types = file_types,
		pagination = pagination,
		view = view
	)

@site.route('/zolder/')
@login_required
def zolder():
	if g.user.admin == True:
		users = User.query.all()
		return render_template(
			"site/admin.html",
			users= users,
			form_user_login = FormUserLogin(),
			form_file_upload = FormFileUpload(),
			form_user_del = FormUserDel()
		)
	else:
		return redirect(request.referrer)
#
#	action views
#
@site.route('/delUserFile/<int:fileid>/')
@login_required
def delUserFile(fileid):
	file = File.query.get(fileid)
	if file:
		if file.user.id == g.user.id:	
			db.session.delete(file)
			db.session.commit()
			path = os.path.join(g.user.path,file.name)
			if os.path.isfile(path):
				os.remove(path)
	return redirect(request.referrer)

@site.route('/dwnUserFile/<int:fileid>/')
@login_required
def dwnUserFile(fileid):
	file = File.query.get(fileid)
	if file and file.user.id == g.user.id:
		return send_from_directory(
			g.user.path,
			file.public_key + file.name,
			as_attachment = True,
			attachment_filename = file.name
		)
	return'failed'

@site.route('/pubFile/<int:fileid>/')
@login_required
def pubFile(fileid=None):
	file = File.query.get(fileid)
	if file and file.user.id == g.user.id:
		file.public = True if file.public == False else False
		db.session.commit()
	return redirect(request.referrer)

@site.route('/dwnPublicFile/<filekey>/<int:fileid>/')
def dwnPublicFile(filekey,fileid):
	file = File.query.get(fileid)
	if file and file.public == True and filekey == file.public_key:
		userTarget = User.query.get(file.owner)
		path = os.path.join(site.uploads_path,userTarget.nickname)
		return send_from_directory(
			path,file.public_key + file.name,
			attachment_filename = file.name,
			as_attachment = True
		)
	return'failed'

@site.route('/forms/delWebbUser/<int:userid>/')
@login_required
def delWebbUser(userid=None):
	userTarget = User.query.get(userid)
	if userTarget and g.user.admin == True:
		db.session.delete(userTarget)
		db.session.commit()
		os.removedirs(os.path.join(site.uploads_path,userTarget.nickname))
	return redirect(request.referrer)
#
#	Form Handles
#
@site.route('/forms/addWebbUser/',methods=['POST'])
@login_required
def addWebbUser():
	form = FormUserLogin()
	if form.validate_on_submit() and g.user.admin == True:
		ph =  PasswordHasher()
		hash = ph.hash(form.password.data)
		q = User(nickname=form.username.data, password=hash)
		db.session.add(q)
		db.session.commit()
		os.makedirs(os.path.join(site.uploads_path,q.nickname))
	return redirect(request.referrer)

@site.route('/forms/uploadFile/',methods=['POST'])
@login_required
def uploadFile():
	form = FormFileUpload()
	if form.validate_on_submit():
		public_key = str(uuid4())
		filename =  secure_filename(form.upload.data.filename)
		form.upload.data.save(os.path.join(g.user.path,public_key+filename)) 
		search = re.compile(r".*(\..*)").match(filename)
		fext = search.group(1) if search else 'unknown'
		q = File(
			owner = g.user.id,
			name = filename,
			size = os.path.getsize(os.path.join(g.user.path,public_key+filename)),
			fext = fext,
			public_key = public_key
		)
		db.session.add(q)
		db.session.commit()
	else:
		filename = None
	return redirect(request.referrer)

#
#	login/logout views
#
@site.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect(url_for('site.login'))

@site.route('/login/',methods=['POST','GET'])
def login():
	if g.user is not None:
		if g.user.is_authenticated:
			return redirect(url_for('site.index'))
	form = FormUserLogin()
	if form.validate_on_submit():
		ph =  PasswordHasher()
		hash = ph.hash(form.password.data)
		user = User.query.filter(User.nickname.ilike("%{}%".format(form.username.data))).first()
		if user:
			try:
				ph.verify(user.password,form.password.data)
				login_user(user)
				return redirect(url_for('site.index'))
			except:
				pass
	return render_template("site/login.html", form_user_login=form)

#
#	Decorators for modifying app/loginmanager behaviour
#
@site.before_request
def before_request():
    g.user = current_user
    if hasattr(current_user,'nickname'):
    	g.user.path = os.path.join(app.uploads_path, current_user.nickname)
    return

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@lm.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('site.login'))



