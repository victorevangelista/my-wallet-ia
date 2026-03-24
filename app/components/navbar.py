from dash import html
import dash_bootstrap_components as dbc
from flask_login import current_user

def create_navbar(user):
    # Fallback para imagem do usuário se não existir
    user_img = "/assets/img_hom.png" # Placeholder padrão
    
    navbar = dbc.Navbar(
        dbc.Container(
            [
                # Lado Esquerdo: Marca + Botão de Toggle
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                html.I(className="fa fa-bars"),
                                id="sidebar-toggle",
                                color="light",
                                outline=True,
                                className="me-3",
                                size="sm"
                            ),
                            width="auto"
                        ),
                        dbc.Col(
                            dbc.NavbarBrand("My Budget", className="navbar-brand-custom", href="/data")
                        ),
                    ],
                    align="center",
                    className="g-0",
                ),
                
                # Lado Direito: Usuário + Logout
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.DropdownMenu(
                                children=[
                                    dbc.DropdownMenuItem(divider=True),
                                    dbc.DropdownMenuItem("Logout", href="/logout", external_link=True),
                                ],
                                nav=True,
                                in_navbar=True,
                                label=html.Div([
                                    html.Span(user.username, className="me-2 text-white"),
                                    html.Img(src=user_img, className="user-avatar-nav")
                                ], className="d-flex align-items-center"),
                                align_end=True,
                                caret=False,
                                toggle_style={"textDecoration": "none"}
                            ),
                            width="auto"
                        ),
                    ],
                    align="center",
                    className="g-0 ms-auto",
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="navbar-custom",
        id="top-navbar"
    )
    return navbar
