from dash import html, dcc
from datetime import datetime
import dash_bootstrap_components as dbc

# Obter o primeiro dia do mês atual
today = datetime.today()
start_date = today.replace(day=1).date()

# =========  Layout  =========== #
layout = dbc.Col([
        dbc.Row([
            # Saldo total
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Saldo'),
                        html.H5('R$ 0', id={'page': 'dashboard', 'type': 'dash-metric', 'id': 'saldo'})
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-university card-icon'),
                        color='warning',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),

            # Receita 
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Receita'),
                        html.H5('R$ 0', id={'page': 'dashboard', 'type': 'dash-metric', 'id': 'receita'})
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-smile-o card-icon'),
                        color='success',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),

            #Despesa
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Despesa'),
                        html.H5('R$ 0', id={'page': 'dashboard', 'type': 'dash-metric', 'id': 'despesa'})
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-meh-o card-icon'),
                        color='danger',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),
        ], style={"margin": "10px"}),

        dbc.Row([
            dbc.Col(
                dbc.Card(dcc.Graph(id={'page': 'dashboard', 'type': 'dash-graph', 'id': 'graph1'}), style={'height': '100%', 'padding': '10px'}), width=12
            )
        ], style={"margin": "10px"}),

        dbc.Row([
            dbc.Col(
                dbc.Card(dcc.Graph(id={'page': 'dashboard', 'type': 'dash-graph', 'id': 'graph2'}), style={'height': '100%', 'padding': '10px'}), width=6
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id={'page': 'dashboard', 'type': 'dash-graph', 'id': 'graph3'}), style={'height': '100%', 'padding': '10px'}), width=3
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id={'page': 'dashboard', 'type': 'dash-graph', 'id': 'graph4'}), style={'height': '100%', 'padding': '10px'}), width=3
            )
        ], style={"margin": "10px"})
       
    ])