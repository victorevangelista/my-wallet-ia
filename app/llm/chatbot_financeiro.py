from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
import matplotlib.pyplot as plt
import pandas as pd
import uuid
import os

# Carrega variáveis de ambiente
_ = load_dotenv(find_dotenv())

# Caminho para o banco de dados SQLite
db_path = "instance/user_data/user_1.sqlite"
assert os.path.exists(db_path), f"Banco não encontrado: {db_path}"
db = SQLDatabase.from_uri(f"sqlite:///{db_path}")

# Prompt para gerar SQL
template_sql = """
Com base no esquema de tabela abaixo, escreva uma consulta SQL que responda à pergunta do usuário.
{schema}

Pergunta: {question}
Somente a consulta SQL, sem explicações adicionais e sem formatações. 
"""

prompt_sql = ChatPromptTemplate.from_template(template=template_sql)

# Prompt para resposta amigável e decisão de visualização
template_chat = """
Você é um assistente de IA especializado em dados financeiros do usuário.

Instruções:
1. Use a resposta da consulta SQL para gerar uma explicação clara ao usuário.
2. Avalie se a resposta pode ser visualizada com um gráfico.
   - Se sim, identifique o melhor tipo entre: "pizza", "barras", "linhas".
   - Se não, retorne "nenhum".
3. Retorne um JSON com os campos:
   {{
      "resposta": "<mensagem explicativa para o usuário no formato Markdown>",
      "tipo_visualizacao": "pizza" ou "barras" ou "linhas" ou "tabela" ou "nenhum"
   }}

IMPORTANTE:
Retorne apenas o JSON válido acima. Não inclua nenhuma explicação fora dele.

Esquema das tabelas:
{schema}

Pergunta: {question}
SQL query: {sql_query} 
Resposta SQL: {response}
"""


prompt_chat = ChatPromptTemplate.from_template(template_chat)

# LLM
llm = ChatGroq(model="llama-3.1-8b-instant")

# Parser de saída
output_parser = JsonOutputParser()

# Recupera schema do banco
def get_schema(_):
    return db.get_table_info()

# Limpa SQL retornada pela LLM
def clean_sql_query(query):
    if not query:
        return ""
    query = query.strip()
    if query.startswith("```sql"):
        query = query[len("```sql"):].strip()
    if query.endswith("```"):
        query = query[:-3].strip()
    return query

# Extrai SQL do output da LLM
def extract_sql_from_llm_output(msg):
    text = msg.content if hasattr(msg, "content") else str(msg)
    return clean_sql_query(text)

# Executa a SQL
def run_query(query):
    query = clean_sql_query(query)
    with db._engine.connect() as conn:
        result = conn.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

# Verifica se resultado pode ser usado para gráfico
def is_valid_for_plot(dados):
    try:
        df = pd.DataFrame(dados)
        if df is None or df.empty:
            return False
        if df.shape[1] != 2:
            return False
        if df.shape[0] < 2:
            return False
        return True
    except Exception:
        return False

def plot_chart(query_result, chart_type="pizza", title="Gráfico de Despesas"):
    df = pd.DataFrame(query_result)
    
    if df.empty:
        raise ValueError("Dados vazios para gerar gráfico.")

    fig, ax = plt.subplots(figsize=(6, 6))

    if chart_type == "pizza":
        if df.shape[1] != 2:
            raise ValueError("Pizza requer exatamente 2 colunas.")
        labels = df.iloc[:, 0]
        values = df.iloc[:, 1]
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

    elif chart_type == "barras":
        labels = df.iloc[:, 0]
        values = df.iloc[:, 1]
        ax.bar(labels, values)
        ax.set_ylabel("Valor")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')

    elif chart_type == "linhas":
        if df.shape[1] < 2:
            raise ValueError("Linha requer pelo menos 2 colunas.")
        df.columns = [str(c) for c in df.columns]
        df.plot(ax=ax)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df.iloc[:, 0], rotation=45, ha='right')

    elif chart_type == "tabela":
        fig.delaxes(ax)  # remove o eixo atual
        fig, ax = plt.subplots(figsize=(8, len(df) * 0.5 + 1))
        ax.axis('off')
        table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        table.scale(1, 1.5)

    else:
        raise ValueError("Tipo de gráfico não suportado")

    plt.title(title)
    image_path = f"temp/{uuid.uuid4().hex}.png"
    os.makedirs("temp", exist_ok=True)
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()
    
    return image_path

def limpar_temp_excesso(pasta="temp", limite_arquivos=5):
    arquivos = sorted(glob.glob(f"{pasta}/*.png"), key=os.path.getmtime)
    if len(arquivos) > limite_arquivos:
        for caminho in arquivos[:-limite_arquivos]:
            try:
                os.remove(caminho)
                print(f"🧼 Removido: {caminho}")
            except Exception as e:
                print(f"Erro ao remover {caminho}: {e}")

# Cadeia que gera SQL
sql_chain = (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt_sql
    | llm.bind(stop="\nSQL Result:")
    | extract_sql_from_llm_output
)

# Cadeia completa: SQL + execução + análise + resposta JSON
full_chain = (
    RunnablePassthrough.assign(sql_query=sql_chain).assign(
        schema=get_schema,
        response=lambda vars: run_query(vars["sql_query"]) if "sql_query" in vars else None
    )
    | prompt_chat
    | llm
    | output_parser
)

# Loop de execução
# if __name__ == "__main__":
#     print("Chatbot financeiro iniciado. Digite sua pergunta ou 'sair' para encerrar.")
#     while True:
#         question = input("\nPergunta: ")
#         if question.lower() in ["sair", "exit", "quit"]:
#             print("Encerrando chatbot.")
#             break

#         try:
#             result = full_chain.invoke({"question": question})
#             resposta = result["resposta"]
#             tipo_vis = result["tipo_visualizacao"]

#             print("\nResposta:", resposta)

#             if tipo_vis in ["pizza", "barras", "linhas"]:
#                 sql_query = sql_chain.invoke({"question": question})
#                 dados = run_query(sql_query)

#                 if is_valid_for_plot(dados):
#                     try:
#                         image_path = plot_chart(dados, chart_type=tipo_vis)
#                         print(f"✅ Gráfico gerado: {image_path}")
#                     except Exception as plot_error:
#                         print(f"⚠️ Erro ao gerar gráfico: {plot_error}")
#                 else:
#                     print("ℹ️ Dados não são adequados para o tipo de visualização proposto.")

#         except Exception as e:
#             print("\nErro:", e)