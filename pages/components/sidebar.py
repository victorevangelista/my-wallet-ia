import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from app import app

from datetime import datetime, date
import plotly.express as px
import numpy as np
import pandas as pd


from globals import *
from dash_bootstrap_templates import ThemeChangerAIO

from flask_login import login_user, logout_user, current_user


# ========= Layout ========= #
layout = dbc.Col([
                html.H1("My Budget", className="text-primary"),
                html.P("by Victor Evangelista", className="text-info"),
                html.Hr(),

    # Seção PERFIL ________________________________________>
                dbc.Button(id='botao_avatar',
                           children=[html.Img(src='/assets/img_hom.png', id='avatar_change', alt='Avatar', className='perfil_avatar')
                ], style={'backgroundColor': 'transparent', 'borderColor': 'transparent'}),

    # Seção NOVO ________________________________________>
                dbc.Row([
                    dbc.Col([
                        dbc.Button(id='open-novo-receita', color='success',
                                   children=['+ Receita'])
                            
                    ], width=6),
                    dbc.Col([
                        dbc.Button(id='open-novo-despesa', color='danger',
                                   children=['- Despesa'])
                            
                    ], width=6)

                ]),

                # Modal RECEITA ________________________>
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle('Adicionar receita')),
                    dbc.ModalBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Descrição: '),
                                dbc.Input(placeholder="Ex. Salário, Dividendos da bolsa, Job...", id="txt-receita"),
                            ], width=6),
                            dbc.Col([
                                dbc.Label('Valor: '),
                                dbc.Input(placeholder="R$ 500,00", id="valor-receita", value=""),
                            ], width=6),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Data: '),
                                dcc.DatePickerSingle(id='date-receitas',
                                                     min_date_allowed=date(2020,1,1),
                                                     max_date_allowed=date(2030,12,31),
                                                     date=datetime.today(),
                                                     style={"width": "100%"}
                                                     ),
                            ], width=4),

                            dbc.Col([
                                dbc.Label('Extras'),
                                dbc.Checklist(
                                    options=[{"label": "Foi Parcelada", "value": 1},
                                             {"label": "Receita recorrente", "value": 2}],
                                    value=[1],
                                    id='swtches-input-receita',
                                    switch=True
                                )
                            ], width=4),

                            dbc.Col([
                                dbc.Label('Categoria da Receita'),
                                dbc.Select(id='select-receita', 
                                           options=[{'label': i, 'value': i} for i in cat_receitas], 
                                           value=cat_receitas[0])
                            ], width=4),

                        ], style={"marginTop": "25px"}),

                        dbc.Row([
                            dbc.Accordion([
                                dbc.AccordionItem(children=[
                                    dbc.Row([

                                        dbc.Col([
                                            html.Legend("Adicionar categoria", style={"color": "green"}),
                                            dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-receita", value=""),
                                            html.Br(),
                                            dbc.Button("Adicionar", className="btn btn-success", id="add-category-receita", style={"margin-top": "20px"}),
                                            html.Br(),
                                            html.Div(id="category-div-add-receita", style={}),
                                        ], width=6),

                                        dbc.Col([
                                            html.Legend("Excluir categoria", style={"color": "red"}),
                                            dbc.Checklist(
                                                id='checklist-selected-style-receita',
                                                options=[{'label': i, 'value': i} for i in cat_receitas],
                                                value=[],
                                                label_checked_style={"color": "red"},
                                                input_checked_style={"backgroudColor": "blue", "borderColor": "Orange"},
                                            ),
                                            dbc.Button('Remover', color='warning', id='remove-category-receita', style={"margin-top": "20px"})
                                        ], width=6)
                                    ])
                                ], title='Adicionar/Remover Categoria')

                            ], flush=True, start_collapsed=True, id='accordion-receita'),
                            
                            html.Div(id='teste-receita', style={"padding-top": "20px"}),
                            dbc.ModalFooter([
                                dbc.Button("Adicionar Receita", id="salvar-receita", color="success"),
                                dbc.Popover(dbc.PopoverBody("Receita Salva"), target="salvar-receita", placement="left", trigger="click"),
                            ])
                        ], style={"marginTop": "25px"})
                    ])
                ], style={"background-color": "rgba(17, 140, 79, 0,05)"},
                    id='modal-novo-receita',
                    size='lg',
                    is_open=False,
                    centered=True,
                    backdrop=True),

                # Modal DESPESA ________________________>
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle('Adicionar despesa')),
                    dbc.ModalBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Descrição: '),
                                dbc.Input(placeholder="Ex. Escola, Combustível...", id="txt-despesa"),
                            ], width=6),
                            dbc.Col([
                                dbc.Label('Valor: '),
                                dbc.Input(placeholder="R$ 500,00", id="valor-despesa", value=""),
                            ], width=6),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Data: '),
                                dcc.DatePickerSingle(id='date-despesas',
                                                     min_date_allowed=date(2020,1,1),
                                                     max_date_allowed=date(2030,12,31),
                                                     date=datetime.today(),
                                                     style={"width": "100%"}
                                                     ),
                            ], width=4),

                            dbc.Col([
                                dbc.Label('Extras'),
                                dbc.Checklist(
                                    options=[{"label": "Foi Parcelado", "value": 1},
                                             {"label": "Despesa recorrente", "value": 2}],
                                    value=[1],
                                    id='swtches-input-despesa',
                                    switch=True
                                )
                            ], width=4),

                            dbc.Col([
                                dbc.Label('Categoria da Despesa'),
                                dbc.Select(id='select-despesa', 
                                           options=[{'label': i, 'value': i} for i in cat_despesas], 
                                           value=cat_despesas[0])
                            ], width=4),

                        ], style={"marginTop": "25px"}),

                        dbc.Row([
                            dbc.Accordion([
                                dbc.AccordionItem(children=[
                                    dbc.Row([

                                        dbc.Col([
                                            html.Legend("Adicionar categoria", style={"color": "green"}),
                                            dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-despesa", value=""),
                                            html.Br(),
                                            dbc.Button("Adicionar", className="btn btn-success", id="add-category-despesa", style={"margin-top": "20px"}),
                                            html.Br(),
                                            html.Div(id="category-div-add-despesa", style={}),
                                        ], width=6),

                                        dbc.Col([
                                            html.Legend("Excluir categoria", style={"color": "red"}),
                                            dbc.Checklist(
                                                id='checklist-selected-style-despesa',
                                                options=[{'label': i, 'value': i} for i in cat_despesas],
                                                value=[],
                                                label_checked_style={"color": "red"},
                                                input_checked_style={"backgroudColor": "blue", "borderColor": "Orange"},
                                            ),
                                            dbc.Button('Remover', color='warning', id='remove-category-despesa', style={"margin-top": "20px"})
                                        ], width=6)
                                    ])
                                ], title='Adicionar/Remover Categoria')
                            ], flush=True, start_collapsed=True, id='accordion-despesa'),
                            
                            html.Div(id='teste-despesa', style={"paddingTop": "20px"}),
                            dbc.ModalFooter([
                                dbc.Button("Adicionar despesa", id="salvar-despesa", color="success"),
                                dbc.Popover(dbc.PopoverBody("Despesa Salva"), target="salvar-despesa", placement="left", trigger="click"),
                            ])
                        ], style={"marginTop": "25px"})
                    ])
                ], style={"background-color": "rgba(17, 140, 79, 0,05)"},
                    id='modal-novo-despesa',
                    size='lg',
                    is_open=False,
                    centered=True,
                    backdrop=True),

    # Seção NAV ________________________________________>
                html.Hr(),
                dbc.Nav([
                    dbc.NavLink("Dashboard", href="/data", active="exact"),
                    dbc.NavLink("Extrato Receitas", href="/extrato-receitas", active="exact"),
                    dbc.NavLink("Extrato Despesas", href="/extrato-despesas", active="exact"),
                ], vertical=True, pills=True, id='nav_buttons', style={"marginBottom": "50px"}),
                
                dbc.Button("Logout", id="logout_button"),


], id='sidebar_completa')



