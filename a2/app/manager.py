from app import webapp
from flask import render_template
from app import awsUtils
from flask_bootstrap import Bootstrap
import json

bootstrap = Bootstrap(webapp)
awsSuite = awsUtils.AWSSuite()

@webapp.route('/manager')
def view_manager():
    print('hello')
    instances = awsSuite.getWorkingInstances()
    # instances = awsSuite.getAllWorkers()
    # instances = awsSuite.getUnusedInstances()
    for instance in instances:
        print('get one')
    return render_template('manager.html', instances=instances)

@webapp.route('/add', methods=['GET', 'POST'])
def add():
    print("add")
    if awsSuite.growOneWorker():
        return json.dumps({"msg": "success"})
    else:
        return json.dumps({"msg": "fail"})

@webapp.route('/shrink', methods=['GET', 'POST'])
def shrink():
    print("shrink")
    if awsSuite.shrinkOneWorker():
        return json.dumps({"msg": "success"})
    else:
        return json.dumps({"msg": "fail"})

@webapp.route('/stop', methods=['GET', 'POST'])
def stop():
    print("stop")
    return True