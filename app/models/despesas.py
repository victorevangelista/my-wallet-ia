from app import db

class Despesas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(250))
    categoria = db.Column(db.String(50))
    data = db.Column(db.Date)
    valor = db.Column(db.Float)
    parcelado = db.Column(db.Boolean)
    fixo = db.Column(db.Boolean)
