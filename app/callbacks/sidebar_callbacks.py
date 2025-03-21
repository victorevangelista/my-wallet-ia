from dash.dependencies import Input, Output, State
from flask import current_app
from dash import no_update
from flask_login import logout_user
from app.services.despesa_service import salvar_despesa
from app.services.receita_service import salvar_receita
from app.services.categoria_service import (
    adicionar_categoria_despesa, adicionar_categoria_receita, 
    remover_categoria_despesa, remover_categoria_receita
)
from app.models.categoria import CatDespesas, CatReceitas
import pandas as pd
import re

def validar_e_converter_valor(valor):
    """
    Valida se um valor é numérico e o converte para FLOAT, aceitando vírgula como separador decimal.
    Exemplo: "1.234,56" -> 1234.56
    """
    if not valor:
        return None  # Retorna None se o valor estiver vazio

    # Remove espaços extras
    valor = valor.strip()

    # Substitui ponto (.) usado como separador de milhar e troca a vírgula (,) pelo ponto (.)
    valor = re.sub(r"\.", "", valor)  # Remove pontos de milhar
    valor = valor.replace(",", ".")  # Substitui a vírgula decimal por ponto

    try:
        return float(valor)  # Converte para FLOAT
    except ValueError:
        return None  # Retorna None se a conversão falhar


