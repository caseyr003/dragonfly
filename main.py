
'''
Created on June 1, 2018

@author: Abhiram Ampabathina

June 1 - Created basic flask app. With one route and sqlite data insert.

'''
import os
import sys
import logging
from flask import Flask, render_template, redirect, url_for, request, g
import sqlite3
import hashlib
import migration
app = Flask(__name__)

__version__ = '0.1'
__PLUGINS__ = "plugins/"
DATABASE = 'static/Users.db'


def config_logging():
    logging.basicConfig(filename="%s.log" % os.path.basename(sys.argv[0]), level=logging.DEBUG,
                        format="[%(asctime)s] %(levelname)-8s %(message)s", datefmt='%H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    logging.debug('Starting..')


def load_plugins():
    imported_plugins = []
    plugins = os.listdir('plugins')
    for plugin in plugins:
        if plugin != "baseplugin.py" and plugin != "__pycache__":
            exec("from plugins import "+plugin.split(".")[0])
            imported_plugins.append(plugin.split(".")[0])
    logging.debug(os.listdir('plugins'))
    logging.debug(imported_plugins)
    return imported_plugins


def main():
    config_logging()
    plugins = load_plugins()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def insert_OCI_USERS(username,fingerprint,api_key_path,region,tenancy):
    try:
        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO OCI_USERS (USERNAME,FINGERPRINT,API_KEY_PATH,REGION,TENANCY) VALUES (?,?,?,?.?)", (username,fingerprint,api_key_path,region,tenancy))
        con.commit()
        con.close()
    except (sqlite3.OperationalError, msg):
        print (msg)
        return (1)
    return (0)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # Validate here before we insert into sqllite3.
        
        # validation_done = migration.authenticate(request.POST['user_ocid'], request.POST['tenancy_ocid'], request.POST['fingerprint'], request.POST['region'], request.POST[''])
        # if validation_done is True:
        #     migration.insert_OCI_USERS(username,fingerprint,api_key_path,region,tenancy)
        # else:
        #     return (basic.html, error=error)
        completion = False
        if completion ==False:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('secret'))
    return render_template('login.html', error=error)


@app.route('/secret')
def secret():
    return "You have successfully logged in"


@app.route('/source')
def select_source():
    return render_template('source.html')


@app.route('/source/ocic')
def ocic_login():
    return render_template('source_ocic.html')


@app.route('/source/vsphere')
def vsphere_login():
    return render_template('source_vsphere.html')


@app.route('/source/local')
def select_local():
    return render_template('source_local.html')


@app.route('/select')
def select_images():
    return render_template('image_selection.html')


if __name__ == '__main__':
    main()
    app.run(debug=True)
