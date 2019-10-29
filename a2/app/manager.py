from app import webapp
from flask import render_template
from app import awsUtils
from flask_bootstrap import Bootstrap
import json

bootstrap = Bootstrap(webapp)

@webapp.route('/')
def index():
    print('hello')
    instances = awsUtils.fetchAllInstances()
    return render_template('manager.html', instances=instances)

@webapp.route('/add', methods=['GET', 'POST'])
def add():
    print("add")
    if awsUtils.growOneWorker():
        return json.dumps({"msg": "success"})
    else:
        return json.dumps({"msg": "fail"})
