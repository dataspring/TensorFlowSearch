__author__ = 'aub3'
#!/usr/bin/env python
from flask import render_template, redirect, request, abort,jsonify
import base64
from inception import *
from settings import *
import sqlite3

png_data = load_network(True)
sess = tf.InteractiveSession()
index,files = load_index()

def home():
    payload = {'gae_mode':False}
    return render_template('editor.html',payload = payload)

def search():
    image_url = request.form['image_url']
    image_data = base64.decodestring(image_url[22:])
    pool3 = sess.graph.get_tensor_by_name('incept/pool_3:0')
    pool3_features = sess.run(pool3,{png_data: image_data})
    results = [k.split('/')[-1] for k in nearest(np.squeeze(pool3_features),index,files)]
    # for fname in results:
    #     download(fname)
    sqlResults = getsqlRes(results)

    print results
    return jsonify(results=sqlResults)

def search_quick():
    image_url = request.form['image_url']
    image_data = base64.decodestring(image_url[22:])
    pool3 = sess.graph.get_tensor_by_name('incept/pool_3:0')
    pool3_features = sess.run(pool3,{png_data: image_data})
    results = [k.split('/')[-1] for k in nearest_fast(np.squeeze(pool3_features),index,files)]
    # for fname in results:
    #     download(fname)
    sqlResults = getsqlRes(results)

    print results
    return jsonify(results=sqlResults)


def add_views(app):
    app.add_url_rule('/',view_func=home)
    app.add_url_rule('/Search',view_func=search,methods=['POST'])
    app.add_url_rule('/Quick',view_func=search_quick,methods=['POST'])


