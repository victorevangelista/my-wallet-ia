import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
import joblib

def treinar_classificador(df, modelo_path='modelo_classificador.joblib'):
    """
    Treina um classificador com base na coluna 'descricao' e 'categoria' de um DataFrame.
    Salva o modelo no disco.
    """
    if 'descricao' not in df.columns or 'categoria' not in df.columns:
        raise ValueError("DataFrame deve conter as colunas 'descricao' e 'categoria'.")

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', RandomForestClassifier(random_state=42))
    ])

    pipeline.fit(df['descricao'], df['categoria'])

    # Salva modelo no disco
    joblib.dump(pipeline, modelo_path)

    return pipeline


def classificar_transacoes(df, clf=None, modelo_path='modelo_classificador.joblib'):
    """
    Classifica um DataFrame com base na coluna 'descricao'.
    Retorna um novo DataFrame com a coluna 'categoria_prevista'.
    """
    if 'Descrição' not in df.columns:
        raise ValueError("DataFrame deve conter a coluna 'descricao'.")

    # Carrega modelo se não foi passado
    if clf is None:
        clf = joblib.load(modelo_path)

    # Previsão
    df_resultado = df.copy()
    df_resultado['categoria_prevista'] = clf.predict(df_resultado['Descrição'])

    return df_resultado



def classificar_categorias_ML(row_data, train_data):
    """
    Classifica as transações importadas usando uma LLM com um conjunto de dados de treinamento.
    
    :param row_data: Lista de dicionários representando as transações.
    :param train_data: DataFrame com os dados de treinamento para a classificação.
    :return: DataFrame com as categorias classificadas.
    """
    if not row_data:
        raise ValueError("Nenhum dado para classificar.")
    
    row_data_df = pd.DataFrame(row_data)
    #remove a coluna Categoria se existir
    if 'Categoria' in row_data_df.columns:
        row_data_df.drop(columns=['Categoria'], inplace=True)

    # Treinar
    clf = treinar_classificador(train_data)

    # Classificar
    row_data_df = classificar_transacoes(row_data_df, clf)

    if row_data_df.empty:
        raise ValueError("O DataFrame de transações está vazio.")
    
    # Renomeia a coluna de categoria prevista
    row_data_df.rename(columns={'categoria_prevista': 'Categoria'}, inplace=True)
        
    # Retorna o DataFrame com as categorias classificadas
    return row_data_df
