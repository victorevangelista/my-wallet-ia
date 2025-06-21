from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Importações atualizadas
from app.services.receita_service import buscar_receitas_por_usuario, update_receita_por_usuario
from app.services.categoria_service import buscar_cat_receitas_por_usuario
from flask_login import current_user
from app import get_current_user_db_session

def register_callbacks(dash_app):
    @dash_app.callback(
        Output('tabela-receitas', 'children'),
        Input("base-url", "pathname")
    )
    def imprimir_tabela(pathname):
        if not current_user.is_authenticated:
            return html.Div("Por favor, faça login para ver as receitas.")

        user_session = get_current_user_db_session()
        if not user_session:
            return html.Div("Erro ao carregar dados do usuário.")

        receitas_data = buscar_receitas_por_usuario(user_session)
        df = pd.DataFrame(receitas_data)
        if df.empty:
            return html.Div("Nenhuma receita encontrada.")

        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce').dt.date
        df = df.fillna('-')
        df = df.sort_values(by='data', ascending=False) # Atribuir o resultado da ordenação

        success, receita_cat_data = buscar_cat_receitas_por_usuario(user_session)
        if success:
            df_cat = pd.DataFrame(receita_cat_data)
            # Lista de categorias distintas
            categorias_distintas = df_cat['categoria'].drop_duplicates().tolist() # Corrigido de 'descricao' para 'categoria'
        else:
            categorias_distintas = []

        columnDefs = [
            {
                "headerName": "Descrição",
                "field": "descricao",
                "cellEditor": "agTextCellEditor",
                "cellEditorParams": {
                    "maxLength": 120,
                },
            },
            {
                "headerName": "Categoria",
                "field": "categoria",
                "cellEditor": "agSelectCellEditor",
                "cellEditorParams": {
                    "values": categorias_distintas,
                },
            },
            {
                "headerName": "Data",
                "field": "data",
                "cellEditor": "agDateStringCellEditor",
            },
            {
                "headerName": "Valor",
                "wrapHeaderText": True,
                "autoHeaderHeight": True,
                "field": "valor",
                "cellEditor": "agNumberCellEditor",
                "cellEditorParams": {
                    "precision": 2,
                    "showStepperButtons": False,
                },
                "type": "rightAligned",
                "valueFormatter": {"function": "d3.format('$,.2f')(params.value)"},
            },
            {
                "headerName": "Parcelado",
                "field": "parcelado",
            },
            {
                "headerName": "Fixo",
                "field": "fixo",
            },
        ]

        tabela = dag.AgGrid(
                id="tbl-receita",
                rowData=df.to_dict("records"),
                # columnDefs=[{"field": i} for i in df.columns],
                columnDefs=columnDefs,
                defaultColDef={"editable": True, "minWidth": 120},
                dashGridOptions={"animateRows": True, 'pagination':True},
            )
        return tabela


    @dash_app.callback(
            [
                Output('alert-auto', 'is_open', allow_duplicate=True), 
                Output('alert-auto', 'children', allow_duplicate=True),
                Output("receitas-update-trigger", "data"),
            ],
            [
                Input('tbl-receita', 'cellValueChanged'),
            ],
            [
                State("alert-auto", "is_open"),
                State("receitas-update-trigger", "data")
            ],
            prevent_initial_call='initial_duplicate'
        )
    def update_data(cell_changed, is_open, update_trigger ):
        if cell_changed and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return not is_open, "Erro de sessão. Faça login novamente.", update_trigger

            id = cell_changed[0]['data']['id']
            descricao = cell_changed[0]['data']['descricao']
            valor = round(float(cell_changed[0]['data']['valor']), 2)
            data = pd.to_datetime(cell_changed[0]['data']['data']).date()
            categoria = cell_changed[0]['data']['categoria']
            parcelado_val = cell_changed[0]['data']['parcelado']
            fixo_val = cell_changed[0]['data']['fixo']

            # Certifique-se que parcelado e fixo sejam booleanos se necessário pelo modelo/serviço
            # Exemplo: parcelado = bool(parcelado_val)

            success, result = update_receita_por_usuario(user_session, id, descricao, categoria, data, valor, parcelado_val, fixo_val)

            return not is_open, f"{result} Linha: {cell_changed[0]['rowId']}" if success else result, update_trigger + 1
        return is_open, "Edite a tabela", update_trigger 

    @dash_app.callback(
        Output('bar-graph-receitas', 'figure'),
        Input("receitas-update-trigger", "data"),
    )
    def bar_graph(trigger_data):
        if not current_user.is_authenticated:
            return px.bar() # Retorna gráfico vazio

        user_session = get_current_user_db_session()
        if not user_session:
            return px.bar()

        receitas_data = buscar_receitas_por_usuario(user_session)
        df = pd.DataFrame(receitas_data)
        if df.empty:
            return px.bar(title="Receitas Gerais").update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        df_grouped = df.groupby("categoria").sum()[["valor"]].reset_index()
        graph = px.bar(df_grouped, x="categoria", y="valor", title="Receitas Gerais")
        graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return graph

    @dash_app.callback(
        Output('valor-receitas-card', 'children'),
        Input("receitas-update-trigger", "data"),
    )
    def display_receitas(trigger_data): # Renomeado display_desp para display_receitas
        if not current_user.is_authenticated:
            return "R$ 0.00"

        user_session = get_current_user_db_session()
        if not user_session:
            return "R$ 0.00"
            
        receitas_data = buscar_receitas_por_usuario(user_session)
        df = pd.DataFrame(receitas_data)
        if df.empty:
            return "R$ 0.00"
        valor = df['valor'].sum()
        return f"R$ {valor:.2f}"