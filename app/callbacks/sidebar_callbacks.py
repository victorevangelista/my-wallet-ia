from dash.dependencies import Input, Output, State
from flask import current_app
from dash import no_update
from flask_login import logout_user, current_user # ADICIONADO current_user

# Importe os serviços refatorados
from app.services.despesa_service import (
    salvar_despesa_por_usuario, 
    buscar_despesas_por_usuario # Se necessário para alguma validação ou lógica aqui
)
from app.services.receita_service import (
    salvar_receita_por_usuario, 
    buscar_receitas_por_usuario # Se necessário
)
from app.services.categoria_service import (
    adicionar_categoria_despesa_por_usuario, adicionar_categoria_receita_por_usuario,
    remover_categoria_despesa_por_usuario, remover_categoria_receita_por_usuario,
    buscar_cat_despesas_por_usuario, buscar_cat_receitas_por_usuario
)
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

# Importar helper para sessão do usuário e modelos se for interagir diretamente (geralmente não no callback)
from app import get_current_user_db_session
# Os modelos CatDespesas e CatReceitas de financial_data serão usados pelos serviços.


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
        if n_clicks and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return not is_open, "Erro de sessão. Faça login novamente.", "danger", no_update, no_update, no_update, no_update, no_update

            if not descricao or not valor or not data or not categoria:
                return not is_open, "Erro: Todos os campos são obrigatórios!", "danger", no_update, no_update, no_update, no_update, no_update

            valor_convertido = validar_e_converter_valor(valor)  # Valida e converte para FLOAT
            if valor_convertido is None:
                return not is_open, "Erro: O campo 'Valor' deve ser um número decimal válido!", "danger", no_update, no_update, no_update, no_update, no_update
            
            # Assumindo que 'categoria' é o nome da categoria (string)
            success, message = salvar_despesa_por_usuario(
                user_session, # Passa a sessão do usuário
                descricao=descricao,
                categoria_nome=categoria, # Passa o nome da categoria
                data=pd.to_datetime(data).date(),
                valor=valor_convertido,
                parcelado=1 in extras,
                fixo=2 in extras
            )
            # Limpa os campos em caso de sucesso
            return not is_open, message, "success" if success else "danger", "" if success else no_update, "" if success else no_update, pd.Timestamp.today().date() if success else no_update, None if success else no_update, [] if success else no_update
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
        if n_clicks and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return not is_open, "Erro de sessão. Faça login novamente.", "danger", no_update, no_update, no_update, no_update, no_update

            if not descricao or not valor or not data or not categoria:
                return not is_open, "Erro: Todos os campos são obrigatórios!", "danger", no_update, no_update, no_update, no_update, no_update

            valor_convertido = validar_e_converter_valor(valor)  # Valida e converte para FLOAT
            if valor_convertido is None:
                return not is_open, "Erro: O campo 'Valor' deve ser um número decimal válido!", "danger", no_update, no_update, no_update, no_update, no_update
            
            success, message = salvar_receita_por_usuario(
                user_session, # Passa a sessão do usuário
                descricao=descricao,
                categoria_nome=categoria, # Passa o nome da categoria
                data=pd.to_datetime(data).date(),
                valor=valor_convertido,
                parcelado=1 in extras,
                fixo=2 in extras
            )
            return not is_open, message, "success" if success else "danger", "" if success else no_update, "" if success else no_update, pd.Timestamp.today().date() if success else no_update, None if success else no_update, [] if success else no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update


    # Callback para carregar categorias no dropdown e checklist
    @dash_app.callback(
        [Output('select-despesa', 'options'), Output('select-receita', 'options'),
         Output('checklist-selected-style-despesa', 'options'), Output('checklist-selected-style-receita', 'options')],
        Input('base-url', 'pathname'), # Ou um Input melhor, como um dcc.Store que é atualizado
        # Adicionar Inputs de stores que são atualizados quando categorias são adicionadas/removidas
        Input('store-cat-despesas', 'data'), 
        Input('store-cat-receitas', 'data')
    )
    def carregar_categorias(pathname, store_cat_despesas_data, store_cat_receitas_data):
        if not current_user.is_authenticated:
            return [], [], [], []
        
        user_session = get_current_user_db_session()
        if not user_session:
            return [], [], [], [] # Ou mensagem de erro

        success_desp, despesas_cats_data = buscar_cat_despesas_por_usuario(user_session)
        success_rec, receitas_cats_data = buscar_cat_receitas_por_usuario(user_session)
        
        categorias_despesas_options = [{'label': c['categoria'], 'value': c['categoria']} for c in despesas_cats_data] if success_desp else []
        categorias_receitas_options = [{'label': c['categoria'], 'value': c['categoria']} for c in receitas_cats_data] if success_rec else []
        return categorias_despesas_options, categorias_receitas_options, categorias_despesas_options, categorias_receitas_options


    # Callback para adicionar categoria de despesa
    @dash_app.callback(
        [
            Output("select-despesa", "options", allow_duplicate=True),
            Output("checklist-selected-style-despesa", "options", allow_duplicate=True),
            Output('category-div-add-despesa', 'is_open', allow_duplicate=True), 
            Output('category-div-add-despesa', 'children', allow_duplicate=True),
            Output('category-div-add-despesa', 'color', allow_duplicate=True),
            Output('input-add-despesa', 'value', allow_duplicate=True), 
            Output('store-cat-despesas', 'data', allow_duplicate=True) # Para disparar atualização do dropdown
        ],
        Input("add-category-despesa", "n_clicks"),
        [
            State("input-add-despesa", "value"),
            State("category-div-add-despesa", "is_open"),
            State('store-cat-despesas', 'data') # Para obter o valor atual do store
        ],
        prevent_initial_call=True
    )
    def add_category_despesa(n_clicks, categoria_nome, is_open, current_store_data):
        if n_clicks and categoria_nome and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return no_update, no_update, not is_open, "Erro de sessão.", "danger", "", current_store_data

            success, message = adicionar_categoria_despesa_por_usuario(user_session, categoria_nome)
            
            # Atualiza o store para disparar o callback carregar_categorias
            new_store_data = {'trigger': current_store_data.get('trigger', 0) + 1} if success else current_store_data
            return no_update, no_update, not is_open,  message, "success" if success else "danger", "" if success else no_update, new_store_data
        return no_update, no_update, no_update, no_update, no_update, no_update, current_store_data

    # Callback para adicionar categoria de receita
    @dash_app.callback(
        [
            Output("select-receita", "options", allow_duplicate=True),
            Output("checklist-selected-style-receita", "options", allow_duplicate=True),
            Output('category-div-add-receita', 'is_open', allow_duplicate=True), 
            Output('category-div-add-receita', 'children', allow_duplicate=True),
            Output('category-div-add-receita', 'color', allow_duplicate=True),
            Output('input-add-receita', 'value'),  
            Output('store-cat-receitas', 'data', allow_duplicate=True) # Para disparar atualização
        ],
        Input("add-category-receita", "n_clicks"),
        [
            State("input-add-receita", "value"),
            State("category-div-add-receita", "is_open"),
            State('store-cat-receitas', 'data')
        ],
        prevent_initial_call=True
    )
    def add_category_receita(n_clicks, categoria_nome, is_open, current_store_data):
        if n_clicks and categoria_nome and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return no_update, no_update, not is_open, "Erro de sessão.", "danger", "", current_store_data

            success, message = adicionar_categoria_receita_por_usuario(user_session, categoria_nome)

            new_store_data = {'trigger': current_store_data.get('trigger', 0) + 1} if success else current_store_data
            return no_update, no_update, not is_open,  message, "success" if success else "danger", "" if success else no_update, new_store_data
        return no_update, no_update, no_update, no_update, no_update, no_update, current_store_data

    # Callback para remover categoria de despesa e atualizar selects
    @dash_app.callback(
        [
            Output("select-despesa", "options", allow_duplicate=True),
            Output("checklist-selected-style-despesa", "options", allow_duplicate=True),
            Output('category-div-remove-despesa', 'is_open', allow_duplicate=True), 
            Output('category-div-remove-despesa', 'children', allow_duplicate=True),
            Output('category-div-remove-despesa', 'color', allow_duplicate=True),
            Output('store-cat-despesas', 'data', allow_duplicate=True) # Para disparar atualização
        ],  # Atualiza dropdowns
        Input("remove-category-despesa", "n_clicks"),
        [
            State("checklist-selected-style-despesa", "value"),
            State("category-div-remove-despesa", "is_open"),
            State('store-cat-despesas', 'data')
        ],
        prevent_initial_call=True
    )
    def remove_category_despesa(n_clicks, categorias_selecionadas, is_open, current_store_data):
        if n_clicks and categorias_selecionadas and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return no_update, no_update, not is_open, "Erro de sessão.", "danger", current_store_data

            messages = []
            all_success = True
            for categoria_nome in categorias_selecionadas:
                success, message = remover_categoria_despesa_por_usuario(user_session, categoria_nome)
                messages.append(message)
                if not success: all_success = False
            new_store_data = {'trigger': current_store_data.get('trigger', 0) + 1} # Sempre atualiza para refletir mudanças
            return no_update, no_update, not is_open, " ".join(messages), "success" if all_success else "warning", new_store_data
        return no_update, no_update, no_update, no_update, no_update, current_store_data

    # Callback para remover categoria de receita e atualizar selects
    @dash_app.callback(
        [
            Output("select-receita", "options", allow_duplicate=True),
            Output("checklist-selected-style-receita", "options", allow_duplicate=True),
            Output('category-div-remove-receita', 'is_open', allow_duplicate=True), 
            Output('category-div-remove-receita', 'children', allow_duplicate=True),
            Output('category-div-remove-receita', 'color', allow_duplicate=True),
            Output('store-cat-receitas', 'data', allow_duplicate=True) # Para disparar atualização
         ],  # Atualiza dropdowns
        Input("remove-category-receita", "n_clicks"),
        [
            State("checklist-selected-style-receita", "value"),
            State("category-div-remove-receita", "is_open"),
            State('store-cat-receitas', 'data')
        ],
        prevent_initial_call=True
    )
    def remove_category_receita(n_clicks, categorias_selecionadas, is_open, current_store_data):
        if n_clicks and categorias_selecionadas and current_user.is_authenticated:
            user_session = get_current_user_db_session()
            if not user_session:
                return no_update, no_update, not is_open, "Erro de sessão.", "danger", current_store_data
            
            messages = []
            all_success = True
            for categoria_nome in categorias_selecionadas:
                success, message = remover_categoria_receita_por_usuario(user_session, categoria_nome)
                messages.append(message)
                if not success: all_success = False
            new_store_data = {'trigger': current_store_data.get('trigger', 0) + 1}
            return no_update, no_update, not is_open, " ".join(messages), "success" if all_success else "warning", new_store_data
        return no_update, no_update, no_update, no_update, no_update, current_store_data