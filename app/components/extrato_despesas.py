from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        html.Legend("Tabela de despesas"),
        dbc.Alert(
            id="alert-auto",
            is_open=False,
            duration=5000,
        ),
        html.Div(id='tabela-despesas', className='dbc')
    ], style={"marginRight": "10px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card(
                dcc.Graph(id='bar-graph-despesas', style={"marginRight": "20px"})
            ),
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Despesas"),
                    html.Legend("R$ -", id='valor-despesas-card', style={"fontSize": "40px"}),
                    html.H6("Total de despesas"),
                ], style={"textAlign": "center", "paddingTop": "30px"})
            )
        ], width=3)
    ], style={"marginTop": "20px"})


], style={"padding": "10px"} )
