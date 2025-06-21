from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db_utils import UserDataBase # Importa a Base específica para dados do usuário


class CatDespesas(UserDataBase): # Mude de db.Model para UserDataBase
    __tablename__ = 'cat_despesas' # Nome da tabela para o DB do usuário
    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String(100), nullable=False)
    # Se você quiser que o nome da categoria seja único por usuário:
    # __table_args__ = (UniqueConstraint('categoria', name='_user_cat_despesa_uc'),)

    def __repr__(self):
        return f'<CatDespesas {self.id}: {self.categoria}>'

class CatReceitas(UserDataBase): # Mude de db.Model para UserDataBase
    __tablename__ = 'cat_receitas' # Nome da tabela para o DB do usuário
    id = Column(Integer, primary_key=True, autoincrement=True)
    categoria = Column(String(100), nullable=False)
    # Se você quiser que o nome da categoria seja único por usuário:
    # __table_args__ = (UniqueConstraint('categoria', name='_user_cat_receita_uc'),)

    def __repr__(self):
        return f'<CatReceitas {self.id}: {self.categoria}>'



class Receita(UserDataBase):
    __tablename__ = 'receitas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    data = Column(Date, nullable=False)
    parcelado = Column(Boolean, default=False) 
    fixo = Column(Boolean, default=False)     
    
    categoria_id = Column(Integer, ForeignKey('cat_receitas.id'), nullable=True)
    categoria = relationship("CatReceitas")

    def __repr__(self):
        return f"<Receita {self.id} {self.descricao} {self.valor}>"

class Despesa(UserDataBase):
    __tablename__ = 'despesas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    descricao = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    data = Column(Date, nullable=False)
    parcelado = Column(Boolean, default=False) 
    fixo = Column(Boolean, default=False)   

    categoria_id = Column(Integer, ForeignKey('cat_despesas.id'), nullable=True)
    categoria = relationship("CatDespesas")

    def __repr__(self):
        return f"<Despesa {self.id} {self.descricao} {self.valor}>"

# Adicione outros modelos financeiros conforme necessário (ex: Contas, Transações OFX importadas)
# Lembre-se de importá-los em init_user_db_tables e get_raw_user_db_session em db_utils.py
