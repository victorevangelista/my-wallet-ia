from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from app.services.despesa_service import buscar_despesas, update_despesa
from app.services.categoria_service import buscar_cat_despesas

def register_callbacks(dash_app):
    @dash_app.callback(
        Output('tabela-despesas', 'children'),
        Input("base-url", "pathname")
    )
    def imprimir_tabela(_):
        despesas = buscar_despesas()
        df = pd.DataFrame(despesas)
        df['data'] = pd.to_datetime(df['data']).dt.date
        df = df.fillna('-')
        df.sort_values(by='data', ascending=False)

        success, despesa_cat = buscar_cat_despesas()
        if success:
            df_cat = pd.DataFrame(despesa_cat)
            # Lista de categorias distintas
            categorias_distintas = df_cat['descricao'].drop_duplicates().tolist()
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
                id="tbl-despesa",
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
                Output('alert-auto', 'children', allow_duplicate=True)
            ],
            [
                Input('tbl-despesa', 'cellValueChanged'),
            ],
            [
                State("alert-auto", "is_open"),
            ],
            prevent_initial_call='initial_duplicate'
        )
    def update_data(cell_changed, is_open ):
        if cell_changed:
            id = cell_changed[0]['data']['id']
            descricao = cell_changed[0]['data']['descricao']
            valor = round(float(cell_changed[0]['data']['valor']), 2)
            data = pd.to_datetime(cell_changed[0]['data']['data']).date()
            categoria = cell_changed[0]['data']['categoria']
            parcelado = cell_changed[0]['data']['parcelado']
            fixo = cell_changed[0]['data']['fixo']

            success, result = update_despesa(id, descricao, categoria, data, valor, parcelado, fixo)

            return not is_open, f"{result} Linha: {cell_changed[0]['rowId']}" if success else result
        return (is_open, "Edite a tabela")


    @dash_app.callback(
        Output('bar-graph-despesas', 'figure'),
        Input("base-url", "pathname"),
    )
    def bar_graph(_):
        despesas = buscar_despesas()
        df = pd.DataFrame(despesas)
        df_grouped = df.groupby("categoria").sum()[["valor"]].reset_index()
        graph = px.bar(df_grouped, x="categoria", y="valor", title="Despesas Gerais")
        graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return graph

    @dash_app.callback(
        Output('valor-despesas-card', 'children'),
        Input("base-url", "pathname"),
    )
    def display_desp(_):
        despesas = buscar_despesas()
        df = pd.DataFrame(despesas)
        valor = df['valor'].sum()
        return f"R$ {valor:.2f}"