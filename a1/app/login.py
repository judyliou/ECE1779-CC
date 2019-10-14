from flask import render_template, request, url_for, redirect, flash, session
from flask_bootstrap import Bootstrap

from a1.app.forms import RegisterForm, LoginForm
from a1.app.utils import *

bootstrap = Bootstrap(webapp)


####### TO DO #######
# - hash password


@webapp.route('/')
@webapp.route('/index')
def index():
    is_login = False
    username = ""
    if session.get('username') is not None:
        is_login = True
        username = session.get('username')
    return render_template('base.html', is_login=is_login, username=username)  ##### change to main page


@webapp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    username = request.form.get('username')
    password = request.form.get('password')

    if form.reset.data:  # if click "Reset"
        return redirect(url_for('register'))

    if form.validate_on_submit():
        # 1. Connect to DB
        # 2. Check username is used or not
        # 3. Insert to DB
        cnx = get_db()
        cursor = cnx.cursor()

        encPwd = encryptString(password)

        query = '''SELECT * FROM users WHERE userID = %s'''
        cursor.execute(query, (username,))
        if cursor.fetchone() is not None:
            flash('The username is used.', 'warning')
            return redirect(url_for('register'))  # not sure
        else:
            query = '''INSERT INTO users (userID, password) VALUES (%s, %s)'''
            cursor.execute(query, (username, encPwd))
            cnx.commit()
            flash('Registration Success! Please login.', 'success')
            return redirect(url_for('login'))
            # return render_template('/uploading.html')
    return render_template('register.html', form=form)


@webapp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    username = request.form.get('username')
    password = request.form.get('password')

    if form.validate_on_submit():
        # 1. Connect to DB
        # 2. Query username
        # 3. Check whether exist and password
        cnx = get_db()
        cursor = cnx.cursor()

        encPwd = encryptString(password)

        query = '''SELECT * FROM users WHERE userID = %s'''
        cursor.execute(query, (username,))
        pwd_db = cursor.fetchone()[1]
        if pwd_db is None:
            flash('Invalid username. Try again or create a new account.', 'warning')
            return redirect(url_for('login'))
        else:
            if pwd_db != encPwd:
                flash('Wrong password.', 'warning')
                return redirect(url_for('login'))
            else:
                flash('Login Success!', 'success')
                # session.permanent = True
                session['username'] = username
                return redirect(url_for('index'))
                # return redirect(url_for('index'))
    return render_template("login.html", form=form)


@webapp.route('/logout')
def logout():
    # session.pop('username', None)
    session.clear()
    flash('You were logged out')
    return redirect(url_for('index'))
