from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import dash
from flask_login import current_user

from app import *
from pages import login, data, register
from globals import *


login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# =========  Layout  =========== #
app.layout = html.Div(children=[
                dcc.Store(id='store-receitas', data=df_receitas.to_dict()),
                dcc.Store(id='store-despesas', data=df_despesas.to_dict()),
                dcc.Store(id='store-cat-receitas', data=df_cat_receitas.to_dict()),
                dcc.Store(id='store-cat-despesas', data=df_cat_despesas.to_dict()),
                
                dbc.Row([
                    dbc.Col([
                        dcc.Location(id="base-url", refresh=False), 
                        dcc.Store(id="login-state", data=""),
                        dcc.Store(id="register-state", data=""),

                        html.Div(id="page-content", style={"height": "100vh", "display": "flex", "justify-content": "center"})
                    ]),
                ]),
            ], style={"padding": "0px"})


# =========  Callbacks Page1  =========== #
@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    return user

@app.callback(Output("base-url", "pathname"), 
            [
                Input("login-state", "data"),
                Input("register-state", "data")
            ])
def render_page_content(login_state, register_state):
    ctx = dash.callback_context
    if ctx.triggered:
        trigg_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigg_id == 'login-state' and login_state == "success":
            return '/data'
        if trigg_id == 'login-state' and login_state == "error":
            return '/login'
        

        elif trigg_id == 'register-state':
            print(register_state, register_state=='')
            if register_state == "":
                return '/login'
            else:
                return '/register'
    else:
        return '/'


@app.callback(Output("page-content", "children"), 
            Input("base-url", "pathname"),
            [State("login-state", "data"), State("register-state", "data")])
def render_page_content(pathname, login_state, register_state):
    if (pathname == "/login" or pathname == "/"):
        return login.render_layout(login_state)

    if pathname == "/register":
        return register.render_layout(register_state)

    if pathname == "/data" or pathname == '/extrato-receitas' or pathname == '/extrato-despesas':
        if current_user.is_authenticated:
            return data.render_layout(current_user.username)
        else:
            return login.render_layout(register_state)
    


if __name__ == "__main__":
    app.run_server(port=8050, debug=True)