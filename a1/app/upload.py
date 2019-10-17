from flask import render_template, request, url_for, redirect, flash, session
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from app import webapp
import cv2
import os

from text_detection import detect_text
from app.utils import get_db, keynameFactory, normalName


def allowed_file(filename):
    return filename.split('.')[-1] in ['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF']


@webapp.route('/album')
def go_album():
    # Check whether the user is logged in
    username = session.get('username')
    if username is None:
        flash('Please log in first')
        return redirect(url_for('login'))
    else:
        # Show all thumbnails of the users
        cnx = get_db()
        cursor = cnx.cursor()
        query = 'SELECT key2 from photos WHERE userID = %s'
        cursor.execute(query, (username,))
        thumbnails = [item[0] for item in cursor.fetchall()]
        urls = []
        for key in thumbnails:
            normName = normalName(key)
            url = url_for('static', filename='uploads/'+key)
            urls.append([url, key, normName])
        return render_template('myalbum.html', urls=urls)


@webapp.route('/upload', methods=['GET'])
def upload_form():
    return render_template("upload.html")


@webapp.route('/upload_submit', methods=['POST'])
def upload():
    username = session.get('username')
    if not 'username': # check whether the user is logged in
        flash('Pleas log in first!', 'warning')
        return redirect(url_for('login'))
    file = request.files.get('uploadedfile')

    if file:
        filename = file.filename
        if filename == '':
            flash('Missing filename!', 'warning')
            return render_template("upload.html") 

        if not allowed_file(filename):
            flash('Only image files allowed!', 'warning')
            return render_template("upload.html") 
        else: 
            if os.fstat(file.fileno()).st_size > 50*1024*1024:
                # if os.path.getsize(file.path) > 1*1024:
                sizeError = "The file size is larger than limit."
                return render_template('upload.html', sizeError=sizeError)

            # keys generated here
            # (key0: original photo/key1: text-detected photo/key2: thumbnail)
            key = username + '_' + filename
            keys = keynameFactory(key)

            path = os.path.join(os.getcwd(), "app", "static", "uploads")
            img_org = os.path.join(path, keys[0])
            file.save(img_org)
          
            # Text detection
            img_detected = detect_text(img_org)
            img_thumb = cv2.resize(img_detected, None, fx=0.3, fy=0.3)

            # Save the detected photos to hard drive
            cv2.imwrite(os.path.join(path, keys[1]), img_detected)
            cv2.imwrite(os.path.join(path, keys[2]), img_thumb)
            
            # Write into DB
            cnx = get_db()
            cursor = cnx.cursor()
            query = '''INSERT INTO photos (userID, key0, key1, key2) VALUES (%s, %s, %s, %s)'''
            cursor.execute(query, (username, keys[0], keys[1], keys[2]))
            cnx.commit()

            flash('Photo Upload Success!', 'success')
            return redirect(url_for('go_album'))
    
    flash('No file selected!', 'warning')
    return render_template("upload.html")    
