from app import webapp
from flask import render_template

@webapp.route('/')
def index():
    print('hello')
    return render_template('manager.html')