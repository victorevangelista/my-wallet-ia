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
            row_data_df["Categoria"] = "Nova Classificação"
            return True, "Importação realizada com sucesso!", "success", row_data_df.to_dict("records")

        except Exception as e:
            db.session.rollback()
            return True, f"Erro na importação: {str(e)}", "danger", row_data