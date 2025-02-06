from models import db

# Modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)
    
    # Relación de un usuario a muchas visitas
    visitas = db.relationship('Visita', backref='usuario', lazy=True)
    me_gustas = db.relationship('MeGusta', backref='usuario', lazy=True)
