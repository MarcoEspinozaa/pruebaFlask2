from flask import Blueprint, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario

# Crear Blueprint para autenticación
auth_bp = Blueprint('auth', __name__)

# Ruta para cerrar sesión
@auth_bp.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Limpia todos los datos de la sesión
    flash('Has cerrado sesión exitosamente.', 'success')  # Mensaje de éxito
    return redirect(url_for('home'))  # Redirige a la página principal o de login

# Ruta para el registro de usuario
@auth_bp.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    email = request.form['email']
    contrasena = request.form['contrasena']
    confirmar_contrasena = request.form['confirmar_contrasena']
    
    # Validaciones
    if Usuario.query.filter_by(email=email).first():
        flash('El email ya está registrado.', 'danger')
    elif contrasena != confirmar_contrasena:
        flash('Las contraseñas no coinciden.', 'danger')
    else:
        hash_password = generate_password_hash(contrasena)
        new_user = Usuario(nombre=nombre, apellido=apellido, email=email, contrasena=hash_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso, ahora puede iniciar sesión.', 'success')
        return redirect(url_for('home'))
    
    return redirect(url_for('home'))

# Ruta para el inicio de sesión
@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contrasena = request.form['contrasena']
    
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and check_password_hash(usuario.contrasena, contrasena):
        session['usuario_id'] = usuario.id
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Credenciales incorrectas. Inténtelo de nuevo.', 'danger')
        return redirect(url_for('home'))