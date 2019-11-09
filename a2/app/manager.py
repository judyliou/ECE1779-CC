from app import webapp
from flask import render_template, request, redirect, url_for
from app import awsUtils
from app.config import awsConfig
from flask_bootstrap import Bootstrap
import json

bootstrap = Bootstrap(webapp)
awsSuite = awsUtils.AWSSuite()

@webapp.route('/')
def view_manager():
    instances = awsSuite.getWorkingInstances()
    print("cur worker #:", len(instances))
    if len(instances) != 1:
        return render_template('initialize.html')
    print('enough insts')
    instances = awsSuite.getWorkingInstances()
    # instances = awsSuite.getAllWorkers()
    # instances = awsSuite.getUnusedInstances()
    return render_template('manager.html', instances=instances)

@webapp.route('/initialize', methods=['GET', 'POST'])
def initialize():
    print('initializing...')
    awsSuite.terminateAllWorkers()
    response = awsSuite.growOneWorker()
    if response:
        print('finish initializing')
    return json.dumps({'success': 1, "msg": 'Success'})

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
    response = awsSuite.terminateAllWorkers()
    awsSuite.stopManager()
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
    ratio, thresholdHigh, thresholdLow = awsSuite.fetchConfig()
    return render_template("/config.html", ratio=ratio, thresholdHigh=thresholdHigh, thresholdLow=thresholdLow)

@webapp.route('/configAutoScaling', methods=['GET', 'POST'])
def configAutoScaling():
    ratio = request.form['ratio']
    thresholdHigh = request.form['thresholdHigh']
    thresholdLow = request.form['thresholdLow']
    error = False
    ratioMsg = ""
    thMsg = ""
    tlMsg = ""
    if not ratio.isdigit() or int(ratio) <= 0 or int(ratio) > 5:
        ratioMsg = "Please input right ratio"
        error = True
    if not thresholdHigh.isdigit() or int(thresholdHigh) < 0 or int(thresholdHigh) > 100:
        thMsg = "Please input right thresholdHigh"
        error = True
    if not thresholdLow.isdigit() or int(thresholdLow) < 0 or int(thresholdLow) > 100:
        tlMsg = "Please input right thresholdLow"
        error = True
    if error is False:
        awsSuite.changeConfig(int(ratio), int(thresholdHigh), int(thresholdLow))
        return redirect(url_for('view_manager'))
    else:
        return render_template("/config.html", ratioMsg=ratioMsg, thMsg=thMsg, tlMsg=tlMsg)