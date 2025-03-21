from dash import html, dcc
import dash_bootstrap_components as dbc
from app.layouts.data_layout import render_layout

def get_layout(username):
    return render_layout(username)
