from dash.dependencies import Input, Output, State
from dash import no_update  
from app.components.dashboard import layout as dashboard
from app.components.extrato_despesas import layout as extrato_despesas
from app.components.extrato_receitas import layout as extrato_receitas
from app.components.import_ofx import layout as import_ofx
from app.components.fina_bot import layout as fina_bot


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
        
        if pathname == '/import-ofx':
            return import_ofx
        
        if pathname == '/fina-bot':
            return fina_bot
        
    @dash_app.callback(
        [
            Output("date-picker-config", "start_date"),
            Output("date-picker-config", "end_date"),
            Output("radio-recorrentes", "value"),
            Output("radio-cartao", "value")
        ],
        Input("btn-limpar-filtros", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_filters(n_clicks):
        from datetime import datetime
        today = datetime.today()
        start = today.replace(day=1).date()
        end = today.date()
        # Dropdowns e Accordion serão resetados via callback de indicadores
        return start, end, "todas", "todas"

    @dash_app.callback(
        [
            Output("filter-icon", "style"),
            Output("btn-limpar-filtros", "style"),
            Output("accordion-filtros", "active_item")
        ],
        [
            Input("date-picker-config", "start_date"),
            Input("date-picker-config", "end_date"),
            Input("radio-recorrentes", "value"),
            Input("radio-cartao", "value"),
            Input("dropdown-receita", "value"),
            Input("dropdown-despesa", "value")
        ],
        [
            State("accordion-filtros", "active_item")
        ]
    )
    def update_filter_ui(start_date, end_date, rec, cart, rec_cat, desp_cat, current_active):
        from datetime import datetime
        from dash import no_update
        
        today = datetime.today()
        default_start = today.replace(day=1).date().strftime("%Y-%m-%d")
        default_end = today.date().strftime("%Y-%m-%d")
        
        is_modified = (
            (start_date and start_date != default_start) or
            (end_date and end_date != default_end) or
            (rec != "todas") or
            (cart != "todas") or
            (isinstance(rec_cat, list) and len(rec_cat) > 0) or
            (isinstance(desp_cat, list) and len(desp_cat) > 0)
        )
        
        style = {"display": "inline-block", "color": "#ffc107"} if is_modified else {"display": "none"}
        btn_style = {"display": "inline-block"} if is_modified else {"display": "none"}
        
        # Lógica de Accordion:
        # 1. Se resetou (não modificado), fechar
        # 2. Se modificou, não forçar abertura (no_update)
        if not is_modified:
            new_active = None
        else:
            new_active = no_update
            
        return style, btn_style, new_active
