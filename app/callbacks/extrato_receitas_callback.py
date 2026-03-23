from dash.dependencies import Input, Output, State, ALL
import dash_ag_grid as dag
from dash import dcc, html, Patch, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Importações atualizadas
from app.services.receita_service import buscar_receitas_por_usuario, update_receita_por_usuario, excluir_receita_por_usuario
from app.services.categoria_service import buscar_cat_receitas_por_usuario
from flask_login import current_user
from app import get_current_user_db_session

def get_filtered_receitas_df(user_session, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao):
    from app.callbacks.dashboard_callbacks import filtrar_df_por_filtros_extras
    receitas_data = buscar_receitas_por_usuario(user_session)
    df = pd.DataFrame(receitas_data)
    if df.empty:
        return df

    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y', errors='coerce')
    df.dropna(subset=['data'], inplace=True)
    
    if start_date and end_date:
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
        df = df[(df["data"] >= start_date_dt) & (df["data"] <= end_date_dt)]
        
    df = filtrar_df_por_filtros_extras(df, filtro_recorrentes, filtro_cartao)
    
    if receita_cats_selected:
        df = df[df["categoria"].isin(receita_cats_selected)]
        
    return df

def register_callbacks(dash_app):
    @dash_app.callback(
        Output({'page': 'receitas', 'type': 'extrato-grid', 'id': ALL}, 'children'),
        [
            Input("base-url", "pathname"),
            Input("store-receitas", "data"),
            Input("dropdown-receita", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value")
        ]
    )
    def imprimir_tabela(pathname, store_receitas, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao):
        outputs = callback_context.outputs_list
        if not outputs or (isinstance(outputs, list) and not outputs[0]): return []
        
        if not current_user.is_authenticated:
            return [html.Div("Por favor, faça login para ver as receitas.")]

        user_session = get_current_user_db_session()
        if not user_session:
            return [html.Div("Erro ao carregar dados do usuário.")]

        df = get_filtered_receitas_df(user_session, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao)
        if df.empty:
            return [html.Div("Nenhuma receita encontrada.")]

        df['data'] = df['data'].dt.date
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
                "headerName": "Cartão de Crédito",
                "field": "cartao_credito",
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
        return [tabela]


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
            cod = cell_changed[0]['data']['cod']
            descricao = cell_changed[0]['data']['descricao']
            valor = round(float(cell_changed[0]['data']['valor']), 2)
            data = pd.to_datetime(cell_changed[0]['data']['data']).date()
            categoria = cell_changed[0]['data']['categoria']
            cartao_credito_val = cell_changed[0]['data']['cartao_credito']
            fixo_val = cell_changed[0]['data']['fixo']

            # Certifique-se que cartao_credito e fixo sejam booleanos se necessário pelo modelo/serviço
            # Exemplo: cartao_credito = bool(cartao_credito_val)

            success, result = update_receita_por_usuario(user_session, id, cod, descricao, categoria, data, valor, cartao_credito_val, fixo_val)

            return not is_open, f"{result} Linha: {cell_changed[0]['rowId']}" if success else result, update_trigger + 1
        return is_open, "Edite a tabela", update_trigger 

    @dash_app.callback(
        Output({'page': 'receitas', 'type': 'extrato-graph', 'id': ALL}, 'figure'),
        [
            Input("receitas-update-trigger", "data"),
            Input("dropdown-receita", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value")
        ]
    )
    def bar_graph(trigger_data, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao):
        outputs = callback_context.outputs_list
        if not outputs or (isinstance(outputs, list) and not outputs[0]): return []
        
        if not current_user.is_authenticated:
            return [px.bar()]

        user_session = get_current_user_db_session()
        if not user_session:
            return [px.bar()]

        df = get_filtered_receitas_df(user_session, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao)
        if df.empty:
            return [px.bar(title="Receitas Gerais").update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')]

        df_grouped = df.groupby("categoria")[["valor"]].sum().reset_index()
        graph = px.bar(df_grouped, x="categoria", y="valor", title="Receitas Gerais")
        graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return [graph]

    @dash_app.callback(
        Output({'page': 'receitas', 'type': 'extrato-metric', 'id': ALL}, 'children'),
        [
            Input("receitas-update-trigger", "data"),
            Input("dropdown-receita", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value")
        ]
    )
    def display_receitas(trigger_data, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao):
        outputs = callback_context.outputs_list
        if not outputs or (isinstance(outputs, list) and not outputs[0]): return []
        
        if not current_user.is_authenticated:
            return ["R$ 0.00"]

        user_session = get_current_user_db_session()
        if not user_session:
            return ["R$ 0.00"]
            
        df = get_filtered_receitas_df(user_session, receita_cats_selected, start_date, end_date, filtro_recorrentes, filtro_cartao)
        if df.empty:
            return ["R$ 0.00"]
        valor = df['valor'].sum()
        return [f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")]
    
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