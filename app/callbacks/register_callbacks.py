from dash.dependencies import Input, Output, State
from werkzeug.security import generate_password_hash
from app.models.user import Users
from app import db
from dash import no_update
from app.db_utils import init_user_db_tables # Importar a função de inicialização

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
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256:600000")
            user = Users(username=username, password=hashed_password, email=email)
            try:
                db.session.add(user)
                db.session.commit()
                # Após o commit do usuário, inicialize as tabelas do seu banco de dados de dados
                # user.id estará disponível após o commit
                init_user_db_tables(user.id)
                return "success", not is_open, "Usuário cadastrado com sucesso!", "success", "", "", ""
            except Exception as e: # Seja mais específico com as exceções se possível (ex: IntegrityError)
                db.session.rollback()
                # print(f"Erro no registro: {e}") # Para debug
                # Verificar se é um erro de constraint (usuário/email já existe)
                return "error", not is_open, "Erro: Login ou e-mail já cadastrado ou outro erro ocorreu.", "danger", no_update, no_update, no_update
        return "error", not is_open, "Erro: Faltou o preenchimento de algum campo.", "danger", no_update, no_update, no_update
