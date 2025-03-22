from dash import html, dcc
import dash_bootstrap_components as dbc
from app.components.sidebar import layout as sidebar

content = html.Div(id="page-content-dash")

def render_layout(username):
    return dbc.Container(children=[
            dcc.Location(id="base-url-data", refresh=True),
            dcc.Store(id="receitas-update-trigger", data=0),
            dcc.Store(id="despesas-update-trigger", data=0),
            dbc.Row([
                dbc.Col([
                    dcc.Location(id='data-url'),
                    sidebar,
                ], md=2),
                dbc.Col([
                    content
                ], md=10, style={"overflow-y": "scroll", "height": "100vh"})
            ]),
        ], fluid=True, style={"padding": "0px"}, className="dbc")
