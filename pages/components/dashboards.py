from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from globals import *
from app import app

card_icon = {
    "color": "white",
    "textAlign": "center",
    "fontSize": 30,
    "margin": "auto",
}

graph_margin = dict(l=25, r=25, t=25, b=0)
# Obter o primeiro dia do mês atual
today = datetime.today()
start_date = today.replace(day=1).date()

# =========  Layout  =========== #
layout = dbc.Col([
        dbc.Row([
            # Saldo total
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Saldo'),
                        html.H5('R$ 0', id='p-saldo-dashboard')
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-university', style=card_icon),
                        color='warning',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),

            # Receita 
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Receita'),
                        html.H5('R$ 0', id='p-receita-dashboard')
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-smile-o', style=card_icon),
                        color='success',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),

            #Despesa
            dbc.Col([
                dbc.CardGroup([
                    dbc.Card([
                        html.Label('Despesa'),
                        html.H5('R$ 0', id='p-despesa-dashboard')
                    ], style={"paddingLeft": "20px", "paddingTop": "10px"}),
                    dbc.Card(
                        html.Div(className='fa fa-meh-o', style=card_icon),
                        color='danger',
                        style={"maxWidth": 75, "height": 100, "marginLeft": "-10px"}
                    )
                ])
            ], width=4),
        ], style={"margin": "10px"}),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.Legend('Filtrar lançamentos', className='card-title'),
                    html.Label("Categoria das receitas"),
                    html.Div(
                        dcc.Dropdown(
                            id='dropdown-receita',
                            clearable=False,
                            style={"width": "100%"},
                            persistence=True,
                            persistence_type="session",
                            multi=True
                        )
                    ),
                    html.Label("Categoria das despesas", style={"marginTop": "10px"}),
                    html.Div(
                        dcc.Dropdown(
                            id='dropdown-despesa',
                            clearable=False,
                            style={"width": "100%"},
                            persistence=True,
                            persistence_type="session",
                            multi=True
                        )
                    ),

                    html.Legend('Período de análise', style={"marginTop": "10px"}),
                    dcc.DatePickerRange(
                        month_format='Do MMM, YY',
                        end_date_placeholder_text='Data...',
                        start_date=start_date,  # Definindo o primeiro dia do mês
                        end_date=datetime.today().date(),  # Ou qualquer outra data de término que você deseje
                        updatemode='singledate',
                        id='date-picker-config',
                        style={'zIndex': '100'}
                    )
                ], style={'height': '100%', "padding": "20px"})
            ], width=4),

            dbc.Col(
                dbc.Card(dcc.Graph(id='graph1'), style={'height': '100%', 'padding': '10px'}), width=8
            )
        ], style={"margin": "10px"}),

        dbc.Row([
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph2'), style={'height': '100%', 'padding': '10px'}), width=6
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph3'), style={'height': '100%', 'padding': '10px'}), width=3
            ),
            dbc.Col(
                dbc.Card(dcc.Graph(id='graph4'), style={'height': '100%', 'padding': '10px'}), width=3
            )
        ], style={"margin": "10px"})
       
    ])



# =========  Callbacks  =========== #
@app.callback(
    [
        Output("dropdown-receita", "options"),
        Output("dropdown-receita", "value"),
        Output("p-receita-dashboard", "children")
    ],
    [
        Input("store-receitas", "data"),
        Input("date-picker-config", "start_date"),
        Input("date-picker-config", "end_date")
    ]
)
def populate_dropdown_values(data, start_date, end_date):
    df = pd.DataFrame(data)
    df["Data"] = pd.to_datetime(df["Data"])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df = df[(df["Data"] >= start_date) & (df["Data"] <= end_date)]
    
    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()

    return ([{"label": i, "value": i} for i in val], val, f"R$ {valor:.2f}")


@app.callback(
    [
        Output("dropdown-despesa", "options"),
        Output("dropdown-despesa", "value"),
        Output("p-despesa-dashboard", "children")
    ],
    [
        Input("store-despesas", "data"),
        Input("date-picker-config", "start_date"),
        Input("date-picker-config", "end_date")
    ]
)
def populate_dropdown_values(data, start_date, end_date):
    df = pd.DataFrame(data)
    df["Data"] = pd.to_datetime(df["Data"])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df = df[(df["Data"] >= start_date) & (df["Data"] <= end_date)]

    valor = df['Valor'].sum()
    val = df.Categoria.unique().tolist()

    return ([{"label": i, "value": i} for i in val], val, f"R$ {valor:.2f}")


