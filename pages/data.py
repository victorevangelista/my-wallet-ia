from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import *

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from dash.exceptions import PreventUpdate

from pages.components import sidebar, dashboards, extrato_despesas, extrato_receitas

load_figure_template(["quartz"])
card_style = {
    'width': '800px',
    'min-height': '300px',
    'padding-top': '25px',
    'padding-right': '25px',
    'padding-left': '25px',
}

df = pd.DataFrame(np.random.randn(100, 1), columns=["data"])
fig = px.line(df, x=df.index, y="data", template="quartz")


# =========  Layout  =========== #
content = html.Div(id="page-content-dash")


def render_layout(username):
    template = dbc.Container(children=[
            dbc.Row([
                dbc.Col([
                    dcc.Location(id='data-url'),
                    sidebar.layout,
                ], md=2),
                dbc.Col([
                    content
                ], md=10, style={"overflow-y": "scroll", "height": "100vh"})
            ]),
            
        ], fluid=True, style={"padding": "0px"}, className="dbc")
    return template 

@app.callback(Output('page-content-dash', 'children'), [Input('data-url', 'pathname')])
def render_page(pathname):
    if pathname == '/data':
        return dashboards.layout
    
    if pathname == '/extrato-despesas':
        return extrato_despesas.layout
    
    if pathname == '/extrato-receitas':
        return extrato_receitas.layout

