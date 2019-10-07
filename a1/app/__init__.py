from flask import Flask
from datetime import timedelta
from config import *

webapp = Flask(__name__)
webapp.config["SECRET_KEY"] = SECRET_KEY   
webapp.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(hours=24)

from app import login
from app import upload