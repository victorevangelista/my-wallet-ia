from app.models.financial_data import Receita as FinancialReceita, CatReceitas

def salvar_receita_por_usuario(user_session, descricao, categoria_nome, data, valor, parcelado, fixo):
    try:
        # Busca o ID da categoria pelo nome, específico para receitas
        categoria_obj = None
        if categoria_nome:
            categoria_obj = user_session.query(CatReceitas).filter_by(categoria=categoria_nome).first()
        
        categoria_id_val = categoria_obj.id if categoria_obj else None

        nova_receita = FinancialReceita(
            descricao=descricao,
            categoria_id=categoria_id_val,
            data=data,
            valor=float(valor),
            parcelado=parcelado,
            fixo=fixo
        )
        user_session.add(nova_receita)
        user_session.commit()
        return True, "Receita salva com sucesso!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao salvar receita: {str(e)}")
        return False, f"Erro ao salvar receita: {str(e)}"


def buscar_receitas_por_usuario(user_session):
    """
    Retorna uma lista de todas as receitas cadastradas no banco de dados.
    """
    try:
        # Realiza um join com Categoria para obter o nome da categoria
        receitas = user_session.query(FinancialReceita).outerjoin(FinancialReceita.categoria).all()
        return [
            {
                "id": receita.id,
                "descricao": receita.descricao,
                "categoria": receita.categoria.categoria if receita.categoria else "Sem Categoria",
                "data": receita.data.strftime("%d/%m/%Y") if receita.data else None,
                "valor": receita.valor,
                "parcelado": receita.parcelado,
                "fixo": receita.fixo,
            }
            for receita in receitas
        ]
    except Exception as e:
        print(f"Erro ao buscar receitas: {str(e)}")
        return [] # Retorna lista vazia em caso de erro


def update_receita_por_usuario(user_session, receita_id, descricao=None, categoria_nome=None, data=None, valor=None, parcelado=None, fixo=None):
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
        receita = user_session.query(FinancialReceita).get(receita_id)
        
        if not receita:
            return False, "Erro: Receita não encontrada."

        # Atualiza apenas os campos informados (que não são None)
        if descricao is not None:
            receita.descricao = descricao
        if categoria_nome is not None:
            categoria_obj = None
            if categoria_nome: # Evita erro se categoria_nome for None ou ""
                categoria_obj = user_session.query(CatReceitas).filter_by(categoria=categoria_nome).first()
            receita.categoria_id = categoria_obj.id if categoria_obj else None
        if data is not None:
            receita.data = data # Assume que 'data' já é um objeto date
        if valor is not None:
            receita.valor = float(valor)
        if parcelado is not None:
            receita.parcelado = parcelado
        if fixo is not None:
            receita.fixo = fixo
        
        user_session.add(receita) # Adiciona à sessão para garantir que as mudanças sejam rastreadas
        user_session.commit()
        return True, "Receita atualizada com sucesso!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao atualizar receita: {str(e)}")
        return False, f"Erro ao atualizar receita: {str(e)}"
