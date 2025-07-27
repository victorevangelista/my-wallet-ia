from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        html.H2("Minhas Receitas", className="mb-4", style={"textAlign": "center"}),
        dbc.Alert(
            id="alert-auto-receita",
            is_open=False,
            duration=5000,
        ),
        html.Div(id='tabela-receitas', className='dbc')
    ], style={"marginRight": "10px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card(
                dcc.Graph(id='bar-graph-receitas', style={"marginRight": "20px"})
            ),
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Receitas"),
                    html.Legend("R$ -", id='valor-receitas-card', style={"fontSize": "40px"}),
                    html.H6("Total de receitas"),
                ], style={"textAlign": "center", "paddingTop": "30px"})
            )
        ], width=3)
    ], style={"marginTop": "20px"})


], style={"padding": "10px"} )
