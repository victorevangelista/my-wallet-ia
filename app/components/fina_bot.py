from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import callback, ctx, no_update
from dash_chat import ChatComponent


# Define default messages for the chat
default_messages = [
    {"role": "assistant", "content": "Olá sou a Fina, sua consultora financeira! Em que posso ajudar hoje?"},
]

# =========  Layout  =========== #
layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            html.H2("Fina - Chatbot Financeiro", className="mb-4", style={"textAlign": "center"}),
            html.Div(
                [
                    ChatComponent(
                        id="chat-component",
                        messages=[],  # Initialize empty since we'll load from storage
                        input_placeholder="Digite sua mensagem aqui...",
                    ),
                    
                    # The store component help use save messages
                    dcc.Store("chat-memory", data=default_messages, storage_type="local"),
                ],
                
                # Some basic CSS styling for the app
                style={
                    "max-width": "100%",
                    "margin": "0 auto",
                    "font-family": "Arial, sans-serif",
                    "padding": "20px",
                }
            )

        ], width=12)
    ]),
], fluid=True, style={"padding": "20px"})


# ========== CALLBACK EXEMPLO ========== #

from app.ia.llm.chatbot_financeiro import full_chain, sql_chain, run_query, is_valid_for_plot, plot_chart



# Função para obter a resposta do bot e gerar gráficos se necessário
def get_bot_response(user_message, history):
    try:
        
        # Converte a lista de histórico em uma string para o prompt
        history_str = history if isinstance(history, str) else "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
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
    Output("chat-component", "messages"),
    Output("chat-memory", "data"),
    Input("chat-component", "new_message"),
    State("chat-memory", "data"),
)
def handle_chat(new_message, messages):
    # If new_message is None, just return the stored messages
    # This is run at page load
    if not new_message:
        return messages, messages

    # If we have a user message, concatenate it to the list of messages
    updated_messages = messages + [new_message]

    # If the new message comes from the user, trigger the OpenAI API
    if new_message["role"] == "user":
        
        # Chama o bot
        print(f"Usuário: {new_message.get('content', '')}")
        print(f"Histórico: {updated_messages}")
        bot_msg = get_bot_response(new_message.get('content', ''), updated_messages)
        print(f"Resposta: {bot_msg}")

        bot_response = {
            "role": "assistant",
            "content": f"{bot_msg['resposta']}\n\n![Gráfico]({bot_msg['imagem']})" if bot_msg.get("imagem") else bot_msg['resposta'],
        }

        # Append the new message to the message list
        updated_messages += [bot_response]

    # We update both the chat component and the chat memory
    return updated_messages, updated_messages



