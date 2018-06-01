
'''
Created on June 1, 2018

@author: Abhiram Ampabathina

June 1 - Created basic flask app. With one route and sqlite data insert.
 
'''

from flask import Flask, render_template, redirect, url_for, request, g
import sqlite3
import hashlib

app = Flask(__name__)

DATABASE = 'Static/Users.db'

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
        # if validation_done is True:
        # then insert_OCI_USERS(username,fingerprint,api_key_path,region,tenancy)
        # else:
        # then send back the same page with error
        # return (basic.html,error=error)
        completion = False
        if completion ==False:
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('secret'))
    return render_template('login.html', error=error)

@app.route('/secret')
def secret():
    return "You have successfully logged in"

if __name__ == '__main__':
    app.run(debug=True)
