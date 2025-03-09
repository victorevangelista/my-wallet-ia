import pandas as pd
import os

path = "instance"

if("df_despesas.csv" in os.listdir(path)) and ("df_receitas.csv" in os.listdir(path)):
    df_despesas = pd.read_csv(f"{path}/df_despesas.csv", index_col=0, parse_dates=True)
    df_receitas = pd.read_csv(f"{path}/df_receitas.csv", index_col=0, parse_dates=True)
    df_despesas["Data"] = pd.to_datetime(df_despesas["Data"])
    df_despesas["Data"] = df_despesas["Data"].apply(lambda x: x.date())
    df_receitas["Data"] = pd.to_datetime(df_receitas["Data"])
    df_receitas["Data"] = df_receitas["Data"].apply(lambda x: x.date())

else:
    data_structure = {
        'Descrição': [],
        'Categoria': [],
        'Data': [],
        'Valor': [],
        'Parcelado': [],
        'Fixo': [],
    }
    df_despesas = pd.DataFrame(data_structure)
    df_receitas = pd.DataFrame(data_structure)
    df_despesas.to_csv(f"{path}/df_despesas.csv")
    df_receitas.to_csv(f"{path}/df_receitas.csv")


if("df_cat_despesas.csv" in os.listdir(path)) and ("df_cat_receitas.csv" in os.listdir(path)):
    df_cat_despesas = pd.read_csv(f"{path}/df_cat_despesas.csv", index_col=0, parse_dates=True)
    df_cat_receitas = pd.read_csv(f"{path}/df_cat_receitas.csv", index_col=0, parse_dates=True)
    cat_despesas = df_cat_despesas.values.tolist()
    cat_receitas = df_cat_receitas.values.tolist()

else:
    cat_despesas = {
        'Categoria': ["Alimentação", "Transporte", "Saúde", "Educação"],
    }
    cat_receitas = {
        'Categoria': ["Salário", "Investimentos", "Freela"],
    }
    df_cat_despesas = pd.DataFrame(cat_despesas, columns=['Categoria'])
    df_cat_receitas = pd.DataFrame(cat_receitas, columns=['Categoria'])
    df_cat_despesas.to_csv(f"{path}/df_cat_despesas.csv")
    df_cat_receitas.to_csv(f"{path}/df_cat_receitas.csv")