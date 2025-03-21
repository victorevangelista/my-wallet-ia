from app import db
from app.models.despesas import Despesas

def salvar_despesa(descricao, categoria, data, valor, parcelado, fixo):
    try:
        nova_despesa = Despesas(
            descricao=descricao,
            categoria=categoria,
            data=data,
            valor=float(valor),
            parcelado=parcelado,
            fixo=fixo
        )
        db.session.add(nova_despesa)
        db.session.commit()
        return True, "Despesa salva com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao salvar despesa: {str(e)}"


def buscar_despesas():
    """
    Retorna uma lista de todas as despesas cadastradas no banco de dados.
    """
    try:
        despesas = Despesas.query.all()  # Busca todas as despesas
        return [
            {
                "id": despesa.id,
                "descricao": despesa.descricao,
                "categoria": despesa.categoria,
                "data": despesa.data.strftime("%d/%m/%Y"),  # Formata a data
                "valor": despesa.valor,  
                "parcelado": despesa.parcelado,
                "fixo": despesa.fixo,
            }
            for despesa in despesas
        ]
    except Exception as e:
        return f"Erro ao buscar despesas: {str(e)}"


def update_despesa(despesa_id, descricao=None, categoria=None, data=None, valor=None, parcelado=None, fixo=None):
    """
    Atualiza uma despesa existente no banco de dados.
    
    Parâmetros:
        - despesa_id (int): ID da despesa a ser atualizada.
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
        despesa = Despesas.query.get(despesa_id)
        
        if not despesa:
            return False, "Erro: Despesa não encontrada."

        # Atualiza apenas os campos informados (que não são None)
        if descricao is not None:
            despesa.descricao = descricao
        if categoria is not None:
            despesa.categoria = categoria
        if data is not None:
            despesa.data = data
        if valor is not None:
            despesa.valor = float(valor)
        if parcelado is not None:
            despesa.parcelado = parcelado
        if fixo is not None:
            despesa.fixo = fixo

        db.session.commit()
        return True, "Despesa atualizada com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao atualizar despesa: {str(e)}"
