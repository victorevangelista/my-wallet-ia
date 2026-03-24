from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, date
from app.models.financial_data import CatDespesas, CatReceitas

# Carregar categorias do banco
def get_categorias_despesas():
    return [{'label': c.categoria, 'value': c.categoria} for c in CatDespesas.query.all()]

def get_categorias_receitas():
    return [{'label': c.categoria, 'value': c.categoria} for c in CatReceitas.query.all()]

# ========= Layout Function ========= #
def create_sidebar(state):
    is_collapsed = (state == 'collapsed')
    
    # Header da Sidebar (escondido se colapsado)
    sidebar_header = html.Div([
        html.H3("My Budget", className="text-primary sidebar-item-text", style={"fontSize": "1.5rem"}),
        html.P("by Victor", className="text-info sidebar-item-text", style={"fontSize": "0.8rem"}),
    ], className="text-center mb-4 mt-3 sidebar-item-text") if not is_collapsed else html.Div(style={"height": "20px"})

    # Conteúdo da Sidebar
    sidebar_content = html.Div([
        sidebar_header,
        html.Hr(),

        # Seção NOVO (Botões menores ou ícones no colapsado)
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        html.I(className="fa fa-plus-circle") if is_collapsed else "+ Receita",
                        id='open-novo-receita', color='success', size="sm", className="w-100"
                    )
                ], width=12 if is_collapsed else 6, className="mb-2"),
                dbc.Col([
                    dbc.Button(
                        html.I(className="fa fa-minus-circle") if is_collapsed else "- Despesa",
                        id='open-novo-despesa', color='danger', size="sm", className="w-100"
                    )
                ], width=12 if is_collapsed else 6)
            ])
        ], className="px-3 mb-4"),

        html.Hr(),

        # Seção NAV (Menu Principal)
        dbc.Nav([
            dbc.NavLink([
                html.I(className="fa fa-tachometer me-3" if not is_collapsed else "fa fa-tachometer"),
                html.Span("Dashboard", className="sidebar-item-text")
            ], href="/data", active="exact"),
            
            dbc.NavLink([
                html.I(className="fa fa-arrow-up me-3 text-success" if not is_collapsed else "fa fa-arrow-up text-success"),
                html.Span("Receitas", className="sidebar-item-text")
            ], href="/extrato-receitas", active="exact"),
            
            dbc.NavLink([
                html.I(className="fa fa-arrow-down me-3 text-danger" if not is_collapsed else "fa fa-arrow-down text-danger"),
                html.Span("Despesas", className="sidebar-item-text")
            ], href="/extrato-despesas", active="exact"),
            
            dbc.NavLink([
                html.I(className="fa fa-file-text me-3" if not is_collapsed else "fa fa-file-text"),
                html.Span("Importar OFX", className="sidebar-item-text")
            ], href="/import-ofx", active="exact"),
            
            dbc.NavLink([
                html.I(className="fa fa-android me-3 text-info" if not is_collapsed else "fa fa-android text-info"),
                html.Span("Fina Bot", className="sidebar-item-text")
            ], href="/fina-bot", active="exact"),
        ], vertical=True, pills=True, className="px-2"),
    ])

    # Modais (Sempre presentes no DOM para funcionamento dos callbacks)
    modals = html.Div([
        # Modal RECEITA
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
                            options=[{"label": "Cartão de Crédito", "value": 1},
                                     {"label": "Receita recorrente", "value": 2}],
                            value=[1],
                            id='swtches-input-receita',
                            switch=True
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label('Categoria da Receita'),
                        dbc.Select(id='select-receita', options=[])
                    ], width=4),
                ], style={"marginTop": "25px"}),
                dbc.Row([
                    dbc.Accordion([
                        dbc.AccordionItem(children=[
                            dbc.Row([
                                dbc.Col([
                                    html.Legend("Adicionar categoria", style={"color": "green"}),
                                    dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-receita", value=""),
                                    dbc.Button("Adicionar", className="btn btn-success", id="add-category-receita", style={"margin-top": "20px"}),
                                    html.Div([dbc.Alert(id="category-div-add-receita", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                                ], width=6),
                                dbc.Col([
                                    html.Legend("Excluir categoria", style={"color": "red"}),
                                    dbc.Checklist(id='checklist-selected-style-receita', options=[], value=[], label_checked_style={"color": "red"}),
                                    dbc.Button('Remover', color='warning', id='remove-category-receita', style={"margin-top": "20px"}),
                                    html.Div([dbc.Alert(id="category-div-remove-receita", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                                ], width=6)
                            ])
                        ], title='Adicionar/Remover Categoria')
                    ], start_collapsed=True, id='accordion-receita'),
                    dbc.Button('Adicionar Receita', color='success', id='salvar-receita-btn', style={"margin-top": "20px"}),
                    html.Div([dbc.Alert(id="alert-receita", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                ], style={"marginTop": "25px"})
            ])
        ], id='modal-novo-receita', size='lg', is_open=False, centered=True, backdrop=True),

        # Modal DESPESA
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
                            options=[{"label": "Cartão de Crédito", "value": 1},
                                     {"label": "Despesa recorrente", "value": 2}],
                            value=[1],
                            id='swtches-input-despesa',
                            switch=True
                        )
                    ], width=4),
                    dbc.Col([
                        dbc.Label('Categoria da Despesa'),
                        dbc.Select(id='select-despesa', options=[])
                    ], width=4),
                ], style={"marginTop": "25px"}),
                dbc.Row([
                    dbc.Accordion([
                        dbc.AccordionItem(children=[
                            dbc.Row([
                                dbc.Col([
                                    html.Legend("Adicionar categoria", style={"color": "green"}),
                                    dbc.Input(type="text", placeholder="Nova categoria...", id="input-add-despesa", value=""),
                                    dbc.Button("Adicionar", className="btn btn-success", id="add-category-despesa", style={"margin-top": "20px"}),
                                    html.Div([dbc.Alert(id="category-div-add-despesa", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                                ], width=6),
                                dbc.Col([
                                    html.Legend("Excluir categoria", style={"color": "red"}),
                                    dbc.Checklist(id='checklist-selected-style-despesa', options=[], value=[], label_checked_style={"color": "red"}),
                                    dbc.Button('Remover', color='warning', id='remove-category-despesa', style={"margin-top": "20px"}),
                                    html.Div([dbc.Alert(id="category-div-remove-despesa", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                                ], width=6)
                            ])
                        ], title='Adicionar/Remover Categoria')
                    ], start_collapsed=True, id='accordion-despesa'),
                    dbc.Button('Adicionar Despesa', color='success', id='salvar-despesa-btn', style={"margin-top": "20px"}),
                    html.Div([dbc.Alert(id="alert-despesa", is_open=False, duration=5000)], style={"padding-top": "20px"}),
                ], style={"marginTop": "25px"})
            ])
        ], id='modal-novo-despesa', size='lg', is_open=False, centered=True, backdrop=True),
    ])

    return html.Div([sidebar_content, modals])
