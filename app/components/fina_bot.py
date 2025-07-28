from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import callback, ctx, no_update

# =========  Layout  =========== #
layout = dbc.Container([
    # Store para manter o histórico da conversa em formato de texto
    dcc.Store(id='chat-history-store', data=[]),
    dbc.Row([
        dbc.Col([
            html.H2("Fina - Chatbot Financeiro", className="mb-4", style={"textAlign": "center"}),
            dbc.Card([
                dbc.CardHeader("Histórico da Conversa"),
                dbc.CardBody([
                    html.Div(
                            id="chat-history",
                            style={
                                "height": "400px",
                                "overflowY": "auto",
                                "padding": "10px",
                                "borderRadius": "5px",
                                "border": "1px solid #dee2e6"
                            },
                        ),
                ])
            ], className="mb-3"),
            dbc.InputGroup([
                dbc.Textarea(
                    id="user-input",
                    placeholder="Digite sua pergunta para a Fina...",
                    style={"resize": "none"},
                    rows=2
                ),
                dbc.Button("Enviar", id="send-button", color="primary", n_clicks=0)
            ], className="mt-2")
        ], width=12)
    ])
], fluid=True, style={"padding": "20px"})


# ========== CALLBACK EXEMPLO ========== #

from app.llm.chatbot_financeiro import full_chain, sql_chain, run_query, is_valid_for_plot, plot_chart

# Função para obter a resposta do bot e gerar gráficos se necessário
def get_bot_response(user_message, history):
    try:
        print(f"Usuário: {user_message}")
        # Converte a lista de histórico em uma string para o prompt
        history_str = "\n".join(history)
        result = full_chain.invoke({"question": user_message, "history": history_str})
        resposta = result["resposta"]
        tipo_vis = result["tipo_visualizacao"]

        # Se for gráfico, gere a imagem e retorne o caminho junto com a resposta
        if tipo_vis in ["pizza", "barras", "linhas"]:
            sql_query = sql_chain.invoke({"question": user_message, "history": history_str})
            dados = run_query(sql_query)
            if is_valid_for_plot(dados):
                try:
                    image_path = plot_chart(dados, chart_type=tipo_vis)
                    return {"resposta": f"{resposta}\n\n", "imagem": image_path}
                except Exception as plot_error:
                    return {"resposta": f"{resposta}\n⚠️ Erro ao gerar gráfico: {plot_error}", "imagem": None}
            else:
                return {"resposta": f"{resposta}", "imagem": None}
        else:
            return {"resposta": resposta, "imagem": None}
    except Exception as e:
        # Mensagem amigável para o usuário
        return {
            "resposta": (
                "Desculpe, ocorreu um erro ao processar sua solicitação.\n\n"
                f"Detalhes técnicos: {str(e)}"
                "\n\nSe a pergunta envolve dados financeiros relacionados, tente ser mais específico ou pergunte quais categorias estão disponíveis por exemplo."
            ),
            "imagem": None
        }


@callback(
    Output("chat-history", "children"),
    Output("user-input", "value"),
    Output("chat-history-store", "data"),
    Input("send-button", "n_clicks"),
    State("user-input", "value"),
    State("chat-history", "children"),
    State("chat-history-store", "data"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_input, chat_history, history_store):
    if not user_input or user_input.strip() == "":
        return no_update, "", no_update

    # Inicializa histórico se necessário
    if not chat_history:
        chat_history = []

    # Adiciona mensagem do usuário (alinhada à direita)
    chat_history = list(chat_history)  # Garante que é uma lista
    chat_history.append(
        html.Div([
            html.Small("Você", style={"display": "block", "marginBottom": "2px", "color": "#000000"}),
            dcc.Markdown(user_input, className="user-message", style={"background": "none", "padding": "0", "display": "inline-block", "margin": "0"})
        ], style={"textAlign": "right", "marginBottom": "10px"})
    )

    # Adiciona mensagem de processamento do bot (alinhada à esquerda)
    chat_history.append(
        html.Div([
            html.Small("Fina Bot", style={"display": "block", "marginBottom": "2px", "color": "#000000"}),
            dcc.Markdown("Fina está processando sua resposta...", className="bot-message", style={"background": "none", "padding": "0", "display": "inline-block", "margin": "0"})
        ], style={"textAlign": "left", "marginBottom": "10px"})
    )

    # Atualiza o histórico de texto para a LLM
    if not history_store:
        history_store = []
    history_store.append(f"Humano: {user_input}")

    return chat_history, "", history_store

# Callback para simular resposta do bot após processamento
@callback(
    Output("chat-history", "children", allow_duplicate=True),
    Output("chat-history-store", "data", allow_duplicate=True),
    Input("chat-history", "children"),
    State("chat-history-store", "data"),
    prevent_initial_call=True
)
def bot_response(chat_history, history_store):
    # Se não há histórico ou não há mensagem de processamento, não faz nada
    if not chat_history or not any(
        "Fina está processando" in (
            c['props']['children'][1]['props']['children'] if isinstance(c, dict) else ""
        ) for c in chat_history
    ):
        return no_update
    
    # Remove a última mensagem (processando)
    chat_history = list(chat_history)
    last = chat_history[-1]
    if isinstance(last, dict):
        children = last.get('props', {}).get('children', [])
        if len(children) > 1 and "Fina está processando" in (
            children[1].get('props', {}).get('children', "") if isinstance(children[1], dict) else str(children[1])
        ):
            chat_history.pop()
    else:
        if "Fina está processando" in last.children[1].children:
            chat_history.pop()

    # Recupera a última mensagem do usuário antes do "Fina está processando"
    user_message = None
    for c in reversed(chat_history):
        if isinstance(c, dict):
            style = c.get('props', {}).get('style', {})
            children = c.get('props', {}).get('children', [])
            if style.get("textAlign") == "right" and len(children) > 1:
                user_message = children[1].get('props', {}).get('children', "")
                break
        else:
            if getattr(c, "style", {}).get("textAlign") == "right":
                user_message = c.children[1].children
                break

    if not user_message:
        return no_update, no_update

    # Chama o bot
    bot_msg = get_bot_response(user_message, history_store)

    # bot_msg agora é um dicionário {"resposta": ..., "imagem": ...}
    components = [
        html.Small("Fina Bot", style={"display": "block", "marginBottom": "2px", "color": "#000000"}),
        dcc.Markdown(bot_msg["resposta"], className="bot-message", style={"background": "none", "padding": "0", "display": "inline-block", "margin": "0"})
    ]
    if bot_msg.get("imagem"):
        components.append(
            html.Img(src=f"/{bot_msg['imagem']}", style={"maxWidth": "100%", "marginTop": "10px"})
        )

    chat_history.append(
        html.Div(components, style={"textAlign": "left", "marginBottom": "10px"})
    )
    
    # Atualiza o histórico de texto com a resposta da IA
    history_store.append(f"IA: {bot_msg['resposta']}")

    return chat_history, history_store
