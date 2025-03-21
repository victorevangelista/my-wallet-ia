from dash.dependencies import Input, Output, State
from werkzeug.security import generate_password_hash
from app.models.user import Users
from app import db
from dash import no_update  

def register_callbacks(dash_app):
    @dash_app.callback(
        [
            Output('register-state', 'data'),
            Output('alert-register-message', 'is_open'), 
            Output('alert-register-message', 'children'),
            Output('alert-register-message', 'color'),
            Output('user_register', 'value'),  
            Output('pwd_register', 'value'),   
            Output('email_register', 'value') 
        ],
        [
            Input('register-button', 'n_clicks'), 
            Input('register-keyboard', 'n_keydowns')
        ],
        [
            State('user_register', 'value'), 
            State('pwd_register', 'value'), 
            State('email_register', 'value'),
            State("alert-register-message", "is_open"),
        ],
    )
    def register(n_clicks, n_keydowns, username, password, email, is_open):
        if not n_clicks and not n_keydowns:
            return "", no_update, no_update, no_update, no_update, no_update, no_update
        
        if username and password and email:
            hashed_password = generate_password_hash(password)
            user = Users(username=username, password=hashed_password, email=email)
            try:
                db.session.add(user)
                db.session.commit()
                return "success", not is_open, "Usuário cadastrado com sucesso!", "success", "", "", ""
            except:
                db.session.rollback()
                return "error", not is_open, "Erro: Login ou e-mail já cadastrado.", "danger", no_update, no_update, no_update
        return "error", not is_open, "Erro: Faltou o preenchimento de algum campo.", "danger", no_update, no_update, no_update
