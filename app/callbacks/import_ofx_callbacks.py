import os
import pandas as pd
import dash_ag_grid as dag
from dash import Input, Output, State, dcc, html, ctx
import dash_bootstrap_components as dbc
import base64
import io
import ofxparse  # Biblioteca para processar OFX
from app import db
from app.models.despesas import Despesas
from app.models.receitas import Receitas
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente do .env
load_dotenv(find_dotenv())

# Obtém o caminho do prompt a partir do .env
PROMPT_FILE = os.getenv("PROMPT_FILE", "config/prompt_classificacao.md")  # Default se não encontrar

def register_callbacks(dash_app):
    
    # Callback para processar o arquivo OFX e exibir os dados na Grid
    @dash_app.callback(
        Output("ofx-grid-container", "children"),
        Output("confirm-import", "disabled"),
        Input("upload-ofx", "contents"),
        State("upload-ofx", "filename")
    )
    def process_ofx_file(contents, filename):
        if not contents:
            return [], True  # Não exibe nada se não houver arquivo
        
        # Decodifica o arquivo OFX
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        ofx_file = io.BytesIO(decoded)

        # Processa o arquivo OFX
        ofx = ofxparse.OfxParser.parse(ofx_file)

        # Converte os dados para um DataFrame
        data = []
        for transaction in ofx.account.statement.transactions:
            data.append({
                "ID": transaction.id,
                "Data": transaction.date.strftime("%d/%m/%Y"),
                "Categoria": "Importado OFX",
                "Descrição": transaction.memo,
                "Valor": round(transaction.amount, 2),
                "Tipo": "Receita" if transaction.amount > 0 else "Despesa"
            })
        
        df = pd.DataFrame(data)

        # Define colunas para a Grid
        columnDefs = [
            {"headerName": "ID", "field": "ID"},
            {"headerName": "Data", "field": "Data"},
            {"headerName": "Categoria", "field": "Categoria"},
            {"headerName": "Descrição", "field": "Descrição"},
            {"headerName": "Valor", "field": "Valor"},
            {"headerName": "Tipo", "field": "Tipo"},
        ]

        # Cria a Grid para exibição
        grid = dag.AgGrid(
            id="ofx-grid",
            rowData=df.to_dict("records"),
            columnDefs=columnDefs,
            defaultColDef={"editable": False, "minWidth": 120},
            dashGridOptions={"animateRows": True, 'pagination': True},
        )

        return grid, False  # Habilita o botão de importação

    # Callback para confirmar a importação e salvar no banco de dados
    @dash_app.callback(
        [
            Output("import-alert", "is_open", allow_duplicate=True),
            Output("import-alert", "children", allow_duplicate=True),
            Output("import-alert", "color", allow_duplicate=True),
        ],
        Input("confirm-import", "n_clicks"),
        State("ofx-grid", "rowData"),
        prevent_initial_call=True
    )
    def confirmar_importacao(n_clicks, row_data):
        if not row_data:
            return True, "Nenhum dado para importar.", "danger"

        try:
            for row in row_data:
                data_transacao = pd.to_datetime(row["Data"], format="%d/%m/%Y")
                descricao = row["Descrição"]
                valor = abs(row["Valor"])  # Valor absoluto para evitar duplicação de sinal
                categoria = row["Categoria"]

                if row["Tipo"] == "Receita":
                    valor = abs(row["Valor"])  # Mantém positivo
                    nova_receita = Receitas(
                        descricao=descricao,
                        categoria=categoria,
                        data=data_transacao,
                        valor=valor,
                        parcelado=False,
                        fixo=False
                    )
                    db.session.add(nova_receita)
                
                elif row["Tipo"] == "Despesa":
                    valor = abs(row["Valor"])  # Converte negativo para positivo
                    nova_despesa = Despesas(
                        descricao=descricao,
                        categoria=categoria,
                        data=data_transacao,
                        valor=valor,
                        parcelado=False,
                        fixo=False
                    )
                    db.session.add(nova_despesa)

            db.session.commit()
            return True, "Importação realizada com sucesso!", "success"

        except Exception as e:
            db.session.rollback()
            return True, f"Erro na importação: {str(e)}", "danger"
        
    # Callback para abrir e fechar o modal
    @dash_app.callback(
        Output("prompt-modal", "is_open"),
        Input("open-prompt-modal", "n_clicks"),
        Input("close-prompt-modal", "n_clicks"),
        State("prompt-modal", "is_open"),
        prevent_initial_call=True
    )
    def toggle_prompt_modal(open_click, close_click, is_open):
        if ctx.triggered_id == "open-prompt-modal":
            return True
        elif ctx.triggered_id == "close-prompt-modal":
            return False
        return is_open

    # Callback para carregar o prompt salvo no arquivo Markdown
    @dash_app.callback(
        Output("prompt-textarea", "value"),
        Input("open-prompt-modal", "n_clicks"),
        prevent_initial_call=True
    )
    def load_prompt(_):
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, "r", encoding="utf-8") as file:
                return file.read()
        return "O prompt ainda não foi definido."

    # Callback para salvar as alterações do prompt no arquivo Markdown
    @dash_app.callback(
        Output("import-alert", "is_open", allow_duplicate=True),
        Output("import-alert", "children", allow_duplicate=True),
        Output("import-alert", "color", allow_duplicate=True),
        Input("save-prompt", "n_clicks"),
        State("prompt-textarea", "value"),
        prevent_initial_call=True
    )
    def save_prompt(_, prompt_text):
        try:
            os.makedirs(os.path.dirname(PROMPT_FILE), exist_ok=True)
            with open(PROMPT_FILE, "w", encoding="utf-8") as file:
                file.write(prompt_text)
            return True, "Prompt salvo com sucesso!", "success"
        except Exception as e:
            return True, f"Erro ao salvar prompt: {str(e)}", "danger"
        

    # Callback para classificar os dados da importação
    @dash_app.callback(
        [
            Output("import-alert", "is_open", allow_duplicate=True),
            Output("import-alert", "children", allow_duplicate=True),
            Output("import-alert", "color", allow_duplicate=True),
            Output("ofx-grid", "rowData"),
        ],
        Input("classifica-import", "n_clicks"),
        State("ofx-grid", "rowData"),
        prevent_initial_call=True
    )
    def confirmar_importacao(n_clicks, row_data):
        if not row_data:
            return True, "Nenhum dado para classificar.", "danger", row_data

        row_data_df = pd.DataFrame(row_data)
        try:

            #=============
            #LLM
            from langchain_groq import ChatGroq
            from langchain_core.prompts import PromptTemplate
            from dotenv import load_dotenv, find_dotenv

            _ = load_dotenv(find_dotenv())

            # Carrega o prompt salvo no arquivo Markdown
            if os.path.exists(PROMPT_FILE):
                with open(PROMPT_FILE, "r", encoding="utf-8") as file:
                    template = file.read()
                    # print(template)
            else:
                return True, f"Defina um prompt adequado para classificação das transações.", "danger", row_data


            prompt = PromptTemplate.from_template(template=template)
            chat = ChatGroq(model="llama-3.1-8b-instant")
            chain = prompt | chat

            categoria = []

            for row in row_data:
                result = chain.invoke(row["Descrição"]).content
                categoria += [result]
                print(result)

            row_data_df["Categoria"] = categoria
            
            return True, "Importação realizada com sucesso!", "success", row_data_df.to_dict("records")

        except Exception as e:
            db.session.rollback()
            return True, f"Erro na importação: {str(e)}", "danger", row_data