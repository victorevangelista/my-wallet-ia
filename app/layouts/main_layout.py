from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

# Definição do layout principal do Dash
layout = html.Div([
    dcc.Location(id="base-url", refresh=True),  
    
    dcc.Store(id='store-receitas', data={}),
    dcc.Store(id='store-despesas', data={}),
    dcc.Store(id='store-cat-receitas', data={}),
    dcc.Store(id='store-cat-despesas', data={}),
    
    # dbc.Row([
    #     dbc.Col([
    #         dcc.Location(id="base-url", refresh=False),  # Garante que a URL seja detectada corretamente
    #         dcc.Store(id="login-state", data=""),  # Armazena o estado de login
    #         dcc.Store(id="register-state", data=""),  # Armazena o estado de registro

    #         html.Div(id="page-content", style={"height": "100vh", "display": "flex", "justify-content": "center"}),  # ✅ Onde as páginas serão renderizadas
            
    #     ]),
    # ]),
    
    dcc.Store(id="login-state", data=""),
    dcc.Store(id="register-state", data=""),
    
    html.Div(id="page-content", style={"height": "100vh", "display": "flex", "justify-content": "center"}),  
], style={"padding": "0px"})
