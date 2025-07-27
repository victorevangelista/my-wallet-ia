from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import current_user
from flask_migrate import Migrate
import flask
import dash
import os

from app.db_utils import get_raw_user_db_session, init_user_db_tables

from app.callbacks import data_callbacks

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Instância do Flask-Migrate

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Obtém o diretório do app
    
    # Caminho para o banco de dados principal de usuários
    # Garante que a pasta 'instance' exista
    INSTANCE_FOLDER_PATH = os.path.join(BASE_DIR, "..", "instance")
    if not os.path.exists(INSTANCE_FOLDER_PATH):
        os.makedirs(INSTANCE_FOLDER_PATH, exist_ok=True)
    DB_PATH = os.path.join(INSTANCE_FOLDER_PATH, "data.sqlite")

    # Inicializa o Flask
    app = Flask(__name__, instance_path=INSTANCE_FOLDER_PATH) # Define instance_path
    app.config["SECRET_KEY"] = os.urandom(12)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Adicione este trecho para servir imagens da pasta 'temp'
    @app.route('/temp/<path:filename>')
    def serve_temp(filename):
        # Caminho absoluto para a pasta /temp na raiz do projeto
        temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp'))
        return flask.send_from_directory(temp_dir, filename)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Integrando Flask-Migrate

    with app.app_context():
        # Importa apenas os modelos de usuário para o DB principal
        from app.models.user import Users
        db.create_all()  # Cria tabelas de usuário (ex: Users) se não existirem

    # Inicializa o Dash
    import dash_bootstrap_components as dbc

    # Definição dos estilos
    estilos = [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        "https://fonts.googleapis.com/icon?family=Material+Icons",
        dbc.themes.MINTY
    ]
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

    # Define o caminho para a pasta de assets na raiz do projeto
    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '', 'assets'))

    dash_app = dash.Dash(
        __name__, 
        server=app, 
        url_base_pathname="/",
        external_stylesheets=estilos + [dbc_css],  
        suppress_callback_exceptions=True,
        assets_folder=assets_path
    )

    # Define o layout do Dash
    from app.layouts.main_layout import layout as main_layout
    dash_app.layout = main_layout




    from app.models.user import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    # Importa callbacks
    from app.callbacks import login_callbacks, register_callbacks, sidebar_callbacks, dashboard_callbacks, extrato_despesas_callback, extrato_receitas_callback, import_ofx_callbacks

    # Registrando callbacks após a criação do Dash
    login_callbacks.register_callbacks(dash_app)
    register_callbacks.register_callbacks(dash_app)  
    data_callbacks.register_callbacks(dash_app)
    sidebar_callbacks.register_callbacks(dash_app)
    dashboard_callbacks.register_callbacks(dash_app)
    extrato_despesas_callback.register_callbacks(dash_app)
    extrato_receitas_callback.register_callbacks(dash_app)
    import_ofx_callbacks.register_callbacks(dash_app)

    from app.pages import login_page, register_page, not_found_page, data_page
    from dash.dependencies import Input, Output, State
    from flask_login import current_user
    from dash import no_update

    @dash_app.callback(
        [Output("page-content", "children"), Output("base-url", "href")], 
        [Input("base-url", "pathname")],
        [State("login-state", "data"), State("register-state", "data")]
    )
    def render_page_content(pathname, login_state, register_state):
        # Se o usuário já estiver autenticado e estiver em /login, redireciona para /data
        if current_user.is_authenticated and pathname in ["/login", "/"]:
            return data_page(current_user.username), "/data"

        # Se o usuário já estiver autenticado e estiver em /register, redireciona para /data
        if current_user.is_authenticated and pathname in ["/register"]:
            return data_page(current_user.username), "/data"
        
        # Se o usuário não estiver logado e tentar acessar /data, redireciona para /login
        if pathname in ["/data", "/extrato-despesas", "/extrato-receitas", "/import-ofx", "/fina-bot"]:
            if current_user.is_authenticated:
                return data_page(current_user.username), no_update
            return login_page(), "/login"

        # Páginas padrão (Login e Registro)
        if pathname == "/login" or pathname == "/": # Adicionado '/' para redirecionar para login
            return login_page(), no_update
        elif pathname == "/register":
            return register_page(), no_update
        return not_found_page(), no_update
    
    @app.before_request
    def before_request_user_db_session():
        """Cria uma sessão de BD para o usuário logado e a armazena em flask.g."""
        if current_user and current_user.is_authenticated:
            user_id = current_user.id
            session_attr = f"user_db_session_{user_id}"
            if not hasattr(g, session_attr):
                setattr(g, session_attr, get_raw_user_db_session(user_id))

    @app.teardown_appcontext
    def teardown_user_db_session(exception=None):
        """Fecha a sessão de BD do usuário armazenada em flask.g."""
        if current_user and current_user.is_authenticated:
            user_id = current_user.id
            session_attr = f"user_db_session_{user_id}"
            if hasattr(g, session_attr):
                session = getattr(g, session_attr)
                session.close()
                # print(f"Sessão do BD do usuário {user_id} fechada.") # Para debug

    return app, dash_app

def get_current_user_db_session():
    """Helper para obter a sessão de BD do usuário atual a partir de flask.g."""
    if current_user and current_user.is_authenticated:
        return getattr(g, f"user_db_session_{current_user.id}", None)
    return None
