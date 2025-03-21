from app import db
from app.models.categoria import CatDespesas, CatReceitas

# Adicionar categoria de despesa
def adicionar_categoria_despesa(nome):
    if not nome:
        return False, "Nome da categoria não pode estar vazio!"
    
    if CatDespesas.query.filter_by(categoria=nome).first():
        return False, "Categoria já existe!"

    try:
        nova_categoria = CatDespesas(categoria=nome)
        db.session.add(nova_categoria)
        db.session.commit()
        return True, "Categoria de despesa adicionada!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao adicionar categoria: {str(e)}"

# Adicionar categoria de receita
def adicionar_categoria_receita(nome):
    if not nome:
        return False, "Nome da categoria não pode estar vazio!"
    
    if CatReceitas.query.filter_by(categoria=nome).first():
        return False, "Categoria já existe!"

    try:
        nova_categoria = CatReceitas(categoria=nome)
        db.session.add(nova_categoria)
        db.session.commit()
        return True, "Categoria de receita adicionada!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao adicionar categoria: {str(e)}"

# Remover categoria de despesa
def remover_categoria_despesa(nome):
    categoria = CatDespesas.query.filter_by(categoria=nome).first()
    if not categoria:
        return False, "Categoria não encontrada!"

    try:
        db.session.delete(categoria)
        db.session.commit()
        return True, "Categoria de despesa removida!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao remover categoria: {str(e)}"

# Remover categoria de receita
def remover_categoria_receita(nome):
    categoria = CatReceitas.query.filter_by(categoria=nome).first()
    if not categoria:
        return False, "Categoria não encontrada!"

    try:
        db.session.delete(categoria)
        db.session.commit()
        return True, "Categoria de receita removida!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao remover categoria: {str(e)}"


def buscar_cat_despesas():
    """
    Retorna uma lista de todas as categorias de despesas cadastradas no banco de dados.
    """
    try:
        cat_despesas = CatDespesas.query.all()  # Busca todas as despesas
        return True, [
            {
                "id": cat_despesa.id,
                "descricao": cat_despesa.categoria
            }
            for cat_despesa in cat_despesas
        ]
    except Exception as e:
        return False, f"Erro ao buscar categorias de despesas: {str(e)}"
    
def buscar_cat_receitas():
    """
    Retorna uma lista de todas as categorias de receitas cadastradas no banco de dados.
    """
    try:
        cat_receitas = CatReceitas.query.all()  # Busca todas as receitas
        return True, [
            {
                "id": cat_receita.id,
                "descricao": cat_receita.categoria
            }
            for cat_receita in cat_receitas
        ]
    except Exception as e:
        return False, f"Erro ao buscar categorias de receitas: {str(e)}"