@app.callback(
    Output("p-saldo-dashboard", "children"),
    [
        Input("store-receitas", "data"),
        Input("store-despesas", "data"),
        Input("date-picker-config", "start_date"),
        Input("date-picker-config", "end_date")
    ]
)
def refresh_saldo(receitas, despesas, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_receita = pd.DataFrame(receitas)
    df_receita["Data"] = pd.to_datetime(df_receita["Data"])
    df_receita = df_receita[(df_receita["Data"] >= start_date) & (df_receita["Data"] <= end_date)]
    
    df_despesa = pd.DataFrame(despesas)
    df_despesa["Data"] = pd.to_datetime(df_despesa["Data"])
    df_despesa = df_despesa[(df_despesa["Data"] >= start_date) & (df_despesa["Data"] <= end_date)]

    valor = df_receita['Valor'].sum() - df_despesa['Valor'].sum()

    return f"R$ {valor:.2f}"


@app.callback(
    Output("graph1", "figure"),
    [
        Input("store-receitas", "data"),
        Input("store-despesas", "data"),
        Input("dropdown-receita", "value"),
        Input("dropdown-despesa", "value"),
        Input("date-picker-config", "start_date"),
        Input("date-picker-config", "end_date")
    ]
)
def update_graph_cashflow(data_receita, data_despesa, receita, despesa, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    df_receita = pd.DataFrame(data_receita)
    df_receita["Data"] = pd.to_datetime(df_receita["Data"])
    df_receita = df_receita[(df_receita["Data"] >= start_date) & (df_receita["Data"] <= end_date)]
    df_receita = df_receita[df_receita["Categoria"].isin(receita)]
    df_receita = df_receita.set_index("Data")[["Valor"]]
    df_rc = df_receita.groupby("Data").sum().rename(columns={"Valor": "Receita"})

    df_despesa = pd.DataFrame(data_despesa)
    df_despesa["Data"] = pd.to_datetime(df_despesa["Data"])
    df_despesa = df_despesa[(df_despesa["Data"] >= start_date) & (df_despesa["Data"] <= end_date)]
    df_despesa = df_despesa[df_despesa["Categoria"].isin(despesa)]
    df_despesa = df_despesa.set_index("Data")[["Valor"]]
    df_dp = df_despesa.groupby("Data").sum().rename(columns={"Valor": "Despesa"})

    df_acum = df_dp.join(df_rc, how="outer").fillna(0)
    df_acum["Acum"] = df_acum["Receita"] - df_acum["Despesa"]
    df_acum["Acum"] = df_acum["Acum"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(name="Fluxo de caixa", x=df_acum.index, y=df_acum["Acum"], mode="lines"))

    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

@app.callback(
    Output("graph2", "figure"),
    [
        Input("store-receitas", "data"),
        Input("store-despesas", "data"),
        Input("dropdown-receita", "value"),
        Input("dropdown-despesa", "value"),
        Input("date-picker-config", "start_date"),
        Input("date-picker-config", "end_date")
    ]
)
def update_graph2(data_receita, data_despesa, receita, despesa, start_date, end_date):
    df_receita = pd.DataFrame(data_receita)
    df_despesa = pd.DataFrame(data_despesa)

    df_receita["Output"] = "Receitas"
    df_despesa["Output"] = "Despesas"
    df_final = pd.concat([df_receita, df_despesa])
    df_final["Data"] = pd.to_datetime(df_final["Data"])

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df_final = df_final[(df_final["Data"] >= start_date) & (df_final["Data"] <= end_date)]
    df_final = df_final[(df_final["Categoria"].isin(receita)) | (df_final["Categoria"].isin(despesa))]
    
    fig = px.bar(df_final, x="Data", y="Valor", color="Output", barmode="group")

    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

@app.callback(
    Output("graph3", "figure"),
    [
        Input("store-receitas", "data"),
        Input("dropdown-receita", "value")
    ]
)
def update_graph_receita(data_receita, receita):
    df_receita = pd.DataFrame(data_receita)
    df_receita = df_receita[df_receita["Categoria"].isin(receita)]
    
    fig = px.pie(df_receita, values=df_receita.Valor, names=df_receita.Categoria, hole=.2)

    fig.update_layout(title={"text": "Receitas"})
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Definindo a legenda abaixo do gráfico
    fig.update_layout(
        legend=dict(
            orientation='h',  # Orientação horizontal
            yanchor='top',    # Alinhar a legenda na parte superior
            y=-0.2,           # Posição da legenda abaixo do gráfico
            xanchor='center', # Alinhar a legenda ao centro
            x=0.5             # Centralizar a legenda
        )
    )
    
    return fig

@app.callback(
    Output("graph4", "figure"),
    [
        Input("store-despesas", "data"),
        Input("dropdown-despesa", "value")
    ]
)
def update_graph_despesa(data_despesa, despesa):
    df_despesa = pd.DataFrame(data_despesa)
    df_despesa = df_despesa[df_despesa["Categoria"].isin(despesa)]
    
    fig = px.pie(df_despesa, values=df_despesa.Valor, names=df_despesa.Categoria, hole=.2)

    fig.update_layout(title={"text": "Despesas"})
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # Definindo a legenda abaixo do gráfico
    fig.update_layout(
        legend=dict(
            orientation='h',  # Orientação horizontal
            yanchor='top',    # Alinhar a legenda na parte superior
            y=-0.2,           # Posição da legenda abaixo do gráfico
            xanchor='center', # Alinhar a legenda ao centro
            x=0.5             # Centralizar a legenda
        )
    )

    return fig