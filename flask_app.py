
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.uploads_path = os.path.join(app.root_path,'uploads')
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)

from blueprints.site.views import site

app.register_blueprint(site)

if __name__ == '__main__':
	app.run()
	