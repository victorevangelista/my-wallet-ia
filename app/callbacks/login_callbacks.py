from dash.dependencies import Input, Output, State
from flask_login import login_user
from werkzeug.security import check_password_hash
from app.models.user import Users
from dash import no_update  

def register_callbacks(dash_app):
    @dash_app.callback(
        [
            Output('login-state', 'data'), 
            Output('redirect', 'href'),
            Output('alert-login-message', 'is_open'), 
            Output('alert-login-message', 'children'),
            Output('alert-login-message', 'color'),
        ],
        [
            Input('login_button', 'n_clicks'), 
            Input('login-keyboard', 'n_keydowns')
        ],
        [
            State('user_login', 'value'), 
            State('pwd_login', 'value'),
            State("alert-login-message", "is_open"),
        ],
    )
    def successful(n_clicks, n_keydowns, username, password, is_open):
        if not n_clicks and not n_keydowns:
            return "", no_update, no_update, "Erro: Login e/ou senha inválido.", "danger"

        user = Users.query.filter_by(username=username).first()
        if user and password is not None:
            if check_password_hash(user.password, password):
                success = login_user(user)
                return "success", "/data", no_update, no_update, no_update  
            else:
                return "error", no_update, not is_open, "Erro: Login e/ou senha inválido(s).", "danger"  # Mantém a página de login se falhar
        else:
            return "error", no_update, not is_open, "Erro: Login e/ou senha não preenchido(s).", "danger"  # Mantém a página de login se falhar
        