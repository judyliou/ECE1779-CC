from app import webapp
from flask import render_template, redirect, url_for, session

from app.utils import get_db, put_http_metric


@webapp.route("/viewImage/<key>", methods=['GET'])
def viewImage(key):
    put_http_metric(session['worker_id'])
    cnx = get_db()
    cursor = cnx.cursor()

    query = ''' select key0, key1 from photos where key2 = %s '''
    cursor.execute(query, (key,))
    keys = cursor.fetchone()
    url0 = url_for('static', filename='uploads/'+keys[0])
    url1 = url_for('static', filename='uploads/'+keys[1])

    return render_template("/twoImages.html", key0=url0, key1=url1)
