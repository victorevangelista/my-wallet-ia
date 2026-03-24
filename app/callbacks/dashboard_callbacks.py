from dash.dependencies import Input, Output, State, ALL
from dash import no_update, callback_context
# Importe os serviços refatorados
from app.services.despesa_service import buscar_despesas_por_usuario
from app.services.receita_service import buscar_receitas_por_usuario
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from flask_login import current_user
from app import get_current_user_db_session

pd.set_option('future.no_silent_downcasting', True)

def filtrar_df_por_filtros_extras(df, filtro_recorrentes, filtro_cartao):
    if df.empty:
        return df
    
    # Criar uma cópia para evitar SettingWithCopyWarning
    df = df.copy()
    
    if 'fixo' not in df.columns: df.loc[:, 'fixo'] = False
    if 'cartao_credito' not in df.columns: df.loc[:, 'cartao_credito'] = False
    
    df.loc[:, 'fixo'] = df['fixo'].fillna(False).astype(bool)
    df.loc[:, 'cartao_credito'] = df['cartao_credito'].fillna(False).astype(bool)
    
    if filtro_recorrentes == "recorrente":
        df = df[df['fixo'] == True]
    elif filtro_recorrentes == "nao_recorrente":
        df = df[df['fixo'] == False]
        
    if filtro_cartao == "cartao_credito":
        df = df[df['cartao_credito'] == True]
    elif filtro_cartao == "outros":
        df = df[df['cartao_credito'] == False]
        
    return df


graph_margin = dict(l=25, r=25, t=25, b=0)
    
