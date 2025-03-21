from dash import html, dcc
import dash_bootstrap_components as dbc

def render_layout():
    return html.Div([
            html.H1("Oops!"),
            html.H3("404 - Page Not Found"),
            dcc.Link("Go To Dashboard", href="/data", className="btn btn-primary"),
        ], className="page-not-found")