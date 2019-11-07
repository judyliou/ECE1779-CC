from flask import Flask
from datetime import timedelta

from config import SECRET_KEY

webapp = Flask(__name__)
webapp.config["SECRET_KEY"] = SECRET_KEY
webapp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
webapp.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

from app import worker
from app import manager
