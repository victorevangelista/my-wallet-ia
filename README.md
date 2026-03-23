# My Wallet IA 💰

**My Wallet IA** é uma aplicação web interativa e completa para gestão financeira pessoal, desenvolvida com Python e Dash. O sistema permite um controle detalhado de receitas, despesas, acompanhamento de categorias, análise visual de fluxo de caixa em tempo real e, ainda, conta com integração de bots inteligentes para auxílio financeiro.

## 🚀 Funcionalidades

- **Dashboard Interativo:** Gráficos (Plotly) de pizza e barras para visualização do saldo, despesas por categoria e evolução do fluxo de caixa ao longo do tempo.
- **Filtros Avançados:** Filtre as análises no dashboard facilmente por Período, Categorias, Lançamentos Recorrentes (Fixos) ou Compras no Cartão de Crédito.
- **Controle de Lançamentos:**
  - Cadastre *Receitas* e *Despesas* rapidamente usando modais (janelas sobrepostas).
  - Adicione e remova categorias personalizadas.
  - Marque se a transação foi parcelada ou se é uma recorrência fixa mensal.
- **Extratos e Tabelas (Ag-Grid):** Tabelas ricas e responsivas na nuvem de extrato, com opções de edição em linha (inline editing) e deleção em lote.
- **Importação de OFX:** Carregue os dados do seu extrato bancário diretamente.
- **Autenticação de Usuários:** Sistema de login completo (`Flask-Login`) com isolamento de dados: cada pessoa usa um banco de dados independente e isolado.
- **Fina Bot:** Assistente IA (Inteligência Artificial) integrado para insights sobre o seu orçamento!

## 🛠️ Tecnologias Utilizadas

- **Backend / Tópicos Principais:** [Python 3](https://www.python.org/), [Flask](https://flask.palletsprojects.com/), [SQLAlchemy](https://www.sqlalchemy.org/) (ORM), e SQLite (Banco de dados).
- **Frontend / UI:** [Dash (by Plotly)](https://dash.plotly.com/), [Dash Bootstrap Components (DBC)](https://dash-bootstrap-components.opensource.faculty.ai/), HTML/CSS.
- **Visualização de Dados:** [Plotly Express / Graph Objects](https://plotly.com/python/), [Dash AG Grid](https://dash.plotly.com/dash-ag-grid)
- **Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)

## ⚙️ Pré-requisitos

Certifique-se de ter o Python instalado na sua máquina. É recomendado o uso do **Python 3.9+**.

## 📦 Instalação

1. Clone o repositório ou baixe os arquivos fonte:
   ```bash
   git clone https://github.com/SeuUsuario/my-wallet-ia.git
   cd my-wallet-ia
   ```

2. Crie e ative um ambiente virtual:
   - **No Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **No macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instale as dependências. Verifique se existe o arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *(Caso não tenha um `requirements.txt`, você pode gerar usando `pip freeze > requirements.txt` baseado no seu ambiente já configurado ou criar um manualmente instalando: `dash`, `dash-bootstrap-components`, `dash-ag-grid`, `pandas`, `plotly`, `Flask-SQLAlchemy`, `Flask-Login` e `Flask-Migrate`)*.

4. Execute as migrações (criação do DB central, se configurado):
   ```bash
   flask db upgrade # Se aplicável de acordo com as extensões SQLAlchemy
   ```

## ▶️ Como Executar

Com as bibliotecas instaladas e o ambiente ativado, execute a aplicação Dash (que geralmente é iniciada por um arquivo `run.py`, `app.py`, ou `main.py` na raiz do seu projeto):

```bash
python run.py  # (ou o nome do seu arquivo principal)
```

Abra o seu navegador web no endereço e porta indicados no terminal (por padrão: `http://127.0.0.1:8050/`).

## 📂 Estrutura do Projeto

```text
my-wallet-ia/
│
├── app/
│   ├── callbacks/       # Regras de negócio e triggers (Dashboard, Extratos, Sidebar, Login)
│   ├── components/      # UI isoladas (ex: sidebar.py, dashboard.py)
│   ├── layouts/         # Templates base de páginas
│   ├── models/          # Modelagem SQLAlchemy (ex: financial_data.py, user.py)
│   ├── pages/           # Instâncias das páginas (login_page, register_page)
│   ├── services/        # Acesso direto à dados (despesa_service, receita_service, etc)
│   └── __init__.py      # Fábrica de inicialização da Aplicação
│
├── assets/              # Imagens, CSS customizados, Logo e Favicon
├── instance/            # Onde os Bancos de Dados SQLite dos usuários são armazenados
├── temp/                # Diretório provisório (ex: Imagens temporárias de recibos)
└── .venv/               # Ambiente virtual Python
```

## 🤝 Contribuição

Contribuições são muito bem-vindas! Siga os passos:
1. Faça um Fork do projeto
2. Crie uma Branch para a sua feature (`git checkout -b feature/MinhaFeature`)
3. Faça o commit (`git commit -m 'Add: MinhaFeature'`)
4. Faça o push (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---
⌨️ Desenvolvido por Victor Evangelista.
