from flask import Blueprint, jsonify, session
from models import db, MeGusta  

# Crear el Blueprint para "me gusta"
me_gusta_bp = Blueprint('me_gusta', __name__)

@me_gusta_bp.route('/dar-me-gusta/<int:id>', methods=['POST'])
def dar_me_gusta(id):
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Por favor, inicia sesión."})
    
    usuario_actual_id = session['usuario']['id']
    
    # Verificar si el usuario ya ha dado "me gusta"
    if MeGusta.query.filter_by(id_visita=id, id_usuario=usuario_actual_id).first():
        return jsonify({"success": False, "message": "Ya has dado 'me gusta' a esta visita."})
    
    # Crear un nuevo "me gusta"
    nuevo_me_gusta = MeGusta(id_visita=id, id_usuario=usuario_actual_id)
    db.session.add(nuevo_me_gusta)
    db.session.commit()
    
    return jsonify({"success": True})

@me_gusta_bp.route('/quitar-me-gusta/<int:id>', methods=['POST'])
def quitar_me_gusta(id):
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Por favor, inicia sesión."})
    
    usuario_actual_id = session['usuario']['id']
    
    # Buscar y eliminar el "me gusta"
    me_gusta = MeGusta.query.filter_by(id_visita=id, id_usuario=usuario_actual_id).first()
    if me_gusta:
        db.session.delete(me_gusta)
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "No has dado 'me gusta' a esta visita."})

@me_gusta_bp.route('/contador-me-gusta/<int:id>', methods=['GET'])
def contador_me_gusta(id):
    me_gusta = MeGusta.query.filter_by(id_visita=id).count()
    return jsonify({"me_gusta": me_gusta})