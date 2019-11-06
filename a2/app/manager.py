from app import webapp
from flask import render_template, request
from app import awsUtils
from app.config import awsConfig
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
    return render_template('manager.html', instances=instances)

@webapp.route('/add', methods=['GET', 'POST'])
def add():
    response = awsSuite.growOneWorker()
    if response == awsConfig.REGISTERED:
        return json.dumps({'success': 1, "msg": 'Success'})
    elif response == awsConfig.MAX_WORKERS:
        return json.dumps({'success': 0, "msg": 'Instances exceed 10'})
    elif response == awsConfig.CREATE_FAILED:
        return json.dumps({'success': 0, "msg": 'Failed to create an instance'})
    else:
        return json.dumps({'success': 0, "msg": 'Network error'})

@webapp.route('/shrink', methods=['GET', 'POST'])
def shrink():
    response = awsSuite.shrinkOneWorker()
    if response == awsConfig.DEREGISTERED:
        return json.dumps({'success': 1, "msg": 'Success'})
    elif response == awsConfig.NO_WORKER:
        return json.dumps({'success': 0, "msg": 'No worker to shrink'})
    else:
        return json.dumps({'success': 0, "msg": 'Network error'})

@webapp.route('/stop', methods=['GET', 'POST'])
def stop():
    response = awsSuite.stopAllInstances()
    if response == awsConfig.ALL_STOPED:
        msg = "All instances successfully stopped"
    else:
        msg = "Some instances not successfully stopped due to network error"
    return render_template('stopped.html', msg=msg)

@webapp.route('/delete', methods=['GET', 'POST'])
def delete():
    response = awsSuite.deleteAll()
    return json.dumps({'success': 1, "msg": 'Delete successfully'})

@webapp.route('/config', methods=['GET', 'POST'])
def config():
    return render_template("/config.html")

@webapp.route('/configAutoScaling', methods=['GET', 'POST'])
def configAutoScaling():
    ratio = request.form['ratio']
    thresholdHigh = request.form['thresholdHigh']
    thresholdLow = request.form['thresholdLow']
    ratioMsg = ""
    thMsg = ""
    tlMsg = ""

    return render_template("/config.html", ratioMsg=ratioMsg, thMsg=thMsg, tlMsg=tlMsg)