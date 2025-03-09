import dash
import dash_bootstrap_components as dbc
import sqlite3
from sqlalchemy import Table, create_engine
from sqlalchemy.sql import select

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os
# import configparser

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.MINTY]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

# Usar caminho absoluto para o banco de dados
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'data.sqlite')

conn = sqlite3.connect(db_path)
engine = create_engine(f'sqlite:///{db_path}')
db = SQLAlchemy()
# config = configparser.ConfigParser()

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
Users_tbl = Table('users', Users.metadata)

app = dash.Dash(__name__, external_stylesheets=estilos + [dbc_css])
server = app.server
app.config.suppress_callback_exceptions = True



server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
    SQLALCHEMY_TRACK_MODIFICATIONS=False)

db.init_app(server)



# Setup the LoginManager for the server
