from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from dash import dcc
from dash import html, Patch
from dash import ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd



# Importações atualizadas
from app.services.despesa_service import buscar_despesas_por_usuario, update_despesa_por_usuario, excluir_despesa_por_usuario
from app.services.categoria_service import buscar_cat_despesas_por_usuario
from flask_login import current_user
from app import get_current_user_db_session

def register_callbacks(dash_app):
    @dash_app.callback(
        Output('tabela-despesas', 'children'),
        Input("base-url", "pathname")
    )
    def imprimir_tabela(pathname):
        if not current_user.is_authenticated:
            return html.Div("Por favor, faça login para ver as despesas.")

        user_session = get_current_user_db_session()
        if not user_session:
            return html.Div("Erro ao carregar dados do usuário.")

        despesas_data = buscar_despesas_por_usuario(user_session)
        df = pd.DataFrame(despesas_data)
        if df.empty:
            return html.Div("Nenhuma despesa encontrada.")
            
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce').dt.date
        df = df.fillna('-')
        df = df.sort_values(by='data', ascending=False) # Atribuir o resultado da ordenação
        success, despesa_cat = buscar_cat_despesas_por_usuario(user_session)
        if success:
            df_cat = pd.DataFrame(despesa_cat)
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
                dcc.Input(id="input-radio-row-selection-checkbox-header-filtered-only", placeholder="Quick filter..."),
                dbc.Button("Excluir Selecionados", id="btn-row-selection-remove", n_clicks=0, className="btn btn-danger"),
                dag.AgGrid(
                        id="tbl-despesa",
                        rowData=df.to_dict("records"),
                        # columnDefs=[{"field": i} for i in df.columns],
                        columnDefs=columnDefs,
                        columnSize="sizeToFit",
                        defaultColDef={"editable": True, "filter": True, "resizable": True},
                        dashGridOptions={"animateRows": True, 'pagination':True, "rowSelection": "multiple"},
                    )
            ]
        )   
        return tabela


    @dash_app.callback(
            [
                Output('alert-auto', 'is_open', allow_duplicate=True), 
                Output('alert-auto', 'children', allow_duplicate=True),
                Output("despesas-update-trigger", "data"),
            ],
            [
                Input('tbl-despesa', 'cellValueChanged'),
            ],
            [
                State("alert-auto", "is_open"),
                State("despesas-update-trigger", "data")
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

            success, result = update_despesa_por_usuario(user_session, id, descricao, categoria, data, valor, parcelado_val, fixo_val)

            return not is_open, f"{result} Linha: {cell_changed[0]['rowId']}" if success else result, update_trigger + 1
        return is_open, "Edite a tabela", update_trigger

    @dash_app.callback(
        Output('bar-graph-despesas', 'figure'),
        Input("despesas-update-trigger", "data"),
    )
    def bar_graph(trigger_data):
        if not current_user.is_authenticated:
            return px.bar() # Retorna gráfico vazio

        user_session = get_current_user_db_session()
        if not user_session:
            return px.bar()

        despesas_data = buscar_despesas_por_usuario(user_session)
        df = pd.DataFrame(despesas_data)
        if df.empty:
            return px.bar(title="Despesas Gerais").update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        df_grouped = df.groupby("categoria").sum()[["valor"]].reset_index()
        graph = px.bar(df_grouped, x="categoria", y="valor", title="Despesas Gerais")
        graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return graph

    @dash_app.callback(
        Output('valor-despesas-card', 'children'),
        Input("despesas-update-trigger", "data"),
    )
    def display_desp(trigger_data):
        if not current_user.is_authenticated:
            return "R$ 0.00"

        user_session = get_current_user_db_session()
        if not user_session:
            return "R$ 0.00"
            
        despesas_data = buscar_despesas_por_usuario(user_session)
        df = pd.DataFrame(despesas_data)
        if df.empty:
            return "R$ 0.00"
        valor = df['valor'].sum()
        return f"R$ {valor:.2f}"
    

    @dash_app.callback(
        Output("tbl-despesa", "dashGridOptions"),
        Input("input-radio-row-selection-checkbox-header-filtered-only", "value"),
    )
    def update_filter(filter_value):
        gridOptions_patch = Patch()
        gridOptions_patch["quickFilterText"] = filter_value
        return gridOptions_patch

    @dash_app.callback(
        Output("tbl-despesa", "rowData"),
        Output("alert-auto", "is_open", allow_duplicate=True),
        Output("alert-auto", "children", allow_duplicate=True),
        Output("alert-auto", "color", allow_duplicate=True),
        Output("tbl-despesa", "deleteSelectedRows"),
        Output("despesas-update-trigger", "data", allow_duplicate=True),
        Input("btn-row-selection-remove", "n_clicks"),
        State("tbl-despesa", "rowData"),
        State("tbl-despesa", "selectedRows"),
        State("despesas-update-trigger", "data"),
        prevent_initial_call=True
    )
    def excluir_despesa(n_clicks, row_data, selected_rows, update_trigger):
        # print(f"Excluir despesas: n_clicks={n_clicks}, selected_rows={selected_rows}")
        if not n_clicks or not selected_rows:
            return row_data, True, "Nenhuma despesa selecionada para exclusão.", "warning", False, update_trigger
        # IDs das despesas selecionadas
        ids_para_excluir = [row["id"] for row in selected_rows if "id" in row]
        if not ids_para_excluir:
            return row_data, True, "Nenhuma despesa selecionada para exclusão.", "warning", False, update_trigger
        try:
            user_session = get_current_user_db_session()
            
            erros = []
            for despesa_id in ids_para_excluir:
                success, message = excluir_despesa_por_usuario(user_session, despesa_id)
                if not success:
                    erros.append(message)
            # Remove as linhas excluídas da grid
            row_data = [row for row in row_data if row["id"] not in ids_para_excluir]
            if erros:
                return row_data, True, f"Algumas despesas não foram excluídas: {'; '.join(erros)}", "warning", False, update_trigger
            # Se todas as despesas foram excluídas com sucesso
            return row_data, True, "Despesas excluídas com sucesso!", "success", True, update_trigger + 1
        except Exception as e:
            return row_data, True, f"Erro: {str(e)}", "danger", False, update_trigger