import mysql.connector
from flask import g
import boto3
from botocore.exceptions import ClientError
import logging
import hashlib

from a1.config import db_config
from a1.app import webapp


def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db


@webapp.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def create_presigned_url(bucket_name, object_name, expiration=86400):
    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


def encryptString(string):
    sha_signature = hashlib.sha256(string.encode()).hexdigest()
    return sha_signature


def keynameFactory(filename):
    """ idea:
    if the the file name is already existed,
    add some suffix at the tail.
    example: asdf.jpg
    2nd time: asdf##001.jpg
    3rd time: asdf##002.jpg
    ...
    so for now, I assume one guy shouldn't upload 1000+ files with the same name

    param: filename
    return: a list of three names
    """
    fileParts = filename.split(".")
    fileShort = ".".join(fileParts[0:len(fileParts) - 1])
    fileType = fileParts[len(fileParts) - 1]

    cnx = get_db()
    cursor = cnx.cursor()
    query = ''' select key0 from photos where key0 like %s or key0 like %s'''
    cursor.execute(query, ("{}##%.%".format(fileShort), "{}.%".format(fileShort)))
    results = cursor.fetchall()

    key0 = fileShort + "##" + '{:03}'.format(len(results)) + "_key0" + "." + fileType
    key1 = fileShort + "##" + '{:03}'.format(len(results)) + "_key1" + "." + fileType
    key2 = fileShort + "##" + '{:03}'.format(len(results)) + "_key2" + "." + fileType
    print(key0)

    return [key0, key1, key2]

def normalName(name):
    """
    from modified filename, extract normal name
    without extension
    :param name: filename (a##001.png)
    :return: a
    """

    nameParts = name.split("##")
    return "##".join(nameParts[0:len(nameParts) - 1])
