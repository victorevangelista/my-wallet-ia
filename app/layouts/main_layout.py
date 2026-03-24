from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd

# Definição do layout principal do Dash
layout = html.Div([
    dcc.Location(id="base-url", refresh=False),  
    
    # Store para gerenciar o estado da sidebar (expandida ou colapsada)
    dcc.Store(id='sidebar-state', data='expanded', storage_type='local'),
    
    dcc.Store(id='store-receitas', data={}),
    dcc.Store(id='store-despesas', data={}),
    dcc.Store(id='store-cat-receitas', data={}),
    dcc.Store(id='store-cat-despesas', data={}),
    
    dcc.Store(id="login-state", data=""),
    dcc.Store(id="register-state", data=""),
    
    # Container da Navbar (será preenchida pelo callback ou ficará oculta no login)
    html.Div(id="navbar-container"),

    # Wrapper principal para Sidebar + Conteúdo
    html.Div([
        # Container da Sidebar (será preenchida pelo callback ou ficará oculta no login)
        html.Div(id="sidebar-container-global"),
        
        # Área de Conteúdo Principal
        html.Div(id="page-content", className="content-container")
    ], className="main-wrapper", id="main-wrapper-id")
    
], style={"padding": "0px", "height": "100vh", "overflow": "hidden"})
