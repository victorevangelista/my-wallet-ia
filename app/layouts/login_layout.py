from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_extensions import Keyboard

def render_layout():
    return dbc.Card([
        dcc.Location(id="redirect", refresh=True),
        dcc.Store(id="register-state", data=""),
        html.Legend("Login"),
        dbc.Input(id="user_login", placeholder="Username", type="text"),
        dbc.Input(id="pwd_login", placeholder="Password", type="password"),
        dbc.Button("Login", id="login_button"),

        html.Div([
            dbc.Alert(
                id="alert-login-message",
                is_open=False,
                duration=5000,
                color=""
            ),
        ], style={"padding-top": "20px", "justify-content": "center", "display": "flex"}),

        html.Div([
            html.Label("Ou", style={"margin-right": "5px"}),
            dcc.Link("Registre-se", href="/register"),
        ], style={"justify-content": "center", "display": "flex"}),

        Keyboard(captureKeys=["Enter"], id="login-keyboard"),
    ], className="align-self-center card-login")
