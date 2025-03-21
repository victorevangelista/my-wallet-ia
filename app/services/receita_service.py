from app import db
from app.models.receitas import Receitas

def salvar_receita(descricao, categoria, data, valor, parcelado, fixo):
    try:
        nova_receita = Receitas(
            descricao=descricao,
            categoria=categoria,
            data=data,
            valor=float(valor),
            parcelado=parcelado,
            fixo=fixo
        )
        db.session.add(nova_receita)
        db.session.commit()
        return True, "Receita salva com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao salvar receita: {str(e)}"


def buscar_receitas():
    """
    Retorna uma lista de todas as receitas cadastradas no banco de dados.
    """
    try:
        receitas = Receitas.query.all()  # Busca todas as receitas
        return [
            {
                "id": receita.id,
                "descricao": receita.descricao,
                "categoria": receita.categoria,
                "data": receita.data.strftime("%d/%m/%Y"),  # Formata a data
                "valor": receita.valor,
                "parcelado": receita.parcelado,
                "fixo": receita.fixo,
            }
            for receita in receitas
        ]
    except Exception as e:
        return f"Erro ao buscar receitas: {str(e)}"


def update_receita(receita_id, descricao=None, categoria=None, data=None, valor=None, parcelado=None, fixo=None):
    """
    Atualiza uma receita existente no banco de dados.
    
    Parâmetros:
        - receita_id (int): ID da receita a ser atualizada.
        - descricao (str): Nova descrição (opcional).
        - categoria (str): Nova categoria (opcional).
        - data (str): Nova data no formato 'YYYY-MM-DD' (opcional).
        - valor (float): Novo valor (opcional).
        - parcelado (bool): Atualizar se é parcelado ou não (opcional).
        - fixo (bool): Atualizar se é fixo ou não (opcional).

    Retorno:
        - (bool, str): Sucesso ou falha e mensagem de retorno.
    """
    try:
        receita = Receitas.query.get(receita_id)
        
        if not receita:
            return False, "Erro: Receita não encontrada."

        # Atualiza apenas os campos informados (que não são None)
        if descricao is not None:
            receita.descricao = descricao
        if categoria is not None:
            receita.categoria = categoria
        if data is not None:
            receita.data = data
        if valor is not None:
            receita.valor = float(valor)
        if parcelado is not None:
            receita.parcelado = parcelado
        if fixo is not None:
            receita.fixo = fixo

        db.session.commit()
        return True, "Receita atualizada com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao atualizar receita: {str(e)}"
