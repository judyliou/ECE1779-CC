from flask import render_template, request, url_for, redirect, flash, session
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from app import webapp
import cv2
import os

import boto3
import tempfile
from PIL import Image
from config import S3_BUCKET

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
            s3 = boto3.client('s3')
            normName = normalName(key)
            user_len = len(session.get('username'))
            normName = normName[user_len+1: ]
            # url = url_for('static', filename='uploads/'+key)
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': key
                }
            )
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
	    
	    
            s3 = boto3.resource('s3')
            path = tempfile.mkdtemp()

          # path = os.path.join(os.getcwd(), "app", "static", "uploads")
            img_org = os.path.join(path, keys[0])
            file.save(img_org)
            with open(img_org, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[0], Body=tmp)
          
            # Text detection
            img_detected = detect_text(img_org)
            img_de = os.path.join(path, keys[1])
            file.save(img_de)
            with open(img_de, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[1], Body=tmp)

            img_thumb = cv2.resize(img_detected, None, fx=0.3, fy=0.3)
            img_th = os.path.join(path, keys[2])
            file.save(img_th)
            with open(img_th, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[2], Body=tmp)

            # Save the detected photos to hard drive
            # cv2.imwrite(os.path.join(path, keys[1]), img_detected)
            # cv2.imwrite(os.path.join(path, keys[2]), img_thumb)
            
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
