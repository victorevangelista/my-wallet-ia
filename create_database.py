from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import warnings
import os
# import configparser

# Usar caminho absoluto para o banco de dados
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'data.sqlite')

conn = sqlite3.connect(db_path)
engine = create_engine(f'sqlite:///{db_path}')
db = SQLAlchemy()
# config = configparser.ConfigParser()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable = False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

Users_tbl = Table('users', Users.metadata)

#fuction to create table using Users class
def create_users_table():
    Users.metadata.create_all(engine)
create_users_table()



# import pandas as pd
# c = conn.cursor()
# df = pd.read_sql('select * from users', conn)
# df
