import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql://root:@127.0.0.1/flask_project'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')
WTF_CSRF_ENABLED = True
SECRET_KEY = 'fUhjgXQfKmoWYsrsV0BiceNvrYKJwlKCAdSCQ42F8pGNGjJGtg0VUdXwHudvesp'
