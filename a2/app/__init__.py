from flask import Flask
from datetime import timedelta

from config import SECRET_KEY
from app import awsUtils

def createApp():
    webapp = Flask(__name__)
    print("Please wait for initializing...")
    awsSuite = awsUtils.AWSSuite()
    workerNum = awsSuite.getWorkersNum()
    if workerNum == 0:
        response = awsSuite.growOneWorker()
    else: 
        response = awsSuite.shrinkWorkers(workerNum - 1)
    print("Initialized done")
    return webapp
webapp = createApp()

webapp.config["SECRET_KEY"] = SECRET_KEY
webapp.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
webapp.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

from app import manager
from app import worker