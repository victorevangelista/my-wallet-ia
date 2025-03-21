from app import create_app

app, dash_app = create_app()

if __name__ == "__main__":
    dash_app.run(debug=True, port=8050)  # Flask inicia o Dash internamente
