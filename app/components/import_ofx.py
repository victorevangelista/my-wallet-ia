from dash import dcc, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

layout = dbc.Container([
        html.H2("Importar Arquivo OFX", className="text-center"),

        # Alerta de Status
        dbc.Alert(id="import-alert", is_open=False, duration=5000, color="info"),
        
        # Seção Drag and Drop para Upload de Arquivo
        dcc.Upload(
            id='upload-ofx',
            children=html.Div([
                'Arraste e solte seu arquivo OFX aqui ou ',
                html.A('clique para selecionar um arquivo')
            ]),
            style={
                'width': '100%', 'height': '60px', 'lineHeight': '60px',
                'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                'textAlign': 'center', 'margin': '10px'
            },
            multiple=False  # Apenas um arquivo por vez
        ),

        html.Br(),

        dbc.Button("Atuaizar Classificação", id="classifica-import", color="success", className="mt-2"),

        # Tabela para Visualização dos Dados Importados
        html.Div(id="ofx-grid-container", children=[]),

        html.Br(),

        # Botão para Confirmar a Importação
        dbc.Button("Confirmar Importação", id="confirm-import", color="success", className="mt-2", disabled=True),
        
    ], fluid=True)
