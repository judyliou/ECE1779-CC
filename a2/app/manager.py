from app import webapp
from flask import render_template
from app import awsUtils
from app.config import awsConfig
from flask_bootstrap import Bootstrap
import json

bootstrap = Bootstrap(webapp)
awsSuite = awsUtils.AWSSuite()

@webapp.route('/')
def index():
    print('hello')
    instances = awsSuite.getWorkingInstances()
    # instances = awsSuite.getAllWorkers()
    # instances = awsSuite.getUnusedInstances()
    return render_template('manager.html', instances=instances)

@webapp.route('/add', methods=['GET', 'POST'])
def add():
    response = awsSuite.growOneWorker()
    if response == awsConfig.REGISTERED:
        return json.dumps({'success': 1, "msg": 'success'})
    elif response == awsConfig.MAX_WORKERS:
        return json.dumps({'success': 0, "msg": 'instances exceed 10'})
    elif response == awsConfig.CREATE_FAILED:
        return json.dumps({'success': 0, "msg": 'failed to create an instance'})
    else:
        return json.dumps({'success': 0, "msg": 'network error'})

@webapp.route('/shrink', methods=['GET', 'POST'])
def shrink():
    response = awsSuite.shrinkOneWorker()
    # response = awsSuite.shrinkWorkers(3)
    # return json.dumps({'success': 0, "msg": str(response)})
    if response == awsConfig.DEREGISTERED:
        return json.dumps({'success': 1, "msg": 'success'})
    elif response == awsConfig.NO_WORKER:
        return json.dumps({'success': 0, "msg": 'no worker to shrink'})
    else:
        return json.dumps({'success': 0, "msg": 'network error'})

@webapp.route('/stop', methods=['GET', 'POST'])
def stop():
    response = awsSuite.stopAllInstances()
    if response == awsConfig.ALL_STOPED:
        msg = "All instances successfully stopped"
    else:
        msg = "Some instances not successfully stopped due to network error"
    return render_template('stopped.html', msg=msg)
    # return json.dumps({'success': 1, 'msg': msg})
    # return json.dumps(dict(redirect='stopped.html'))
