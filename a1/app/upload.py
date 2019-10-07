from flask import render_template, request, url_for, redirect, flash, session
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from app import webapp
import boto3
import tempfile
from PIL import Image
import os
import tempfile

from config import S3_BUCKET
from app.utils import *

def allowed_file(filename):
    return filename.split('.')[1] in ['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF']

@webapp.route('/album')
def go_album():
    # Check whether the user is logged in
    username = session.get('username')
    if  username is None:
        flash('Please log in first')
        return redirect(url_for('login'))
    else:
        # Show all thumbnails of the users
        cnx = get_db()
        cursor = cnx.cursor()
        query = 'SELECT key2 from photos WHERE userID = %s'
        cursor.execute(query, (username,))
        # print(cursor.fetchone())
        thumbnails = [item[0] for item in cursor.fetchall()]
        urls = []
        for key in thumbnails:
            # Retrive images from S3
            s3 = boto3.client('s3')
            url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': key
                }
            )
            urls.append(url)
         
        return render_template('myalbum.html', urls=urls)

@webapp.route('/upload',methods=['GET'])
def upload_form():
    return render_template("upload.html")

@webapp.route('/upload_submit', methods=['POST'])
def upload():
    username = session.get('username')
    if not 'username': # check whether the user is logged in
        flash('Pleas log in first')
        return redirect(url_for('login'))

    file = request.files.get('uploadedfile')

    if file:
        filename = file.filename
        if filename == '':
            flash('Missing filename')
            return render_template("upload.html") 

        if not allowed_file(filename):
            flash('Only image files allowed')
            return render_template("upload.html") 
        else:  
            # Save to S3
            s3 = boto3.resource('s3')
            path = tempfile.mkdtemp()
            filepath = path + filename
            
            # Save the original photo
            file.save(filepath)
            key = username + '_' + filename
            with open(filepath, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=key, Body=tmp)

            ##################### TO DO ######################
            # 1. text detection                              #
            # 2. save the result and thumbnail of the result #                              #
            ##################################################
            cnx = get_db()
            cursor = cnx.cursor()
            query = '''INSERT INTO photos (userID, key2) VALUES (%s, %s)'''
            cursor.execute(query, (username, key))
            cnx.commit()


            flash('Photo Upload Success!')
            return redirect(url_for('go_album'))
    
    flash('No file selected')
    return render_template("upload.html")    
    


# @webapp.route('/upload', methods=['GET', 'POST'])
# def upload():
#     form = UploadForm()

#     if form.validate_on_submit():
#         f = form.photo.data
#         filename = form.file.data.filename
        
#         print(filename)
#         return redirect(url_for('go_album'))
#         # Save to S3
#         # s3 = boto3.resource('s3')
#         # s3.Object('ece1779testbucket', ).put(Body=open('/tmp/hello.txt', 'rb'))
#     print(form.errors)   
#     # return 'wrong uplaod'
#     return render_template('upload.html', form=form)