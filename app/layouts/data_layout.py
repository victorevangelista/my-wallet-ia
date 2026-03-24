from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime

content = html.Div(id="page-content-dash")

today = datetime.today()
start_date = today.replace(day=1).date()

filtros_globais = html.Div([
    dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    html.Div([
                        dbc.Button(
                            [html.I(className="fa fa-trash-alt me-2"), "Limpar Filtros"],
                            id="btn-limpar-filtros",
                            color="danger",
                            outline=True,
                            size="sm",
                            className="p-1",
                            style={"display": "none", "fontSize": "12px"}
                        )
                    ], className="d-flex justify-content-end mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Categorias das Receitas"),
                            dcc.Dropdown(
                                id='dropdown-receita',
                                clearable=False,
                                style={"width": "100%"},
                                persistence=True,
                                persistence_type="session",
                                multi=True
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Categorias das Despesas"),
                            dcc.Dropdown(
                                id='dropdown-despesa',
                                clearable=False,
                                style={"width": "100%"},
                                persistence=True,
                                persistence_type="session",
                                multi=True
                            )
                        ], md=4),
                        dbc.Col([
                            html.Label("Período de Análise"),
                            html.Br(),
                            dcc.DatePickerRange(
                                month_format='Do MMM, YY',
                                end_date_placeholder_text='Data...',
                                start_date=start_date,
                                end_date=datetime.today().date(),
                                updatemode='singledate',
                                id='date-picker-config',
                                style={'zIndex': '100'},
                                persistence=True,
                                persistence_type="local",
                            )
                        ], md=4)
                    ], className="g-4 mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Lançamentos Recorrentes:"),
                            dbc.RadioItems(
                                options=[
                                    {"label": "Todos", "value": "todas"},
                                    {"label": "Fixos", "value": "recorrente"},
                                    {"label": "Não recorrentes", "value": "nao_recorrente"}
                                ],
                                value="todas",
                                id="radio-recorrentes",
                                inline=True,
                                style={"marginBottom": "10px"},
                                persistence=True,
                                persistence_type="local",
                            ),
                        ], md=6),
                        dbc.Col([
                            html.Label("Compras no Cartão:"),
                            dbc.RadioItems(
                                options=[
                                    {"label": "Todos", "value": "todas"},
                                    {"label": "No Cartão", "value": "cartao_credito"},
                                    {"label": "Outros", "value": "outros"}
                                ],
                                value="todas",
                                id="radio-cartao",
                                inline=True,
                                persistence=True,
                                persistence_type="local",
                            )
                        ], md=6),
                    ], className="g-4"),
                ],
                title=html.Div([
                    "Filtros Globais",
                    html.I(className="fa fa-filter ms-2", id="filter-icon", style={"display": "none"}),
                ], className="d-flex align-items-center"),
                item_id="item-filtros",
            ),
        ],
        id="accordion-filtros",
        start_collapsed=True,
        flush=True,
        className="custom-accordion",
    )
], style={"margin": "10px"})

def render_layout(username):
    return html.Div([
        # Stores locais para controle de refresh de dados
        dcc.Store(id="receitas-update-trigger", data=0),
        dcc.Store(id="despesas-update-trigger", data=0),
        dcc.Location(id='data-url', refresh=False),
        
        # Filtros Globais (agora em Accordion)
        filtros_globais,
        
        # Área onde o callback injeta Dashboard, Extratos, etc.
        content
    ], className="dbc")
