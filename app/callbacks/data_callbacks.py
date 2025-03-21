from dash.dependencies import Input, Output
from dash import no_update  
from app.components.dashboard import layout as dashboard
from app.components.extrato_despesas import layout as extrato_despesas
from app.components.extrato_receitas import layout as extrato_receitas

def register_callbacks(dash_app):
    @dash_app.callback(
            Output('page-content-dash', 'children'), 
            [
                Input('data-url', 'pathname')
            ]
    )
    def render_page(pathname):
        if pathname == '/data':
            return dashboard
        
        if pathname == '/extrato-despesas':
            return extrato_despesas
        
        if pathname == '/extrato-receitas':
            return extrato_receitas
