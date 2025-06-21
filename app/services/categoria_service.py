# Removido: from app import db
# Assumindo que CatDespesas e CatReceitas foram movidos para financial_data.py e usam UserDataBase
from app.models.financial_data import CatDespesas, CatReceitas 

# Adicionar categoria de despesa
def adicionar_categoria_despesa_por_usuario(user_session, nome):
    if not nome:
        return False, "Nome da categoria não pode estar vazio!"
    
    if user_session.query(CatDespesas).filter_by(categoria=nome).first():
        return False, "Categoria já existe!"

    try:
        nova_categoria = CatDespesas(categoria=nome)
        user_session.add(nova_categoria)
        user_session.commit()
        return True, "Categoria de despesa adicionada!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao adicionar categoria de despesa: {str(e)}")
        return False, f"Erro ao adicionar categoria: {str(e)}"

# Adicionar categoria de receita
def adicionar_categoria_receita_por_usuario(user_session, nome):
    if not nome:
        return False, "Nome da categoria não pode estar vazio!"
    
    if user_session.query(CatReceitas).filter_by(categoria=nome).first():
        return False, "Categoria já existe!"

    try:
        nova_categoria = CatReceitas(categoria=nome)
        user_session.add(nova_categoria)
        user_session.commit()
        return True, "Categoria de receita adicionada!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao adicionar categoria de receita: {str(e)}")
        return False, f"Erro ao adicionar categoria: {str(e)}"

# Remover categoria de despesa
def remover_categoria_despesa_por_usuario(user_session, nome):
    categoria = user_session.query(CatDespesas).filter_by(categoria=nome).first()
    if not categoria:
        return False, "Categoria não encontrada!"

    try:
        # TODO: Adicionar verificação se a categoria está em uso por alguma Despesa
        user_session.delete(categoria)
        user_session.commit()
        return True, "Categoria de despesa removida!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao remover categoria de despesa: {str(e)}")
        return False, f"Erro ao remover categoria: {str(e)}"

# Remover categoria de receita
def remover_categoria_receita_por_usuario(user_session, nome):
    categoria = user_session.query(CatReceitas).filter_by(categoria=nome).first()
    if not categoria:
        return False, "Categoria não encontrada!"

    try:
        # TODO: Adicionar verificação se a categoria está em uso por alguma Receita
        user_session.delete(categoria)
        user_session.commit()
        return True, "Categoria de receita removida!"
    except Exception as e:
        user_session.rollback()
        print(f"Erro ao remover categoria de receita: {str(e)}")
        return False, f"Erro ao remover categoria: {str(e)}"


def buscar_cat_despesas_por_usuario(user_session):
    """
    Retorna uma lista de todas as categorias de despesas cadastradas no banco de dados.
    """
    try:
        cat_despesas = user_session.query(CatDespesas).all()
        return True, [
            {
                "id": cat_despesa.id,
                "categoria": cat_despesa.categoria # Alterado de 'descricao' para 'categoria'
            }
            for cat_despesa in cat_despesas
        ]
    except Exception as e:
        print(f"Erro ao buscar categorias de despesas: {str(e)}")
        return False, []
    
def buscar_cat_receitas_por_usuario(user_session):
    """
    Retorna uma lista de todas as categorias de receitas cadastradas no banco de dados.
    """
    try:
        cat_receitas = user_session.query(CatReceitas).all()
        return True, [
            {
                "id": cat_receita.id,
                "categoria": cat_receita.categoria # Alterado de 'descricao' para 'categoria'
            }
            for cat_receita in cat_receitas
        ]
    except Exception as e:
        print(f"Erro ao buscar categorias de receitas: {str(e)}")
        return False, []