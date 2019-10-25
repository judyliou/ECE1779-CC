from flask import render_template
from app import webapp

@webapp.route("/viewWorker/<index>", methods=['GET'])
def viewWorker(index):
    print(index)
    return render_template("workerInfo.html", worker=index)