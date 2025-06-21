from app.models.financial_data import Despesa as FinancialDespesa, CatDespesas

def salvar_despesa_por_usuario(user_session, descricao, categoria_nome, data, valor, parcelado, fixo):
    try:
        # Busca o ID da categoria pelo nome, específico para despesas
        categoria_obj = None
        if categoria_nome:
            categoria_obj = user_session.query(CatDespesas).filter_by(categoria=categoria_nome).first()
        
        categoria_id_val = categoria_obj.id if categoria_obj else None

        nova_despesa = FinancialDespesa(
            descricao=descricao,
            categoria_id=categoria_id_val,
            data=data,
            valor=float(valor),
            parcelado=parcelado,
            fixo=fixo
        )
        user_session.add(nova_despesa)
        user_session.commit()
        return True, "Despesa salva com sucesso!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao salvar despesa: {str(e)}")
        return False, f"Erro ao salvar despesa: {str(e)}"


def buscar_despesas_por_usuario(user_session):
    """
    Retorna uma lista de todas as despesas cadastradas no banco de dados.
    """
    try:
        despesas = user_session.query(FinancialDespesa).outerjoin(FinancialDespesa.categoria).all()
        return [
            {
                "id": despesa.id,
                "descricao": despesa.descricao,
                "categoria": despesa.categoria.categoria if despesa.categoria else "Sem Categoria",
                "data": despesa.data.strftime("%d/%m/%Y") if despesa.data else None,
                "valor": despesa.valor,  
                "parcelado": despesa.parcelado,
                "fixo": despesa.fixo,
            }
            for despesa in despesas
        ]
    except Exception as e:
        print(f"Erro ao buscar despesas: {str(e)}")
        return [] # Retorna lista vazia em caso de erro


def update_despesa_por_usuario(user_session, despesa_id, descricao=None, categoria_nome=None, data=None, valor=None, parcelado=None, fixo=None):
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
        despesa = user_session.query(FinancialDespesa).get(despesa_id)
        
        if not despesa:
            return False, "Erro: Despesa não encontrada."

        # Atualiza apenas os campos informados (que não são None)
        if descricao is not None:
            despesa.descricao = descricao
        if categoria_nome is not None:
            categoria_obj = None
            if categoria_nome: # Evita erro se categoria_nome for None ou ""
                categoria_obj = user_session.query(CatDespesas).filter_by(categoria=categoria_nome).first()
            despesa.categoria_id = categoria_obj.id if categoria_obj else None
        if data is not None:
            despesa.data = data # Assume que 'data' já é um objeto date
        if valor is not None:
            despesa.valor = float(valor)
        if parcelado is not None:
            despesa.parcelado = parcelado
        if fixo is not None:
            despesa.fixo = fixo
        
        user_session.add(despesa) # Adiciona à sessão para garantir que as mudanças sejam rastreadas
        user_session.commit()
        return True, "Despesa atualizada com sucesso!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao atualizar despesa: {str(e)}")
        return False, f"Erro ao atualizar despesa: {str(e)}"
