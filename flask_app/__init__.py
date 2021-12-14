import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MYSQL_HOST'] = os.getenv('DATABASE_HOST')
app.config['MYSQL_USER'] = os.getenv('DATABASE_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DATABASE_PASS')
app.config['MYSQL_DB'] = os.getenv('DATABASE_SCHEMA')
mysql = MySQL(app)
bcrypt = Bcrypt(app)

from flask_app import routes
