import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app

# Base declarativa para os modelos de dados financeiros específicos do usuário
UserDataBase = declarative_base()

# Diretório para armazenar os bancos de dados dos usuários
# Usamos current_app.instance_path para garantir que está dentro da pasta 'instance' do Flask
USER_DB_PARENT_DIR_NAME = "user_data"

def get_user_db_dir():
    """Retorna o caminho absoluto para o diretório de bancos de dados dos usuários."""
    # Garante que o diretório exista
    path = os.path.join(current_app.instance_path, USER_DB_PARENT_DIR_NAME)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def get_user_db_path(user_identifier):
    """Retorna o caminho para o arquivo SQLite do usuário."""
    return os.path.join(get_user_db_dir(), f"user_{user_identifier}.sqlite")

_user_engines = {} # Cache para engines, para não recriar toda vez
_user_session_factories = {} # Cache para session factories

def get_user_db_engine(user_identifier):
    """Cria ou obtém do cache uma engine SQLAlchemy para o banco de dados do usuário."""
    if user_identifier not in _user_engines:
        db_path = get_user_db_path(user_identifier)
        _user_engines[user_identifier] = create_engine(f"sqlite:///{db_path}")
    return _user_engines[user_identifier]

def init_user_db_tables(user_identifier):
    """
    Cria as tabelas no banco de dados do usuário, se não existirem.
    Esta função deve ser chamada após o registro do usuário.
    """
    engine = get_user_db_engine(user_identifier)
    # Importar modelos financeiros aqui ANTES de create_all
    # Isso garante que UserDataBase.metadata conheça as tabelas.
    # Se os modelos estiverem em app.models.financial_data, importe-os aqui.
    from app.models.financial_data import Receita, Despesa, CatDespesas, CatReceitas
    UserDataBase.metadata.create_all(engine)
    # print(f"Tabelas verificadas/criadas para o usuário {user_identifier} em {get_user_db_path(user_identifier)}")

def get_raw_user_db_session(user_identifier):
    """
    Retorna uma nova sessão SQLAlchemy para o banco de dados do usuário.
    O chamador é responsável por gerenciar o ciclo de vida desta sessão (geralmente via g e teardown_appcontext).
    """
    if user_identifier not in _user_session_factories:
        engine = get_user_db_engine(user_identifier)
        # Garante que as tabelas existam ao criar a factory pela primeira vez para um usuário
        # Isso é importante se um usuário antigo logar e o DB ainda não foi "tocado" por esta lógica.
        from app.models.financial_data import Receita, Despesa, CatDespesas, CatReceitas
        UserDataBase.metadata.create_all(engine)
        _user_session_factories[user_identifier] = sessionmaker(bind=engine)
    
    Session = _user_session_factories[user_identifier]
    return Session()
