from dash import dcc, html
import dash_ag_grid as dag
import dash_bootstrap_components as dbc

layout = dbc.Container([
        html.H2("Importação de Dados", className="mb-4", style={"textAlign": "center"}),
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
        # Botão para abrir o modal de edição do prompt
        dbc.Button(
            html.I(className="fa fa-cog", title="Editar Prompt de Classificação"),  # Ícone de engrenagem
            id="open-prompt-modal",
            color="primary",
            className="mt-2",
            style={"fontSize": "12px"}  # Ajusta o tamanho do botão
        ),

        # Modal para editar o prompt
        dbc.Modal([
            dbc.ModalHeader("Editar Prompt de Classificação"),
            dbc.ModalBody([
                dcc.Textarea(
                    id="prompt-textarea",
                    style={"width": "100%", "height": "300px"},
                )
            ]),
            dbc.ModalFooter([
                dbc.Button("Salvar", id="save-prompt", color="success"),
                dbc.Button("Fechar", id="close-prompt-modal", color="secondary")
            ])
        ], id="prompt-modal", is_open=False),


        # Tabela para Visualização dos Dados Importados
        html.Div(id="ofx-grid-container", children=[]),

        html.Br(),

        # Botão para Confirmar a Importação
        dbc.Button("Confirmar Importação", id="confirm-import", color="success", className="mt-2", disabled=True),
        
    ], fluid=True)
