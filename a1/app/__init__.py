from flask import Flask
from datetime import timedelta

from a1.config import SECRET_KEY

webapp = Flask(__name__)
webapp.config["SECRET_KEY"] = SECRET_KEY
webapp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

from a1.app import login
from a1.app import upload
from a1.app import viewImage
from a1.app.api import blueprint as api

webapp.register_blueprint(api, url_prefix='/api')
