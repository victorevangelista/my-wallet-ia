from dash.dependencies import Input, Output, State
from dash import no_update
from app.services.despesa_service import buscar_despesas
from app.services.receita_service import buscar_receitas
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


graph_margin = dict(l=25, r=25, t=25, b=0)

def register_callbacks(dash_app):
    @dash_app.callback(
        [
            Output("dropdown-despesa", "options"),
            Output("dropdown-despesa", "value"),
            Output("p-despesa-dashboard", "children")
        ],
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname")
        ]
    )
    def populate_dropdown_despesas(start_date, end_date, _):
        despesas = buscar_despesas()
        df = pd.DataFrame(despesas)

        if df.empty:
            return no_update, no_update, "R$ 0,00"  # Retorna zero se não houver dados

        # Converter a coluna "data" para datetime
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

        # Converter datas do filtro
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filtrar pela data
        df = df[(df["data"] >= start_date) & (df["data"] <= end_date)]

        # Calcular soma correta
        valor = df["valor"].sum()

        # Criar dropdown de categorias únicas
        val = df["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in val]

        return dropdown_options, val, f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # Formata número
    

    @dash_app.callback(
        [
            Output("dropdown-receita", "options"),
            Output("dropdown-receita", "value"),
            Output("p-receita-dashboard", "children")
        ],
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname")
        ]
    )
    def populate_dropdown_receitas(start_date, end_date, _):
        receitas = buscar_receitas()
        df = pd.DataFrame(receitas)

        if df.empty:
            return no_update, no_update, "R$ 0,00"  # Retorna zero se não houver dados

        # Converter a coluna "data" para datetime
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

        # Converter datas do filtro
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filtrar pela data
        df = df[(df["data"] >= start_date) & (df["data"] <= end_date)]

        # Calcular soma correta
        valor = df["valor"].sum()

        # Criar dropdown de categorias únicas
        val = df["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in val]

        return dropdown_options, val, f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # Formata número
    
    @dash_app.callback(
        Output("p-saldo-dashboard", "children"),
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname")
        ]
    )
    def refresh_saldo(start_date, end_date, _):
        receitas = buscar_receitas()
        df_receita = pd.DataFrame(receitas)

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        df_receita["data"] = pd.to_datetime(df_receita["data"])
        df_receita = df_receita[(df_receita["data"] >= start_date) & (df_receita["data"] <= end_date)]
        
        despesas = buscar_despesas()
        df_despesa = pd.DataFrame(despesas)

        df_despesa["data"] = pd.to_datetime(df_despesa["data"])
        df_despesa = df_despesa[(df_despesa["data"] >= start_date) & (df_despesa["data"] <= end_date)]

        valor = df_receita['valor'].sum() - df_despesa['valor'].sum()

        return f"R$ {valor:.2f}"
    

    @dash_app.callback(
        Output("graph1", "figure"),
        [
            Input("dropdown-receita", "value"),
            Input("dropdown-despesa", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date")
        ]
    )
    def update_graph_cashflow(receita, despesa, start_date, end_date):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        receitas = buscar_receitas()
        df_receita = pd.DataFrame(receitas)
        df_receita["data"] = pd.to_datetime(df_receita["data"])
        df_receita = df_receita[(df_receita["data"] >= start_date) & (df_receita["data"] <= end_date)]
        df_receita = df_receita[df_receita["categoria"].isin(receita)]
        df_receita = df_receita.set_index("data")[["valor"]]
        df_rc = df_receita.groupby("data").sum().rename(columns={"valor": "receita"})

        despesas = buscar_despesas()
        df_despesa = pd.DataFrame(despesas)
        df_despesa["data"] = pd.to_datetime(df_despesa["data"])
        df_despesa = df_despesa[(df_despesa["data"] >= start_date) & (df_despesa["data"] <= end_date)]
        df_despesa = df_despesa[df_despesa["categoria"].isin(despesa)]
        df_despesa = df_despesa.set_index("data")[["valor"]]
        df_dp = df_despesa.groupby("data").sum().rename(columns={"valor": "despesa"})

        df_acum = df_dp.join(df_rc, how="outer").fillna(0)
        df_acum["acum"] = df_acum["receita"] - df_acum["despesa"]
        df_acum["acum"] = df_acum["acum"].cumsum()

        fig = go.Figure()
        fig.add_trace(go.Scatter(name="Fluxo de caixa", x=df_acum.index, y=df_acum["acum"], mode="lines"))

        fig.update_layout(margin=graph_margin, height=300)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig
    
    @dash_app.callback(
        Output("graph2", "figure"),
        [
            Input("dropdown-receita", "value"),
            Input("dropdown-despesa", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date")
        ]
    )
    def update_graph2(receita, despesa, start_date, end_date):
        data_receita = buscar_receitas()
        df_receita = pd.DataFrame(data_receita)
        data_despesa = buscar_despesas()
        df_despesa = pd.DataFrame(data_despesa)

        df_receita["Output"] = "Receitas"
        df_despesa["Output"] = "Despesas"
        df_final = pd.concat([df_receita, df_despesa])
        df_final["data"] = pd.to_datetime(df_final["data"])

        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        df_final = df_final[(df_final["data"] >= start_date) & (df_final["data"] <= end_date)]
        df_final = df_final[(df_final["categoria"].isin(receita)) | (df_final["categoria"].isin(despesa))]
        
        fig = px.bar(df_final, x="data", y="valor", color="Output", barmode="group")

        fig.update_layout(margin=graph_margin, height=300)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    @dash_app.callback(
        Output("graph3", "figure"),
        [
            Input("dropdown-receita", "value")
        ]
    )
    def update_graph_receita(receita):
        data_receita = buscar_receitas()
        df_receita = pd.DataFrame(data_receita)
        df_receita = df_receita[df_receita["categoria"].isin(receita)]
        
        fig = px.pie(df_receita, values=df_receita.valor, names=df_receita.categoria, hole=.2)

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

    @dash_app.callback(
        Output("graph4", "figure"),
        [
            Input("dropdown-despesa", "value")
        ]
    )
    def update_graph_despesa(despesa):
        data_despesa = buscar_despesas()
        df_despesa = pd.DataFrame(data_despesa)
        df_despesa = df_despesa[df_despesa["categoria"].isin(despesa)]
        
        fig = px.pie(df_despesa, values=df_despesa.valor, names=df_despesa.categoria, hole=.2)

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