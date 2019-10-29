import os
import tempfile

from flask import request, jsonify, Response, make_response
from flask import Blueprint

from app import webapp
import boto3
from config import S3_BUCKET

import json
import cv2
from text_detection import detect_text

from app.upload import allowed_file
from app.utils import *
 

blueprint = Blueprint('api', __name__)
@blueprint.route('/register', methods=['POST'])
def register():
    username = str(request.form.get('username'))
    password = str(request.form.get('password'))

    # username too long
    # need to figure out which status respond to which situation
    if len(username) > 100:
        return make_response(json.loads('{ "success": "false", "error": \"username is too long\" }'), 400)
    elif username == "None" or len(username) == 0:
        return make_response(json.loads('{ "success": "false", "error": \"username is needed\" }'), 400)

    cnx = get_db()
    cursor = cnx.cursor()

    query = '''SELECT * FROM users WHERE userID = %s'''
    cursor.execute(query, (username,))
    if cursor.fetchone() is not None:
        # some http response
        return make_response(json.loads('{ "success": "false", "error": \"user already existed\" }'), 400)
    else:
        # here salt is created
        salt = randomString(12)
        encPwd = encryptString(password + salt)
        query = '''INSERT INTO users (userID, password, salt) VALUES (%s, %s, %s)'''
        cursor.execute(query, (username, encPwd, salt, ))
        cnx.commit()
        # 201
        return make_response(json.loads('{ "success": "true", "error": \"user created\" }'), 201)
        # return render_template('/uploading.html')
    return make_response(json.loads('{ "success": "false", "error": \"net Error\" }'), 408)


@blueprint.route('/upload', methods=['POST'])
def upload():
    username = str(request.form.get('username'))
    password = str(request.form.get('password'))
    file = request.files.get('file')

    cnx = get_db()
    cursor = cnx.cursor()

    query = '''select * from users where userID = %s '''
    cursor.execute(query, (username, ))
    user = cursor.fetchone()
    if user is None:
        ################### some http status
        # user not existed
        return make_response(json.loads('{ "success": "false", "error": \"user doesn\'t exist\" }'), 401)
    else :
        correctPwd = user[1]
        salt = user[2]
        encPwd = encryptString(password + salt)
        if correctPwd != encPwd:
            ################### some http status
            # password not matched
            return make_response(json.loads('{ "success": "false", "error": \"wrong password\" }'), 401)


    if file:
        filename = file.filename
        print(filename)

        if filename == '':
            ################### some http status
            return make_response(json.loads('{ "success": "false", "error": \"filename is needed\" }'), 400)

        if not allowed_file(filename):
            ################### some http status
            return make_response(json.loads('{ "success": "false", "error": \"bad file\" }'), 400)
        else:
            # file size cannot be larger than 50mb, perhaps?
            if os.fstat(file.fileno()).st_size > 50*1024*1024:
                sizeError = "The file size is larger than limit."
                ################### some http status
                return make_response(json.loads('{ "success": "false", "error": \"file is too large\" }'), 400)
            
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


#            path = os.path.join(os.getcwd(), "app", "static", "uploads")
#            img_org = os.path.join(path, keys[0])
#            file.save(img_org)
          
            #Text detection
            # img_detected = detect_text(img_org)
            # img_thumb = cv2.resize(img_detected, None, fx=0.3, fy=0.3)

            # Save the detected photos to hard drive
            # cv2.imwrite(os.path.join(path, keys[1]), img_detected)
            # cv2.imwrite(os.path.join(path, keys[2]), img_thumb)
            
            # Write into DB
            cnx = get_db()
            cursor = cnx.cursor()
            query = '''INSERT INTO photos (userID, key0, key1, key2) VALUES (%s, %s, %s, %s)'''
            cursor.execute(query, (username, keys[0], keys[1], keys[2]))
            cnx.commit()

            ################### some http status
            return make_response(json.loads('{"success": "true", "msg": "upload successfully" }'), 200)
    else: 
        return make_response(json.loads('{ "success": "false", "error": \"file is needed\" }'), 400)

    return make_response(json.loads('{ "success": "false", "error": \"net Error\" }'), 408)
