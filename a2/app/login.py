from flask import render_template, request, url_for, redirect, flash, session
from flask_bootstrap import Bootstrap

from app.forms import RegisterForm, LoginForm
from app.utils import *

bootstrap = Bootstrap(webapp)



@webapp.route('/')
@webapp.route('/index')
def index():
    is_login = False
    username = ""
    if session.get('username') is not None:
        is_login = True
        username = session.get('username')
    return render_template('base.html', is_login=is_login, username=username) 


@webapp.route('/register', methods=['GET', 'POST'])
def register():
    """ Go to the register page.

    After the user submit the register form (username, password and confirmed
    confirmed password included), the browser side invalidate all inputs and 
    check whether username exist in database or not. If not, insert the user 
    information into database ('users' table), and jump to login page; otherwise,
    falsh a warning and ask the user to register again.
    
    """
    put_http_metric(session['worker_id'])
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

        # here salt is created
        salt = randomString(12)
        encPwd = encryptString(password + salt)

        query = '''SELECT * FROM users WHERE userID = %s'''
        cursor.execute(query, (username,))
        if cursor.fetchone() is not None:
            flash('The username is used.', 'warning')
            return redirect(url_for('register'))  # not sure
        else:
            query = '''INSERT INTO users (userID, password, salt) VALUES (%s, %s, %s)'''
            cursor.execute(query, (username, encPwd, salt))
            cnx.commit()
            flash('Registration Success! Please login.', 'success')
            return redirect(url_for('login'))
            # return render_template('/uploading.html')
    return render_template('register.html', form=form)


@webapp.route('/login', methods=['GET', 'POST'])
def login():
    """ Go to the login page.
    
    After the client post the user information (username and password), connect 
    to database to check whether the username exists and match with password.
    
    If both username and password are valid, add username to the session and 
    jump to homepage; otherwise, falsh a warning and ask to insert username and 
    password again.

    """
    put_http_metric(session['worker_id'])
    form = LoginForm()
    username = request.form.get('username')
    password = request.form.get('password')

    if form.validate_on_submit():
        # 1. Connect to DB
        # 2. Query username
        # 3. Check whether exist and password
        cnx = get_db()
        cursor = cnx.cursor()

        query = '''SELECT * FROM users WHERE userID = %s'''
        cursor.execute(query, (username,))
        user_result = cursor.fetchone()
        if user_result is None:
            flash('Invalid username! Try again or create a new account.', 'warning')
            return redirect(url_for('login'))
        else:
            pwd_db = user_result[1]
            salt = user_result[2]
            encPwd = encryptString(password + salt)
            if pwd_db != encPwd:
                flash('Wrong password!', 'warning')
                return redirect(url_for('login'))
            else:
                flash('Login Success!', 'success')
                session.permanent = True
                session['username'] = username
                return redirect(url_for('index'))
    return render_template("login.html", form=form)


@webapp.route('/logout')
def logout():
    session.clear()
    flash('You were logged out', 'success')
    return redirect(url_for('index'))
