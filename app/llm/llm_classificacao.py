#=============
#LLM
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv
import pandas as pd

_ = load_dotenv(find_dotenv())

def classificar_categorias_llm(row_data, template):
    """
    Classifica as transações importadas usando uma LLM com um prompt específico.
    
    :param row_data: Lista de dicionários representando as transações.
    :param template: Template do prompt a ser usado para a classificação.
    :return: DataFrame com as categorias classificadas.
    """
    if not row_data:
        raise ValueError("Nenhum dado para classificar.")
    if not isinstance(row_data, list):
        raise TypeError("row_data deve ser uma lista de dicionários.")  
    # Cria o template do prompt
    # O template deve ser definido fora desta função para evitar recarregamento desnecessário
    # Se o template for passado como argumento, ele deve ser uma string formatada corretamente
    if not template:
        raise ValueError("O template do prompt não pode ser vazio.")        
    
    row_data_df = pd.DataFrame(row_data)
    if row_data_df.empty:
        raise ValueError("O DataFrame de transações está vazio.") 
    
    prompt = PromptTemplate.from_template(template=template)
    chat = ChatGroq(model="llama-3.1-8b-instant")
    chain = prompt | chat

    categoria = []

    for row in row_data:
        result = chain.invoke(row["Descrição"]).content
        categoria += [result]
        print(result)

    row_data_df["Categoria"] = categoria

    return row_data_df