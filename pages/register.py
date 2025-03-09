from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from werkzeug.security import generate_password_hash
from dash.exceptions import PreventUpdate
from dash_extensions import Keyboard

from app import *

# =========  Layout  =========== #
def render_layout(message):
    message = f"Ocorreu algum erro durante o registro. {message}" if "Erro" in message else message

    layout = dbc.Card([
                html.Legend("Registrar"),
                dbc.Input(id="user_register", placeholder="Username", type="text"),
                dbc.Input(id="pwd_register", placeholder="Password", type="password"),
                dbc.Input(id="email_register", placeholder="E-mail", type="email"),
                dbc.Button("Registrar", id='register-button'),
                html.Span(message, style={"text-align": "center"}),

                html.Div([
                    html.Label("Ou ", style={"margin-right": "5px"}),
                    dcc.Link("faça login", href="/login"),
                ], style={"padding": "20px", "justify-content": "center", "display": "flex"}),

                Keyboard(captureKeys=["Enter"], id="register-keyboard"),

            ], className="align-self-center card-register")
    return layout



# =========  Callbacks Page1  =========== #
@app.callback(
    Output('register-state', 'data'),
    
    [Input('register-button', 'n_clicks'), 
     Input('register-keyboard', 'n_keydowns')],

    [State('user_register', 'value'), 
    State('pwd_register', 'value'),
    State('email_register', 'value')],
    )
def successful(n_clicks, n_keydowns, username, password, email):
    if n_clicks == None and n_keydowns == None:
        raise PreventUpdate
    print(n_keydowns)

    if username is not None and password is not None and email is not None:
        hashed_password = generate_password_hash(password)
        ins = Users_tbl.insert().values(username=username,  password=hashed_password, email=email)
        try:
            conn = engine.connect()
            conn.execute(ins)
            conn.commit()
            conn.close()
            return ''
        except Exception as e:
            conn.rollback()
            conn.close()
            return 'Erro: Login ou e-mail já castrado.' if "UNIQUE" in e.args[0] else "Erro inesperado!"
    else:
        return 'Erro: Faltou o preenchimento de algum campo.'