from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from globals import *
from app import app

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        html.Legend("Tabela de despesas"),
        dbc.Alert(
            id="alert-auto",
            is_open=False,
            duration=15000,
        ),
        html.Div(id='tabela-despesas', className='dbc')
    ], style={"marginRight": "10px"}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-graph-despesas', style={"marginRight": "20px"})
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Despesas"),
                    html.Legend("R$ -", id='valor-despesas-card', style={"fontSize": "40px"}),
                    html.H6("Total de despesas"),
                ], style={"textAlign": "center", "paddingTop": "30px"})
            )
        ], width=3)
    ], style={"marginTop": "20px"})


], style={"padding": "10px"} )

# =========  Callbacks  =========== #
# Tabela
@app.callback(
    Output('tabela-despesas', 'children'),
    Input('store-despesas', 'data'),
    State("store-cat-despesas", "data")
)
def imprimir_tabela(data, despesa_cat):
    df = pd.DataFrame(data)
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    df = df.fillna('-')
    df.sort_values(by='Data', ascending=False)

    df_cat = pd.DataFrame(despesa_cat)

    # Lista de categorias distintas
    categorias_distintas = df_cat['Categoria'].drop_duplicates().tolist()

    columnDefs = [
        {
            "headerName": "Descrição",
            "field": "Descrição",
            "cellEditor": "agTextCellEditor",
            "cellEditorParams": {
                "maxLength": 120,
            },
        },
        {
            "headerName": "Categoria",
            "field": "Categoria",
            "cellEditor": "agSelectCellEditor",
            "cellEditorParams": {
                "values": categorias_distintas,
            },
        },
        {
            "headerName": "Data",
            "field": "Data",
            "cellEditor": "agDateStringCellEditor",
        },
        {
            "headerName": "Valor",
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "field": "Valor",
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
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "field": "Parcelado",
            "cellEditor": "agNumberCellEditor",
            "cellEditorParams": {
                "precision": 0,
                "step": 1,
                "showStepperButtons": True,
                "min": 0,
                "max": 1,
            },
        },
        {
            "headerName": "Fixo",
            "wrapHeaderText": True,
            "autoHeaderHeight": True,
            "field": "Fixo",
            "cellEditor": "agNumberCellEditor",
            "cellEditorParams": {
                "precision": 0,
                "step": 1,
                "showStepperButtons": True,
                "min": 0,
                "max": 1,
            },
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


@app.callback(
        [
            Output('store-despesas', 'data', allow_duplicate=True),
            Output('alert-auto', 'is_open'), 
            Output('alert-auto', 'children')
        ],
        Input('tbl-despesa', 'cellValueChanged'),
        [
            State("alert-auto", "is_open"),
            State('store-despesas', 'data'),
        ],
        prevent_initial_call='initial_duplicate'
    )
def update_data(cell_changed, is_open, dict_despesas):
    df_despesas = pd.DataFrame(dict_despesas)

    if cell_changed:
        descricao = cell_changed[0]['data']['Descrição']
        valor = round(float(cell_changed[0]['data']['Valor']), 2)
        date = pd.to_datetime(cell_changed[0]['data']['Data']).date()
        categoria = cell_changed[0]['data']['Categoria']
        parcelado = cell_changed[0]['data']['Parcelado']
        fixo = cell_changed[0]['data']['Fixo']

        df_despesas.loc[cell_changed[0]['rowId']] = [descricao, categoria, date, valor, parcelado, fixo]
        df_despesas.to_csv(f"{path}/df_despesas.csv")
    
        data_return = df_despesas.to_dict()
        return (data_return, not is_open, f"Tabela editada com sucesso! Linha: {cell_changed[0]['rowId']}")
    data_return = df_despesas.to_dict()
    return (data_return, is_open, "Edite a tabela")


@app.callback(
    Output('bar-graph-despesas', 'figure'),
    Input('store-despesas', 'data')
)
def bar_graph(data):
    df = pd.DataFrame(data)
    df_grouped = df.groupby("Categoria").sum()[["Valor"]].reset_index()
    graph = px.bar(df_grouped, x="Categoria", y="Valor", title="Despesas Gerais")
    graph.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return graph

@app.callback(
    Output('valor-despesas-card', 'children'),
    Input('store-despesas', 'data')
)
def display_desp(data):
    df = pd.DataFrame(data)
    valor = df['Valor'].sum()
    return f"R$ {valor:.2f}"