# =========  Callbacks  =========== #
# Pop-up receita
@app.callback(
    Output('modal-novo-receita', 'is_open'),
    Input('open-novo-receita', 'n_clicks'),
    State('modal-novo-receita', 'is_open')
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open


# Pop-up Despesa
@app.callback(
    Output('modal-novo-despesa', 'is_open'),
    Input('open-novo-despesa', 'n_clicks'),
    State('modal-novo-despesa', 'is_open')
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open


@app.callback(
    Output('store-receitas', 'data', allow_duplicate=True),

    Input('salvar-receita', 'n_clicks'),
    [
        State('txt-receita', 'value'),
        State('valor-receita', 'value'),
        State('date-receitas', 'date'),
        State('swtches-input-receita', 'value'),
        State('select-receita', 'value'),
        State('store-receitas', 'data'),
    ],
    prevent_initial_call='initial_duplicate'
)
def salve_form_receita(n, descricao, valor, date, switches, categoria, dict_receitas):
    # import pdb
    # pdb.set_trace()

    df_receitas = pd.DataFrame(dict_receitas)

    if n and not(valor == "" or valor == None):
        valor = round(float(valor), 2)
        date = pd.to_datetime(date).date()
        categoria = categoria[0] if type(categoria) == list else categoria
        parcelado = 1 if 1 in switches else 0
        fixo = 1 if 2 in switches else 0

        df_receitas.loc[df_receitas.shape[0]] = [descricao, categoria, date, valor, parcelado, fixo]
        df_receitas.to_csv(f"{path}/df_receitas.csv")
    
    data_return = df_receitas.to_dict()
    return data_return



@app.callback(
    Output('store-despesas', 'data'),

    Input('salvar-despesa', 'n_clicks'),
    [
        State('txt-despesa', 'value'),
        State('valor-despesa', 'value'),
        State('date-despesas', 'date'),
        State('swtches-input-despesa', 'value'),
        State('select-despesa', 'value'),
        State('store-despesas', 'data'),
    ]
)
def salve_form_despesa(n, descricao, valor, date, switches, categoria, dict_despesas):
    # import pdb
    # pdb.set_trace()

    df_despesas = pd.DataFrame(dict_despesas)

    if n and not(valor == "" or valor == None):
        valor = round(float(valor), 2)
        date = pd.to_datetime(date).date()
        categoria = categoria[0] if type(categoria) == list else categoria
        parcelado = 1 if 1 in switches else 0
        fixo = 1 if 2 in switches else 0

        df_despesas.loc[df_despesas.shape[0]] = [descricao, categoria, date, valor, parcelado, fixo]
        df_despesas.to_csv(f"{path}/df_despesas.csv")
    
    data_return = df_despesas.to_dict()
    return data_return


@app.callback(
    [
        Output("select-receita", "options"),
        Output("checklist-selected-style-receita", "options"),
        Output("checklist-selected-style-receita", "value"),
        Output("store-cat-receitas", "data")
    ],

    [
        Input("add-category-receita", "n_clicks"),
        Input("remove-category-receita", "n_clicks")
    ],

    [
        State("input-add-receita", "value"),
        State("checklist-selected-style-receita", "value"),
        State("store-cat-receitas", "data")
    ]
)
def add_category_receita(n, n2, txt, check_delete, data):
    # import pdb
    # pdb.set_trace()

    cat_receita = list(data["Categoria"].values())

    if n and not (txt == "" or txt == None):
        cat_receita = cat_receita + [txt] if txt not in cat_receita else cat_receita

    if n2 and len(check_delete) > 0:
        cat_receita = [i for i in cat_receita if i not in check_delete]

    opt_receita = [{"label": i, "value": i} for i in cat_receita]
    df_cat_receita = pd.DataFrame(cat_receita, columns=['Categoria'])
    df_cat_receita.to_csv(f"{path}/df_cat_receitas.csv")
    data_return = df_cat_receita.to_dict()

    return [opt_receita, opt_receita, [], data_return]


@app.callback(
    [
        Output("select-despesa", "options"),
        Output("checklist-selected-style-despesa", "options"),
        Output("checklist-selected-style-despesa", "value"),
        Output("store-cat-despesas", "data")
    ],

    [
        Input("add-category-despesa", "n_clicks"),
        Input("remove-category-despesa", "n_clicks")
    ],

    [
        State("input-add-despesa", "value"),
        State("checklist-selected-style-despesa", "value"),
        State("store-cat-despesas", "data")
    ]
)
def add_category_despesa(n, n2, txt, check_delete, data):
    # import pdb
    # pdb.set_trace()

    cat_despesa = list(data["Categoria"].values())

    if n and not (txt == "" or txt == None):
        cat_despesa = cat_despesa + [txt] if txt not in cat_despesa else cat_despesa

    if n2 and len(check_delete) > 0:
        cat_despesa = [i for i in cat_despesa if i not in check_delete]

    opt_despesa = [{"label": i, "value": i} for i in cat_despesa]
    df_cat_despesa = pd.DataFrame(cat_despesa, columns=['Categoria'])
    df_cat_despesa.to_csv(f"{path}/df_cat_despesas.csv")
    data_return = df_cat_despesa.to_dict()

    return [opt_despesa, opt_despesa, [], data_return]


@app.callback(
    Output('data-url', 'pathname'),
    Input('logout_button', 'n_clicks'),
    )
def successful(n_clicks):
    if n_clicks == None:
        raise PreventUpdate
    
    if current_user.is_authenticated:
        logout_user()
        return '/login'
    else: 
        return '/login'