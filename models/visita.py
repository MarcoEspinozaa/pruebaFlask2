from models import db

# Modelo de Visita
class Visita(db.Model):
    id_visita = db.Column(db.Integer, primary_key=True)
    parque = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.String(50), nullable=False)
    fecha_visita = db.Column(db.String(15), unique=True, nullable=False)
    detalles = db.Column(db.Text, nullable=False)
    
    # Clave foránea hacia el usuario
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relación de una visita a muchos "me gusta"
    me_gustas = db.relationship('MeGusta', backref='visita', lazy=True)