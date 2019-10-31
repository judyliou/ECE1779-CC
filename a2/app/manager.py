from app import webapp
from flask import render_template

@webapp.route('/manager')
def view_manager():
    print('hello')
    return render_template('manager.html')