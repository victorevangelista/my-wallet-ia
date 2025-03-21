from app import db

class CatDespesas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), unique=True, nullable=False)

class CatReceitas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(50), unique=True, nullable=False)
