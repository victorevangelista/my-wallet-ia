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
        html.Div(id={'page': 'receitas', 'type': 'extrato-grid', 'id': 'table'}, className='dbc')
    ], style={"marginRight": "10px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card(
                dcc.Graph(id={'page': 'receitas', 'type': 'extrato-graph', 'id': 'bar'}, style={"marginRight": "20px"})
            ),
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Receitas"),
                    html.Legend("R$ -", id={'page': 'receitas', 'type': 'extrato-metric', 'id': 'total'}, style={"fontSize": "40px"}),
                    html.H6("Total de receitas"),
                ], style={"textAlign": "center", "paddingTop": "30px"})
            )
        ], width=3)
    ], style={"marginTop": "20px"})
])
