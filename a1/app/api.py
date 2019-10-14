import os
import tempfile

from flask import request, jsonify, Response, make_response
from flask import Blueprint

from app.upload import allowed_file
from app.utils import *
from config import S3_BUCKET

blueprint = Blueprint('api', __name__)
@blueprint.route('/register', methods=['POST'])
def register():
    username = str(request.args.get('username'))
    password = str(request.args.get('password'))

    # username too long
    # need to figure out which status respond to which situation
    if len(username) > 100:
        return make_response("{success: false}", 404)
    elif username is None or len(username) == 0:
        return make_response("{success: false}", 404)

    cnx = get_db()
    cursor = cnx.cursor()

    encPwd = encryptString(password)
    query = '''SELECT * FROM users WHERE userID = %s'''
    cursor.execute(query, (username,))
    if cursor.fetchone() is not None:
        # some http response
        return make_response("{success: false}", 404)
    else:
        query = '''INSERT INTO users (userID, password) VALUES (%s, %s)'''
        cursor.execute(query, (username, encPwd))
        cnx.commit()
        # 200
        return make_response("{success: true}", 200)
        # return render_template('/uploading.html')
    return make_response("{success: false}", 300)


@blueprint.route('/upload', methods=['POST'])
def upload():
    username = str(request.form.get('username'))
    password = str(request.form.get('password'))
    file = request.files.get('file')

    cnx = get_db()
    cursor = cnx.cursor()

    query = '''select password from users where userID = %s '''
    cursor.execute(query, (username, ))
    correctPwd = cursor.fetchone()[0]
    if correctPwd is None:
        ################### some http status
        # user not existed
        return
    else :
        encPwd = encryptString(password)
        if correctPwd != encPwd:
            ################### some http status
            # password not matched
            return


    if file:
        filename = file.filename
        if filename == '':
            ################### some http status
            return

        if not allowed_file(filename):
            ################### some http status
            return
        else:
            # Save to S3
            s3 = boto3.resource('s3')
            path = tempfile.mkdtemp()
            # keys generated here, then save the original into tmp (key[0])
            # keys[1][2] are still waited to be created
            key = username + '_' + filename
            keys = keynameFactory(key)
            filepath = path + keys[0]

            # Save the original photo
            file.save(filepath)
            # file size cannot be larger than 50mb, perhaps?
            if os.path.getsize(filepath) > 50*1024*1024:
                sizeError = "The file size is larger than limit."
                ################### some http status
                return

            # here we need to change the other two to right files
            with open(filepath, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[0], Body=tmp)
            with open(filepath, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[1], Body=tmp)
            with open(filepath, 'rb') as tmp:
                s3.Bucket(S3_BUCKET).put_object(Key=keys[2], Body=tmp)

            ##################### TO DO ######################
            # 1. text detection                              #
            # 2. save the result and thumbnail of the result #                              #
            ##################################################

            # a function to create 3 key names

            query = '''INSERT INTO photos (userID, key0, key1, key2) VALUES (%s, %s, %s, %s)'''
            cursor.execute(query, (username, keys[0], keys[1], keys[2]))
            cnx.commit()

            ################### some http status
            return make_response("{success: true}", 200)

    return make_response("{success: false}", 404)