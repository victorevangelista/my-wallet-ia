from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_extensions import Keyboard
import dash_bootstrap_components as dbc

def render_layout():
    return dbc.Card([
        dcc.Store(id="register-state", data=""),
        html.Legend("Registrar"),
        dbc.Input(id="user_register", placeholder="Username", type="text"),
        dbc.Input(id="pwd_register", placeholder="Password", type="password"),
        dbc.Input(id="email_register", placeholder="E-mail", type="email"),
        dbc.Button("Registrar", id='register-button'),
        
        html.Div([
            dbc.Alert(
                id="alert-register-message",
                is_open=False,
                duration=5000,
                color=""
            ),
        ], style={"padding-top": "20px", "justify-content": "center", "display": "flex"}),

        html.Div([
            html.Label("Ou ", style={"margin-right": "5px"}),
            dcc.Link("faça login", href="/login"),
        ], style={"padding": "10px 20px 20px 20px", "justify-content": "center", "display": "flex"}),

        Keyboard(captureKeys=["Enter"], id="register-keyboard"),
    ], className="align-self-center card-register")
