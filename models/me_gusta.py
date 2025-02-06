from models import db

# Modelo de MeGusta
class MeGusta(db.Model):
    id_megusta = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_visita = db.Column(db.Integer, db.ForeignKey('visita.id_visita'), nullable=False)
    
    # Asegurar que un usuario no pueda dar más de un "me gusta" a la misma visita
    __table_args__ = (
        db.UniqueConstraint('id_usuario', 'id_visita', name='unique_megusta'),
    )