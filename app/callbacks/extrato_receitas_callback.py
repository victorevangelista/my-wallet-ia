from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from dash import dcc
from dash import html, Patch
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Importações atualizadas
from app.services.receita_service import buscar_receitas_por_usuario, update_receita_por_usuario, excluir_receita_por_usuario
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
            if 'categoria' in df_cat.columns:
                categorias_distintas = df_cat['categoria'].drop_duplicates().tolist()
            else:
                categorias_distintas = []
        else:
            categorias_distintas = []

        columnDefs = [
            {
                "headerName": "",
                "field": "check",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
                "headerCheckboxSelectionFilteredOnly": True,
            },
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

        tabela = html.Div(
            [
                dcc.Input(id="input-radio-row-selection-checkbox-header-filtered-only-receita", placeholder="Quick filter..."),
                dbc.Button("Excluir Selecionados", id="btn-row-selection-remove-receita", n_clicks=0, className="btn btn-danger"),
                dag.AgGrid(
                    id="tbl-receita",
                    rowData=df.to_dict("records"),
                    # columnDefs=[{"field": i} for i in df.columns],
                    columnDefs=columnDefs,
                    columnSize="sizeToFit",
                    defaultColDef={"editable": True, "filter": True, "resizable": True},
                    dashGridOptions={"animateRows": True, 'pagination':True, "rowSelection": "multiple"},
                )
            ], 
        )
        return tabela


    @dash_app.callback(
            [
                Output('alert-auto-receita', 'is_open', allow_duplicate=True), 
                Output('alert-auto-receita', 'children', allow_duplicate=True),
                Output("receitas-update-trigger", "data"),
            ],
            [
                Input('tbl-receita', 'cellValueChanged'),
            ],
            [
                State("alert-auto-receita", "is_open"),
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
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @dash_app.callback(
        Output("tbl-receita", "dashGridOptions"),
        Input("input-radio-row-selection-checkbox-header-filtered-only-receita", "value"),
    )
    def update_filter(filter_value):
        gridOptions_patch = Patch()
        gridOptions_patch["quickFilterText"] = filter_value
        return gridOptions_patch

    @dash_app.callback(
        Output("tbl-receita", "rowData", allow_duplicate=True),
        Output("alert-auto-receita", "is_open", allow_duplicate=True),
        Output("alert-auto-receita", "children", allow_duplicate=True),
        Output("alert-auto-receita", "color", allow_duplicate=True),
        Output("tbl-receita", "deleteSelectedRows", allow_duplicate=True),
        Output("receitas-update-trigger", "data", allow_duplicate=True),
        Input("btn-row-selection-remove-receita", "n_clicks"),
        State("tbl-receita", "rowData"),
        State("tbl-receita", "selectedRows"),
        State("receitas-update-trigger", "data"),
        prevent_initial_call=True
    )
    def excluir_receita(n_clicks, row_data, selected_rows, update_trigger):
        # print(f"Excluir receitas: n_clicks={n_clicks}, selected_rows={selected_rows}")
        if not n_clicks or not selected_rows:
            return row_data, True, "Nenhuma receita selecionada para exclusão.", "warning", False, update_trigger
        # IDs das receitas selecionadas
        ids_para_excluir = [row["id"] for row in selected_rows if "id" in row]
        if not ids_para_excluir:
            return row_data, True, "Nenhuma receita selecionada para exclusão.", "warning", False, update_trigger
        try:
            user_session = get_current_user_db_session()
            from app.services.receita_service import excluir_receita_por_usuario
            erros = []
            for receita_id in ids_para_excluir:
                success, message = excluir_receita_por_usuario(user_session, receita_id)
                if not success:
                    erros.append(message)
            # Remove as linhas excluídas da grid
            row_data = [row for row in row_data if row["id"] not in ids_para_excluir]
            if erros:
                return row_data, True, f"Algumas receitas não foram excluídas: {'; '.join(erros)}", "warning", False, update_trigger
            # Se todas as receitas foram excluídas com sucesso
            return row_data, True, "Receitas excluídas com sucesso!", "success", True, update_trigger + 1
        except Exception as e:
            return row_data, True, f"Erro: {str(e)}", "danger", False, update_trigger