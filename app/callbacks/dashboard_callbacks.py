from dash.dependencies import Input, Output, State
from dash import no_update
# Importe os serviços refatorados
from app.services.despesa_service import buscar_despesas_por_usuario
from app.services.receita_service import buscar_receitas_por_usuario
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from flask_login import current_user
from app import get_current_user_db_session


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
    def populate_dropdown_despesas(start_date, end_date, pathname):
        if not current_user.is_authenticated:
            return [], [], "R$ 0,00"
        
        user_session = get_current_user_db_session()
        if not user_session:
            # Adicionar log ou tratamento de erro se a sessão não for encontrada
            return [], [], "R$ 0,00"

        despesas_data = buscar_despesas_por_usuario(user_session)
        if not despesas_data: # Checa se a lista está vazia (retorno em caso de erro ou sem dados)
            return [], [], "R$ 0,00"

        df = pd.DataFrame(despesas_data)
        if df.empty:
            return [], [], "R$ 0,00"

        # Converter a coluna "data" para datetime
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors='coerce')
        df.dropna(subset=['data'], inplace=True) # Remove linhas onde a conversão de data falhou

        # Converter datas do filtro
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        # Filtrar pela data
        df_filtered = df[(df["data"] >= start_date_dt) & (df["data"] <= end_date_dt)]

        # Calcular soma correta
        valor = df_filtered["valor"].sum()

        # Criar dropdown de categorias únicas
        val = df_filtered["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in val if pd.notna(i)]

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
    def populate_dropdown_receitas(start_date, end_date, pathname):
        if not current_user.is_authenticated:
            return [], [], "R$ 0,00"
        
        user_session = get_current_user_db_session()
        if not user_session:
            return [], [], "R$ 0,00"

        receitas_data = buscar_receitas_por_usuario(user_session)
        if not receitas_data:
            return [], [], "R$ 0,00"
            
        df = pd.DataFrame(receitas_data)
        if df.empty:
            return [], [], "R$ 0,00"

        # Converter a coluna "data" para datetime
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors='coerce')
        df.dropna(subset=['data'], inplace=True)

        # Converter datas do filtro
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        # Filtrar pela data
        df_filtered = df[(df["data"] >= start_date_dt) & (df["data"] <= end_date_dt)]

        # Calcular soma correta
        valor = df_filtered["valor"].sum()

        # Criar dropdown de categorias únicas
        val = df_filtered["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in val if pd.notna(i)]

        return dropdown_options, val, f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # Formata número
    
    @dash_app.callback(
        Output("p-saldo-dashboard", "children"),
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname")
        ]
    )
    def refresh_saldo(start_date, end_date, pathname):
        if not current_user.is_authenticated:
            return "R$ 0,00"
        
        user_session = get_current_user_db_session()
        if not user_session:
            return "R$ 0,00"

        receitas_data = buscar_receitas_por_usuario(user_session)
        df_receita = pd.DataFrame(receitas_data)
        
        despesas_data = buscar_despesas_por_usuario(user_session)
        df_despesa = pd.DataFrame(despesas_data)

        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        soma_receitas = 0
        if not df_receita.empty:
            df_receita["data"] = pd.to_datetime(df_receita["data"], format="%d/%m/%Y", errors='coerce')
            df_receita.dropna(subset=['data'], inplace=True)
            df_receita = df_receita[(df_receita["data"] >= start_date_dt) & (df_receita["data"] <= end_date_dt)]
            soma_receitas = df_receita['valor'].sum()

        soma_despesas = 0
        if not df_despesa.empty:
            df_despesa["data"] = pd.to_datetime(df_despesa["data"], format="%d/%m/%Y", errors='coerce')
            df_despesa.dropna(subset=['data'], inplace=True)
            df_despesa = df_despesa[(df_despesa["data"] >= start_date_dt) & (df_despesa["data"] <= end_date_dt)]
            soma_despesas = df_despesa['valor'].sum()
            
        valor = soma_receitas - soma_despesas

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
    def update_graph_cashflow(receita_cats_selected, despesa_cats_selected, start_date, end_date):
        fig = go.Figure()
        fig.update_layout(margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        if not current_user.is_authenticated:
            return fig
        
        user_session = get_current_user_db_session()
        if not user_session:
            return fig

        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        receitas_data = buscar_receitas_por_usuario(user_session)
        df_receita = pd.DataFrame(receitas_data)
        if not df_receita.empty:
            df_receita["data"] = pd.to_datetime(df_receita["data"], format="%d/%m/%Y", errors='coerce')
            df_receita.dropna(subset=['data'], inplace=True)
            df_receita = df_receita[(df_receita["data"] >= start_date_dt) & (df_receita["data"] <= end_date_dt)]
            if receita_cats_selected: # Checa se a lista não está vazia
                 df_receita = df_receita[df_receita["categoria"].isin(receita_cats_selected)]
            df_receita = df_receita.set_index("data")[["valor"]]
            df_rc = df_receita.groupby(level="data").sum().rename(columns={"valor": "receita"})
        else:
            df_rc = pd.DataFrame(columns=["receita"])

        despesas_data = buscar_despesas_por_usuario(user_session)
        df_despesa = pd.DataFrame(despesas_data)
        if not df_despesa.empty:
            df_despesa["data"] = pd.to_datetime(df_despesa["data"], format="%d/%m/%Y", errors='coerce')
            df_despesa.dropna(subset=['data'], inplace=True)
            df_despesa = df_despesa[(df_despesa["data"] >= start_date_dt) & (df_despesa["data"] <= end_date_dt)]
            if despesa_cats_selected: # Checa se a lista não está vazia
                df_despesa = df_despesa[df_despesa["categoria"].isin(despesa_cats_selected)]
            df_despesa = df_despesa.set_index("data")[["valor"]]
            df_dp = df_despesa.groupby(level="data").sum().rename(columns={"valor": "despesa"})
        else:
            df_dp = pd.DataFrame(columns=["despesa"])

        df_acum = df_dp.join(df_rc, how="outer").fillna(0)
        if not df_acum.empty:
            df_acum["acum"] = df_acum["receita"] - df_acum["despesa"]
            df_acum["acum"] = df_acum["acum"].cumsum()
            fig.add_trace(go.Scatter(name="Fluxo de caixa", x=df_acum.index, y=df_acum["acum"], mode="lines"))
        
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
    def update_graph2(receita_cats_selected, despesa_cats_selected, start_date, end_date):
        fig = px.bar() 
        fig.update_layout(margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

        if not current_user.is_authenticated:
            return fig
        
        user_session = get_current_user_db_session()
        if not user_session:
            return fig

        receitas_data = buscar_receitas_por_usuario(user_session)
        df_receita = pd.DataFrame(receitas_data)
        
        despesas_data = buscar_despesas_por_usuario(user_session)
        df_despesa = pd.DataFrame(despesas_data)

        if not df_receita.empty:
            df_receita["Output"] = "Receitas"
        if not df_despesa.empty:
            df_despesa["Output"] = "Despesas"
        
        df_final = pd.concat([df_receita, df_despesa])
        if df_final.empty:
            return fig

        df_final["data"] = pd.to_datetime(df_final["data"], format="%d/%m/%Y", errors='coerce')
        df_final.dropna(subset=['data'], inplace=True)

        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)

        df_final = df_final[(df_final["data"] >= start_date_dt) & (df_final["data"] <= end_date_dt)]
        
        # Garante que receita_cats_selected e despesa_cats_selected sejam listas antes de usar isin
        filter_receitas = df_final["categoria"].isin(receita_cats_selected if receita_cats_selected else []) & (df_final["Output"] == "Receitas")
        filter_despesas = df_final["categoria"].isin(despesa_cats_selected if despesa_cats_selected else []) & (df_final["Output"] == "Despesas")
        df_final = df_final[filter_receitas | filter_despesas]
        
        if not df_final.empty:
            fig = px.bar(df_final, x="data", y="valor", color="Output", barmode="group")
            fig.update_layout(margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        return fig

    @dash_app.callback(
        Output("graph3", "figure"),
        [
            Input("dropdown-receita", "value")
        ]
    )
    def update_graph_receita(receita_cats_selected): # Removido start_date, end_date se não for usar
        fig = px.pie(hole=.2)
        fig.update_layout(title={"text": "Receitas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

        if not current_user.is_authenticated:
            return fig
        
        user_session = get_current_user_db_session()
        if not user_session:
            return fig

        receitas_data = buscar_receitas_por_usuario(user_session)
        df_receita = pd.DataFrame(receitas_data)

        if df_receita.empty or not receita_cats_selected:
            return fig
        
        # Não precisa filtrar por data aqui se não for um Input
        # df_receita["data"] = pd.to_datetime(df_receita["data"], format="%d/%m/%Y", errors='coerce')
        # df_receita.dropna(subset=['data'], inplace=True)
        # start_date_dt = pd.to_datetime(start_date)
        # end_date_dt = pd.to_datetime(end_date)
        # df_receita = df_receita[(df_receita["data"] >= start_date_dt) & (df_receita["data"] <= end_date_dt)]

        df_receita = df_receita[df_receita["categoria"].isin(receita_cats_selected)]
        
        if not df_receita.empty:
            fig = px.pie(df_receita, values="valor", names="categoria", hole=.2)
            fig.update_layout(title={"text": "Receitas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

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
    def update_graph_despesa(despesa_cats_selected): # Removido start_date, end_date se não for usar
        fig = px.pie(hole=.2)
        fig.update_layout(title={"text": "Despesas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

        if not current_user.is_authenticated:
            return fig
            
        user_session = get_current_user_db_session()
        if not user_session:
            return fig

        despesas_data = buscar_despesas_por_usuario(user_session)
        df_despesa = pd.DataFrame(despesas_data)

        if df_despesa.empty or not despesa_cats_selected:
            return fig

        # Não precisa filtrar por data aqui se não for um Input
        
        df_despesa = df_despesa[df_despesa["categoria"].isin(despesa_cats_selected)]
        
        if not df_despesa.empty:
            fig = px.pie(df_despesa, values="valor", names="categoria", hole=.2)
            fig.update_layout(title={"text": "Despesas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

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