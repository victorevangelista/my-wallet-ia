import warnings
# Silenciar avisos de SSL/urllib3 de forma agressiva antes de qualquer import
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")
warnings.filterwarnings("ignore", category=ImportWarning)

import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

from app import create_app

app, dash_app = create_app()

if __name__ == "__main__":
    dash_app.run(debug=True, port=8050)  # Flask inicia o Dash internamente
