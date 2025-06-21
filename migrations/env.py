import logging
from logging.config import fileConfig

from flask import current_app

from alembic import context

# Adicionado para acessar UserDataBase e utilitários
import os
from sqlalchemy import create_engine
from app.db_utils import UserDataBase # Assumindo que UserDataBase está acessível aqui

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')


def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine


def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace(
            '%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_metadata():
    if hasattr(target_db, 'metadatas'):
        return target_db.metadatas[None]
    return target_db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                # Ajuste para não logar "No changes" múltiplas vezes se um DB de usuário não tiver mudanças
                # logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives
    
    # --- Migração do Banco de Dados Principal ---
    logger.info("Iniciando migração para o banco de dados principal...")
    connectable_main = get_engine()
    with connectable_main.connect() as connection_main:
        context.configure(
            connection=connection_main,
            target_metadata=get_metadata(), # Metadados do DB principal (Users)
            **conf_args
        )
        with context.begin_transaction():
            context.run_migrations()
    logger.info("Banco de dados principal migrado.")

    # --- Migração dos Bancos de Dados dos Usuários ---
    logger.info("\nIniciando migração para bancos de dados de usuários...")
    user_db_parent_dir = os.path.join(current_app.instance_path, "user_data")

    if not os.path.exists(user_db_parent_dir):
        logger.info(f"Diretório de dados de usuário '{user_db_parent_dir}' não encontrado. Pulando migrações de usuários.")
    else:
        for filename in os.listdir(user_db_parent_dir):
            if filename.startswith("user_") and filename.endswith(".sqlite"):
                user_db_path = os.path.join(user_db_parent_dir, filename)
                logger.info(f"Processando banco de dados do usuário: {user_db_path}")
                
                user_engine = create_engine(f"sqlite:///{user_db_path}")
                with user_engine.connect() as user_connection:
                    context.configure(
                        connection=user_connection,
                        target_metadata=UserDataBase.metadata, # Metadados dos dados financeiros (Despesa, Receita, etc.)
                        **conf_args 
                    )
                    with context.begin_transaction():
                        context.run_migrations()
                    logger.info(f"Banco de dados {filename} migrado.")
    logger.info("Migração dos bancos de dados de usuários concluída.")

    # Código original para um único DB foi movido e adaptado acima.
    # O código abaixo não será mais executado diretamente se a lógica acima for completa.
    # Se quiser manter uma execução única para o DB principal e depois o loop,
    # a estrutura acima já faz isso.
    # Se a intenção era ter apenas uma configuração de contexto por execução do `flask db upgrade`,
    # então o Alembic precisaria ser invocado programaticamente para cada DB de usuário,
    # o que é mais complexo do que modificar o env.py desta forma.

    # Código original comentado/removido para evitar dupla execução no DB principal:
    # connectable = get_engine()
    #
    # with connectable.connect() as connection:
    #     context.configure(
    #         connection=connection,
    #         target_metadata=get_metadata(),
    #         **conf_args
    #     )
    #
    #     with context.begin_transaction():
    #         context.run_migrations()



if context.is_offline_mode():
    # A migração offline para múltiplos bancos de dados dinâmicos é mais complexa
    # e geralmente não é o foco. Esta seção provavelmente precisaria de uma
    # lógica similar à online se fosse necessário suportá-la completamente.
    # Por simplicidade, vamos manter a migração offline focada no DB principal.
    run_migrations_offline()
else:
    run_migrations_online()
