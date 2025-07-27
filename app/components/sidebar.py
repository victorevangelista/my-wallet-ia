from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date
from app.models.financial_data import CatDespesas, CatReceitas

# Carregar categorias do banco
def get_categorias_despesas():
    return [{'label': c.categoria, 'value': c.categoria} for c in CatDespesas.query.all()]

def get_categorias_receitas():
    return [{'label': c.categoria, 'value': c.categoria} for c in CatReceitas.query.all()]


# ========= Layout ========= #
layout = dbc.Col([
                html.H1("My Budget", className="text-primary"),
                html.P("by Victor Evangelista", className="text-info"),
                html.Hr(),

    # Seção PERFIL ________________________________________>
                dbc.Button(id='botao_avatar',
                           children=[html.Img(src='../assets/img_hom.png', id='avatar_change', alt='Avatar', className='perfil_avatar')
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
                                dcc.DatePickerSingle(id='date-receita',
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
                                dbc.Select(
                                            id='select-receita', 
                                            options=[], 
                                           )
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
                                            html.Div([
                                                dbc.Alert(
                                                    id="category-div-add-receita",
                                                    is_open=False,
                                                    duration=5000,
                                                    color=""
                                                ),
                                            ], style={"padding-top": "20px"}),
                                        ], width=6),

                                        dbc.Col([
                                            html.Legend("Excluir categoria", style={"color": "red"}),
                                            dbc.Checklist(
                                                id='checklist-selected-style-receita',
                                                options=[],
                                                value=[],
                                                label_checked_style={"color": "red"},
                                                input_checked_style={"backgroudColor": "blue", "borderColor": "Orange"},
                                            ),
                                            dbc.Button('Remover', color='warning', id='remove-category-receita', style={"margin-top": "20px"}),
                                            html.Div([
                                                dbc.Alert(
                                                    id="category-div-remove-receita",
                                                    is_open=False,
                                                    duration=5000,
                                                    color=""
                                                ),
                                            ], style={"padding-top": "20px"}),
                                        ], width=6)
                                    ])
                                ], title='Adicionar/Remover Categoria')

                            ],  start_collapsed=True, id='accordion-receita'),
                            dbc.Button('Adicionar Receita', color='success', id='salvar-receita-btn', style={"margin-top": "20px"}),
                            html.Div([
                                dbc.Alert(
                                    id="alert-receita",
                                    is_open=False,
                                    duration=5000,
                                    color=""
                                ),
                            ], style={"padding-top": "20px"}),
                            
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
                                dbc.Select(
                                            id='select-despesa', 
                                            options=[], 
                                           )
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
                                            html.Div([
                                                dbc.Alert(
                                                    id="category-div-add-despesa",
                                                    is_open=False,
                                                    duration=5000,
                                                    color=""
                                                ),
                                            ], style={"padding-top": "20px"}),
                                        ], width=6),

                                        dbc.Col([
                                            html.Legend("Excluir categoria", style={"color": "red"}),
                                            dbc.Checklist(
                                                id='checklist-selected-style-despesa',
                                                options=[],
                                                value=[],
                                                label_checked_style={"color": "red"},
                                                input_checked_style={"backgroudColor": "blue", "borderColor": "Orange"},
                                            ),
                                            dbc.Button('Remover', color='warning', id='remove-category-despesa', style={"margin-top": "20px"}),
                                            html.Div([
                                                dbc.Alert(
                                                    id="category-div-remove-despesa",
                                                    is_open=False,
                                                    duration=5000,
                                                    color=""
                                                ),
                                            ], style={"padding-top": "20px"}),
                                        ], width=6)
                                    ])
                                ], title='Adicionar/Remover Categoria')
                            ], start_collapsed=True, id='accordion-despesa'),
                            dbc.Button('Adicionar Despesa', color='success', id='salvar-despesa-btn', style={"margin-top": "20px"}),
                            html.Div([
                                dbc.Alert(
                                    id="alert-despesa",
                                    is_open=False,
                                    duration=5000,
                                    color=""
                                ),
                            ], style={"padding-top": "20px"}),
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
                    dbc.NavLink("Importar OFX", href="/import-ofx", active="exact"),
                    dbc.NavLink("Fina Bot", href="/fina-bot", active="exact"),
                ], vertical=True, pills=True, id='nav_buttons', style={"marginBottom": "50px"}),
                
                dbc.Button("Logout", id="logout_button"),
                


], id='sidebar_completa')


