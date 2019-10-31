import mysql.connector
from flask import g
import logging
import hashlib
import random
import boto3
from datetime import datetime

from config import db_config
from app import webapp


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

def randomString(length):
    result = ""
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    charactersLength = len(characters)
    for i in range(length):
        result += characters[random.randint(0, charactersLength - 1)]
    print(result)
    return result

# def put_http_metric(id):
#     print('time:', datetime.utcnow())
#     client = boto3.client('cloudwatch', region_name='us-east-1')
#     response = client.put_metric_data(
#         Namespace='Mynamespace',
#         MetricData=[
#             {
#                 'MetricName': 'HTTPRequest',
#                 'Dimensions': [
#                     {
#                         'Name': 'InstanceId',
#                         'Value': id,
#                     },
#                 ],
#                 'Timestamp': datetime.utcnow(),
#                 'StatisticValues': {
#                     'SampleCount': 1.0,
#                     'Sum': 1.0,
#                     'Minimum': 1.0,
#                     'Maximum': 1.0
#                 },
#                 'StorageResolution': 60
#             },
#         ]
#     )