def register_callbacks(dash_app):

    @dash_app.callback(
        Output({'page': 'dashboard', 'type': 'dash-metric', 'id': ALL}, "children"),
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("dropdown-receita", "value"),
            Input("dropdown-despesa", "value"),
            Input("base-url", "pathname"),
            Input("store-receitas", "data"),
            Input("store-despesas", "data"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value")
        ]
    )
    def update_dashboard_metrics(start_date, end_date, receita_cats, despesa_cats, pathname, store_receitas, store_despesas, filtro_recorrentes, filtro_cartao):
        outputs = callback_context.outputs_list
        if not outputs or (isinstance(outputs, list) and not outputs[0]):
            return []
            
        if not current_user.is_authenticated:
            return ["R$ 0,00"] * len(outputs)
        
        user_session = get_current_user_db_session()
        if not user_session:
            return ["R$ 0,00"] * len(outputs)
 
        # Buscar dados
        receitas_data = buscar_receitas_por_usuario(user_session)
        despesas_data = buscar_despesas_por_usuario(user_session)
        
        df_receita = pd.DataFrame(receitas_data)
        df_despesa = pd.DataFrame(despesas_data)
 
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
 
        # Processar Receitas
        soma_receitas = 0
        if not df_receita.empty:
            df_receita["data"] = pd.to_datetime(df_receita["data"], format="%d/%m/%Y", errors='coerce')
            df_receita.dropna(subset=['data'], inplace=True)
            df_receita = df_receita[(df_receita["data"] >= start_date_dt) & (df_receita["data"] <= end_date_dt)]
            df_receita = filtrar_df_por_filtros_extras(df_receita, filtro_recorrentes, filtro_cartao)
            
            # Filtro de categorias
            if receita_cats:
                df_receita = df_receita[df_receita["categoria"].isin(receita_cats)]
                
            soma_receitas = df_receita['valor'].sum()
 
        # Processar Despesas
        soma_despesas = 0
        if not df_despesa.empty:
            df_despesa["data"] = pd.to_datetime(df_despesa["data"], format="%d/%m/%Y", errors='coerce')
            df_despesa.dropna(subset=['data'], inplace=True)
            df_despesa = df_despesa[(df_despesa["data"] >= start_date_dt) & (df_despesa["data"] <= end_date_dt)]
            df_despesa = filtrar_df_por_filtros_extras(df_despesa, filtro_recorrentes, filtro_cartao)
            
            # Filtro de categorias
            if despesa_cats:
                df_despesa = df_despesa[df_despesa["categoria"].isin(despesa_cats)]
                
            soma_despesas = df_despesa['valor'].sum()
            
        soma_saldo = soma_receitas - soma_despesas
 
        # Formatar resultados
        def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        results = []
        for output in outputs:
            metric_id = output['id']['id']
            if metric_id == 'saldo': results.append(fmt(soma_saldo))
            elif metric_id == 'receita': results.append(fmt(soma_receitas))
            elif metric_id == 'despesa': results.append(fmt(soma_despesas))
        
        return results

    
    # O callback de dropdowns continua separado pois tem outputs de texto e dropdown
    @dash_app.callback(
        [
            Output("dropdown-despesa", "options"),
            Output("dropdown-despesa", "value")
        ],
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname"),
            Input("store-despesas", "data"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value"),
            Input("btn-limpar-filtros", "n_clicks")
        ],
        [
            State("dropdown-despesa", "value")
        ]
    )
    def populate_dropdown_despesas(start_date, end_date, pathname, store_despesas, filtro_recorrentes, filtro_cartao, n_clicks, current_val):
        if not current_user.is_authenticated:
            return [], []
        
        user_session = get_current_user_db_session()
        if not user_session: return [], []

        despesas_data = buscar_despesas_por_usuario(user_session)
        if not despesas_data: return [], []

        df = pd.DataFrame(despesas_data)
        if df.empty: return [], []

        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors='coerce')
        df.dropna(subset=['data'], inplace=True)
        df_filtered = df[(df["data"] >= pd.to_datetime(start_date)) & (df["data"] <= pd.to_datetime(end_date))]
        df_filtered = filtrar_df_por_filtros_extras(df_filtered, filtro_recorrentes, filtro_cartao)

        all_cats = df_filtered["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in all_cats if pd.notna(i)]
        
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        
        # Reset total se clicou no botão limpar
        if triggered_id == "btn-limpar-filtros":
            return dropdown_options, all_cats
            
        # Se for apenas navegação, e já houver valor, manter (deixar Dash Persistence agir)
        if (triggered_id == "base-url" or not triggered_id) and current_val:
            return dropdown_options, no_update
            
        # Manter seleção se possível ao mudar datas/radio
        if current_val:
            new_val = [c for c in current_val if c in all_cats]
            if new_val:
                return dropdown_options, new_val
                
        return dropdown_options, all_cats

    @dash_app.callback(
        [
            Output("dropdown-receita", "options"),
            Output("dropdown-receita", "value")
        ],
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("base-url", "pathname"),
            Input("store-receitas", "data"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value"),
            Input("btn-limpar-filtros", "n_clicks")
        ],
        [
            State("dropdown-receita", "value")
        ]
    )
    def populate_dropdown_receitas(start_date, end_date, pathname, store_receitas, filtro_recorrentes, filtro_cartao, n_clicks, current_val):
        if not current_user.is_authenticated:
            return [], []
        
        user_session = get_current_user_db_session()
        if not user_session: return [], []

        receitas_data = buscar_receitas_por_usuario(user_session)
        if not receitas_data: return [], []
            
        df = pd.DataFrame(receitas_data)
        if df.empty: return [], []

        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y", errors='coerce')
        df.dropna(subset=['data'], inplace=True)
        df_filtered = df[(df["data"] >= pd.to_datetime(start_date)) & (df["data"] <= pd.to_datetime(end_date))]
        df_filtered = filtrar_df_por_filtros_extras(df_filtered, filtro_recorrentes, filtro_cartao)

        all_cats = df_filtered["categoria"].unique().tolist()
        dropdown_options = [{"label": i, "value": i} for i in all_cats if pd.notna(i)]
        
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        
        if triggered_id == "btn-limpar-filtros":
            return dropdown_options, all_cats
            
        if (triggered_id == "base-url" or not triggered_id) and current_val:
            return dropdown_options, no_update
            
        # Manter seleção se possível
        if current_val:
            new_val = [c for c in current_val if c in all_cats]
            if new_val:
                return dropdown_options, new_val
                
        return dropdown_options, all_cats

    

    @dash_app.callback(
        Output({'page': 'dashboard', 'type': 'dash-graph', 'id': ALL}, "figure"),
        [
            Input("dropdown-receita", "value"),
            Input("dropdown-despesa", "value"),
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("store-receitas", "data"),
            Input("store-despesas", "data"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value")
        ]
    )
    def update_dashboard_graphs(receita_cats_selected, despesa_cats_selected, start_date, end_date, store_receitas, store_despesas, filtro_recorrentes, filtro_cartao):
        outputs = callback_context.outputs_list
        if not outputs or (isinstance(outputs, list) and not outputs[0]): return []
        
        if not current_user.is_authenticated:
            return [go.Figure()] * len(outputs)
        
        user_session = get_current_user_db_session()
        if not user_session: return [go.Figure()] * len(outputs)

        # Preparar dados base
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
        
        receitas_data = buscar_receitas_por_usuario(user_session)
        df_receita_base = pd.DataFrame(receitas_data)
        if not df_receita_base.empty:
            df_receita_base["data"] = pd.to_datetime(df_receita_base["data"], format="%d/%m/%Y", errors='coerce')
            df_receita_base.dropna(subset=['data'], inplace=True)
            df_receita_base = df_receita_base[(df_receita_base["data"] >= start_date_dt) & (df_receita_base["data"] <= end_date_dt)]
            df_receita_base = filtrar_df_por_filtros_extras(df_receita_base, filtro_recorrentes, filtro_cartao)

        despesas_data = buscar_despesas_por_usuario(user_session)
        df_despesa_base = pd.DataFrame(despesas_data)
        if not df_despesa_base.empty:
            df_despesa_base["data"] = pd.to_datetime(df_despesa_base["data"], format="%d/%m/%Y", errors='coerce')
            df_despesa_base.dropna(subset=['data'], inplace=True)
            df_despesa_base = df_despesa_base[(df_despesa_base["data"] >= start_date_dt) & (df_despesa_base["data"] <= end_date_dt)]
            df_despesa_base = filtrar_df_por_filtros_extras(df_despesa_base, filtro_recorrentes, filtro_cartao)

        final_results = []
        for output in outputs:
            graph_id = output['id']['id']
            fig = go.Figure()
            fig.update_layout(margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

            if graph_id == 'graph1': # Cashflow
                df_rc = pd.DataFrame(columns=["receita"])
                if not df_receita_base.empty:
                    df_temp = df_receita_base.copy()
                    if receita_cats_selected: df_temp = df_temp[df_temp["categoria"].isin(receita_cats_selected)]
                    df_rc = df_temp.set_index("data")[["valor"]].groupby(level="data").sum().rename(columns={"valor": "receita"})
                
                df_dp = pd.DataFrame(columns=["despesa"])
                if not df_despesa_base.empty:
                    df_temp = df_despesa_base.copy()
                    if despesa_cats_selected: df_temp = df_temp[df_temp["categoria"].isin(despesa_cats_selected)]
                    df_dp = df_temp.set_index("data")[["valor"]].groupby(level="data").sum().rename(columns={"valor": "despesa"})
                
                df_acum = df_dp.join(df_rc, how="outer").fillna(0)
                if not df_acum.empty:
                    df_acum["acum"] = (df_acum["receita"] - df_acum["despesa"]).cumsum()
                    fig.add_trace(go.Scatter(name="Fluxo de caixa", x=df_acum.index, y=df_acum["acum"], mode="lines"))
            
            elif graph_id == 'graph2': # Bar Comparison
                df_r = df_receita_base.copy() if not df_receita_base.empty else pd.DataFrame()
                df_d = df_despesa_base.copy() if not df_despesa_base.empty else pd.DataFrame()
                if not df_r.empty: df_r["Output"] = "Receitas"
                if not df_d.empty: df_d["Output"] = "Despesas"
                df_final = pd.concat([df_r, df_d])
                if not df_final.empty:
                    f_r = df_final["categoria"].isin(receita_cats_selected or []) & (df_final["Output"] == "Receitas")
                    f_d = df_final["categoria"].isin(despesa_cats_selected or []) & (df_final["Output"] == "Despesas")
                    df_final = df_final[f_r | f_d]
                    if not df_final.empty:
                        fig = px.bar(df_final, x="data", y="valor", color="Output", barmode="group")
                        fig.update_layout(margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

            elif graph_id == 'graph3': # Receitas Pie
                if not df_receita_base.empty and receita_cats_selected:
                    df_temp = df_receita_base[df_receita_base["categoria"].isin(receita_cats_selected)]
                    if not df_temp.empty:
                        fig = px.pie(df_temp, values="valor", names="categoria", hole=.2)
                        fig.update_layout(title={"text": "Receitas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

            elif graph_id == 'graph4': # Despesas Pie
                if not df_despesa_base.empty and despesa_cats_selected:
                    df_temp = df_despesa_base[df_despesa_base["categoria"].isin(despesa_cats_selected)]
                    if not df_temp.empty:
                        fig = px.pie(df_temp, values="valor", names="categoria", hole=.2)
                        fig.update_layout(title={"text": "Despesas"}, margin=graph_margin, height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        fig.update_layout(legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5))

            final_results.append(fig)
        
        return final_results