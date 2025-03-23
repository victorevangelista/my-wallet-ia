from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import current_user
from flask_migrate import Migrate
import dash
import os

from app.callbacks import data_callbacks

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # Instância do Flask-Migrate

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Obtém o diretório do app
    DB_PATH = os.path.join(BASE_DIR, "..", "instance", "data.sqlite")  # Caminho correto

    # Inicializa o Flask
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.urandom(12)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Integrando Flask-Migrate

    with app.app_context():
        from app import models  # Importa os modelos para serem reconhecidos
        db.create_all()  # Apenas para primeira inicialização

    # Inicializa o Dash
    import dash_bootstrap_components as dbc

    # Definição dos estilos
    estilos = [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
        "https://fonts.googleapis.com/icon?family=Material+Icons",
        dbc.themes.MINTY
    ]
    dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

    dash_app = dash.Dash(
        __name__, 
        server=app, 
        url_base_pathname="/",
        external_stylesheets=estilos + [dbc_css],  
        suppress_callback_exceptions=True
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
        if pathname in ["/data", "/extrato-despesas", "/extrato-receitas", "/import-ofx"]:
            if current_user.is_authenticated:
                return data_page(current_user.username), no_update
            return login_page(), "/login"

        # Páginas padrão (Login e Registro)
        if pathname in ["/login", "/"]:
            return login_page(), no_update
        elif pathname == "/register":
            return register_page(), no_update
        return not_found_page(), no_update
    
    return app, dash_app
