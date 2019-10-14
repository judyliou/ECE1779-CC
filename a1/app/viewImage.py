from a1.app import webapp
from flask import render_template, redirect
import boto3

from a1.app.utils import get_db
from a1.config import S3_BUCKET


@webapp.route("/viewImage/<key>", methods=['GET'])
def viewImage(key):
    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' select key0,key1 from photos where key2 = %s '''
    cursor.execute(query, (key,))
    keys = cursor.fetchone()

    # Retrieve images from S3
    s3 = boto3.client('s3')
    url0 = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': keys[0]
        }
    )
    url1 = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': S3_BUCKET,
            'Key': keys[1]
        }
    )

    return render_template("/twoImages.html", key0=url0, key1=url1)