def register_callbacks(dash_app):
    @dash_app.callback(
        Output('base-url-data', 'href'),
        [Input("logout_button", "n_clicks")]
    )
    def logout(n_clicks):
        if n_clicks:
            print("logout!")
            logout_user()
            return '/login'  # Redireciona para login após logout
            # return no_update    
        return no_update


    # Pop-up receita
    @dash_app.callback(
        Output('modal-novo-receita', 'is_open'),
        Input('open-novo-receita', 'n_clicks'),
        State('modal-novo-receita', 'is_open')
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open


    # Pop-up Despesa
    @dash_app.callback(
        Output('modal-novo-despesa', 'is_open'),
        Input('open-novo-despesa', 'n_clicks'),
        State('modal-novo-despesa', 'is_open')
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open
        

    # Callback para adicionar uma nova despesa
    @dash_app.callback(
        [
            Output('alert-despesa', 'is_open', allow_duplicate=True), 
            Output('alert-despesa', 'children', allow_duplicate=True),
            Output('alert-despesa', 'color', allow_duplicate=True),
            Output("txt-despesa", "value"),
            Output("valor-despesa", "value"), 
            Output("date-despesas", "date"),
            Output("select-despesa", "value"), 
            Output("swtches-input-despesa", "value"),
        ],
        
        [Input("salvar-despesa-btn", "n_clicks")],
        
        [
            State("txt-despesa", "value"),
            State("valor-despesa", "value"), 
            State("date-despesas", "date"),
            State("select-despesa", "value"), 
            State("swtches-input-despesa", "value"),
            State("alert-despesa", "is_open"),
        ],
        prevent_initial_call=True  # Callback só será chamado quando o botão for clicado
    )
    def salvar_despesa_btn(n_clicks, descricao, valor, data, categoria, extras, is_open):
        if n_clicks:
            if not descricao or not valor or not data or not categoria:
                return not is_open, "Erro: Todos os campos são obrigatórios!", "danger", no_update, no_update, no_update, no_update, no_update

            valor_convertido = validar_e_converter_valor(valor)  # Valida e converte para FLOAT
            if valor_convertido is None:
                return not is_open, "Erro: O campo 'Valor' deve ser um número decimal válido!", "danger", no_update, no_update, no_update, no_update, no_update

            success, message = salvar_despesa(
                descricao=descricao,
                categoria=categoria,
                data=pd.to_datetime(data).date(),
                valor=valor_convertido,
                parcelado=1 in extras,
                fixo=2 in extras
            )
            return not is_open, message if success else "Erro ao salvar despesa!", "success", "", "", pd.datetime.today().date(), [], 0
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Callback para adicionar uma nova receita
    @dash_app.callback(
        [
            Output('alert-receita', 'is_open', allow_duplicate=True), 
            Output('alert-receita', 'children', allow_duplicate=True),
            Output('alert-receita', 'color', allow_duplicate=True),
            Output("txt-receita", "value"),
            Output("valor-receita", "value"), 
            Output("date-receita", "date"),
            Output("select-receita", "value"), 
            Output("swtches-input-receita", "value"),
        ],
        
        [Input("salvar-receita-btn", "n_clicks")],
        
        [
            State("txt-receita", "value"),
            State("valor-receita", "value"), 
            State("date-receita", "date"),
            State("select-receita", "value"), 
            State("swtches-input-receita", "value"),
            State("alert-receita", "is_open"),
        ],
        prevent_initial_call=True  # Callback só será chamado quando o botão for clicado
    )
    def salvar_receita_btn(n_clicks, descricao, valor, data, categoria, extras, is_open):
        if n_clicks:
            if not descricao or not valor or not data or not categoria:
                return not is_open, "Erro: Todos os campos são obrigatórios!", "danger", no_update, no_update, no_update, no_update, no_update

            valor_convertido = validar_e_converter_valor(valor)  # Valida e converte para FLOAT
            if valor_convertido is None:
                return not is_open, "Erro: O campo 'Valor' deve ser um número decimal válido!", "danger", no_update, no_update, no_update, no_update, no_update

            success, message = salvar_receita(
                descricao=descricao,
                categoria=categoria,
                data=pd.to_datetime(data).date(),
                valor=valor_convertido,
                parcelado=1 in extras,
                fixo=2 in extras
            )
            return not is_open, message if success else "Erro ao salvar receita!", "success", "", "", pd.datetime.today().date(), [], 0
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update


    # Callback para carregar categorias no dropdown e checklist
    @dash_app.callback(
        [Output('select-despesa', 'options'), Output('select-receita', 'options'),
         Output('checklist-selected-style-despesa', 'options'), Output('checklist-selected-style-receita', 'options')],
        Input('base-url', 'pathname')  # Atualiza categorias sempre que a página carregar
    )
    def carregar_categorias(_):
        with dash_app.server.app_context():  # Garante que estamos dentro do contexto da aplicação
            categorias_despesas = [{'label': c.categoria, 'value': c.categoria} for c in CatDespesas.query.all()]
            categorias_receitas = [{'label': c.categoria, 'value': c.categoria} for c in CatReceitas.query.all()]
        return categorias_despesas, categorias_receitas, categorias_despesas, categorias_receitas


    # Callback para adicionar categoria de despesa
    @dash_app.callback(
        [
            Output("select-despesa", "options", allow_duplicate=True),
            Output("checklist-selected-style-despesa", "options", allow_duplicate=True),
            Output('category-div-add-despesa', 'is_open', allow_duplicate=True), 
            Output('category-div-add-despesa', 'children', allow_duplicate=True),
            Output('category-div-add-despesa', 'color', allow_duplicate=True),
            Output('input-add-despesa', 'value', allow_duplicate=True), 
        ],
        Input("add-category-despesa", "n_clicks"),
        [
            State("input-add-despesa", "value"),
            State("category-div-add-despesa", "is_open"),
        ],
        prevent_initial_call='initial_duplicate'
    )
    def add_category_despesa(n_clicks, categoria, is_open):
        if n_clicks and categoria:
            success, message = adicionar_categoria_despesa(categoria)

            with current_app.app_context():
                categorias_despesas = [{'label': c.categoria, 'value': c.categoria} for c in CatDespesas.query.all()]

            return categorias_despesas, categorias_despesas, not is_open,  message if success else f"Erro: {message}", "success" if success else "danger", ""
        return no_update, no_update, no_update, no_update, no_update, no_update

    # Callback para adicionar categoria de receita
    @dash_app.callback(
        [
            Output("select-receita", "options", allow_duplicate=True),
            Output("checklist-selected-style-receita", "options", allow_duplicate=True),
            Output('category-div-add-receita', 'is_open', allow_duplicate=True), 
            Output('category-div-add-receita', 'children', allow_duplicate=True),
            Output('category-div-add-receita', 'color', allow_duplicate=True),
            Output('input-add-receita', 'value'),  
        ],
        Input("add-category-receita", "n_clicks"),
        [
            State("input-add-receita", "value"),
            State("category-div-add-receita", "is_open"),
        ],
        prevent_initial_call='initial_duplicate'
    )
    def add_category_receita(n_clicks, categoria, is_open):
        if n_clicks and categoria:
            success, message = adicionar_categoria_receita(categoria)

            with current_app.app_context():
                categorias_receitas = [{'label': c.categoria, 'value': c.categoria} for c in CatReceitas.query.all()]

            return categorias_receitas, categorias_receitas, not is_open,  message if success else f"Erro: {message}", "success" if success else "danger", ""
        return no_update, no_update, no_update, no_update, no_update, no_update

    # Callback para remover categoria de despesa e atualizar selects
    @dash_app.callback(
        [
            Output("select-despesa", "options", allow_duplicate=True),
            Output("checklist-selected-style-despesa", "options", allow_duplicate=True),
            Output('category-div-remove-despesa', 'is_open', allow_duplicate=True), 
            Output('category-div-remove-despesa', 'children', allow_duplicate=True),
            Output('category-div-remove-despesa', 'color', allow_duplicate=True),
        ],  # Atualiza dropdowns
        Input("remove-category-despesa", "n_clicks"),
        [
            State("checklist-selected-style-despesa", "value"),
            State("category-div-remove-despesa", "is_open"),
        ],
        prevent_initial_call='initial_duplicate'
    )
    def remove_category_despesa(n_clicks, categorias, is_open):
        if n_clicks and categorias:
            for categoria in categorias:
                success, message = remover_categoria_despesa(categoria)

            with current_app.app_context():
                categorias_despesas = [{'label': c.categoria, 'value': c.categoria} for c in CatDespesas.query.all()]

            return categorias_despesas, categorias_despesas, not is_open, message if success else f"Erro: {message}", "success" if success else "danger"
        return no_update, no_update, no_update, no_update, no_update

    # Callback para remover categoria de receita e atualizar selects
    @dash_app.callback(
        [
            Output("select-receita", "options", allow_duplicate=True),
            Output("checklist-selected-style-receita", "options", allow_duplicate=True),
            Output('category-div-remove-receita', 'is_open', allow_duplicate=True), 
            Output('category-div-remove-receita', 'children', allow_duplicate=True),
            Output('category-div-remove-receita', 'color', allow_duplicate=True),
         ],  # Atualiza dropdowns
        Input("remove-category-receita", "n_clicks"),
        [
            State("checklist-selected-style-receita", "value"),
            State("category-div-remove-receita", "is_open"),
        ],
        prevent_initial_call='initial_duplicate'
    )
    def remove_category_receita(n_clicks, categorias, is_open):
        if n_clicks and categorias:
            for categoria in categorias:
                success, message = remover_categoria_receita(categoria)

            with current_app.app_context():
                categorias_receitas = [{'label': c.categoria, 'value': c.categoria} for c in CatReceitas.query.all()]

            return categorias_receitas, categorias_receitas, not is_open, message if success else f"Erro: {message}", "success" if success else "danger"
        return no_update, no_update, no_update, no_update, no_update