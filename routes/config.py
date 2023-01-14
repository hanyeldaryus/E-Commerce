
from flask import Flask
import os
from flask_mysqldb import MySQL
from os.path import join, dirname, realpath, abspath


app = Flask(__name__, template_folder="../templates",
            static_folder="../static")
app.config['UPLOAD_FOLDER'] = abspath(
    join(dirname(realpath(__file__)), '..', 'static', 'images', 'userpp'))
app.secret_key = 'workshop-rpl'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = 'weshop'


mysql = MySQL(app)
