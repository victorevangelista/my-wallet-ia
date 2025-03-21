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
                        html.H5('R$ 0', id='p-saldo-dashboard')
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
                        html.H5('R$ 0', id='p-receita-dashboard')
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
                        html.H5('R$ 0', id='p-despesa-dashboard')
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
            dbc.Col([
                dbc.Card([
                    html.Legend('Filtrar lançamentos', className='card-title'),
                    html.Label("Categoria das receitas"),
                    html.Div(
                        dcc.Dropdown(
                            id='dropdown-receita',
                            clearable=False,
                            style={"width": "100%"},
                            persistence=True,
                            persistence_type="session",
                            multi=True
                        )
                    ),
                    html.Label("Categoria das despesas", style={"marginTop": "10px"}),
                    html.Div(
                        dcc.Dropdown(
                            id='dropdown-despesa',
                            clearable=False,
                            style={"width": "100%"},
                            persistence=True,
                            persistence_type="session",
                            multi=True
                        )
                    ),

                    html.Legend('Período de análise', style={"marginTop": "10px"}),
                    dcc.DatePickerRange(
                        month_format='Do MMM, YY',
                        end_date_placeholder_text='Data...',
                        start_date=start_date,  # Definindo o primeiro dia do mês
                        end_date=datetime.today().date(),  # Ou qualquer outra data de término que você deseje
                        updatemode='singledate',
                        id='date-picker-config',
                        style={'zIndex': '100'}
                    )
                ], style={'height': '100%', "padding": "20px"})
            ], width=4),

            dbc.Col(
                dbc.Card(dcc.Graph(id='graph1'), style={'height': '100%', 'padding': '10px'}), width=8
            )
        ], style={"margin": "10px"}),

        dbc.Row([
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph2'), style={'height': '100%', 'padding': '10px'}), width=6
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph3'), style={'height': '100%', 'padding': '10px'}), width=3
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph4'), style={'height': '100%', 'padding': '10px'}), width=3
            )
        ], style={"margin": "10px"})
       
    ])