from dash import html, dcc
import dash_bootstrap_components as dbc
from app.layouts.login_layout import render_layout

def get_layout():
    return render_layout()
