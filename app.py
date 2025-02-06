from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

from models import db, Usuario, Visita, MeGusta 

app = Flask(__name__)
app.secret_key = '@Admin123'

# Configuración de la base de datos MySQL usando la variable de entorno MYSQL_URL
app .config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:KkbUiHacxfrSPmQuYNVnlOOUUnufNANe@mysql.railway.internal:3306/railway"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()  # Limpia todos los datos de la sesión
    flash('Has cerrado sesión exitosamente.', 'success')  # Mensaje de éxito
    return redirect(url_for('home'))  # Redirige a la página principal o de login

# Ruta para el registro de usuario
@app.route('/register', methods=['POST'])
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
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    contrasena = request.form['contrasena']
    usuario = Usuario.query.filter_by(email=email).first()
    
    if usuario and check_password_hash(usuario.contrasena, contrasena):
        flash('Inicio de sesión exitoso.', 'success')
        
        # ID, nombre y apellido del usuario en la sesión
        session['usuario'] = {'id': usuario.id, 'nombre': usuario.nombre, 'apellido': usuario.apellido}
        
        return redirect(url_for('dashboard'))  # Redirige a la vista de películas
    else:
        flash('Credenciales incorrectas.', 'danger')
        return redirect(url_for('home'))  # Vuelve al login en caso de error

@app.route('/dashboard')
def dashboard():
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para ver la lista de visitas.', 'warning')
        return redirect(url_for('home'))  # Redirige a la página de home si no está autenticado
    
    id_usuario = session['usuario']['id']
    
    # Obtener las visitas creadas por el usuario actual, ordenadas por rating descendente
    mis_visitas = Visita.query.filter_by(id_usuario=id_usuario).order_by(Visita.rating.desc()).all()
    
    # Obtener las visitas creadas por otros usuarios, ordenadas por rating descendente
    otras_visitas = (
        db.session.query(Visita, Usuario.nombre, Usuario.apellido)
        .join(Usuario, Visita.id_usuario == Usuario.id) 
        .filter(Visita.id_usuario != id_usuario)  
        .order_by(Visita.rating.desc())  
        .all()
    )
    
    # Obtener el nombre del usuario actual para mostrarlo en el dashboard
    usuario = session.get('usuario')
    
    # Debug: 
    print("Mis visitas:", mis_visitas)
    print("Otras visitas:", otras_visitas)
    
    return render_template('dashboard.html', mis_visitas=mis_visitas, otras_visitas=otras_visitas, usuario=usuario)

@app.route('/nueva', methods=['GET', 'POST'])
def crear_visita():
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para crear una nueva visita.', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        parque = request.form['parque'].strip().lower()  # Convertir a minúsculas y eliminar espacios
        rating = request.form['rating']
        fecha_visita = request.form['fecha_visita']
        detalles = request.form['detalles']

        # ID del usuario en la sesión
        id_usuario = session['usuario']['id']

        # Verificar si el usuario ya tiene un parque con ese nombre
        if Visita.query.filter_by(parque=parque, id_usuario=id_usuario).first():
            flash('Ya has creado un parque con este nombre.', 'danger')
            return render_template('nueva_visita.html', parque=parque,rating=rating,fecha_hoy=fecha_visita,detalles=detalles,id_usuario=id_usuario)
        
        # Validar que la fecha no sea futura
        fecha_actual = datetime.now().date()
        fecha_visita_obj = datetime.strptime(fecha_visita, '%Y-%m-%d').date()

        if fecha_visita_obj > fecha_actual:
            flash('No se permiten fechas futuras. La fecha máxima es hoy.', 'danger')
            return render_template('nueva_visita.html', parque=parque,rating=rating,fecha_visita=fecha_visita,detalles=detalles,id_usuario=id_usuario)

        nueva_visita = Visita(parque=parque,rating=rating,fecha_visita=fecha_visita,detalles=detalles,id_usuario=id_usuario)
        db.session.add(nueva_visita)
        db.session.commit()

        # Mensaje de éxito y redirigir al dashboard
        flash('Visita creada correctamente.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('nueva_visita.html', fecha_hoy=fecha_hoy)  # Muestra el formulario

@app.route('/visita/editar/<int:id>', methods=['GET', 'POST'])
def editar_visita(id):
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:  
        flash('Por favor, inicia sesión para editar una visita.', 'warning')
        return redirect(url_for('home'))  
    
    visita = Visita.query.get_or_404(id)  # Buscar la visita o devuelve 404 si no existe
    if request.method == 'POST':
        # Obtener el nuevo parque
        nuevo_parque = request.form['parque']
        
        # Verificar si ya existe un parque con ese nombre, excluyendo el actual
        if Visita.query.filter(Visita.parque == nuevo_parque, Visita.id_visita != id).first():
            flash('Ya existe un parque con ese nombre.', 'danger')
            return render_template('nueva_pelicula.html', visita=visita, editar=True)

        # Actualizar los datos de la visita
        visita.parque = nuevo_parque
        visita.rating = request.form['rating']
        visita.fecha_visita = request.form['fecha_visita']
        visita.detalles = request.form['detalles']
        db.session.commit()
        flash('Visita actualizada correctamente.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('nueva_visita.html', visita=visita, editar=True)

@app.route('/visita/borrar/<int:id>', methods=['POST'])
def borrar_visita(id):
    visita = Visita.query.get_or_404(id)  # Busca la visita o devuelve 404 si no existe
    db.session.delete(visita)
    db.session.commit()
    flash('Visita borrada correctamente.', 'success')
    return redirect(url_for('dashboard'))  # Redirige al listado de visitas}

@app.route('/ver/<int:id>', methods=['GET'])
def ver_visita(id):
    # Verificar si el usuario ha iniciado sesión
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para ver una visita.', 'warning')
        return redirect(url_for('home'))  # Redirige a la página de home si no está autenticado
    
    #Visita
    visita = Visita.query.get_or_404(id)
    
    # Usuario asociado a la visita
    usuario = Usuario.query.get_or_404(visita.id_usuario)
    
    # Cantidad de "me gusta" asociados a la visita
    me_gusta = MeGusta.query.filter_by(id_visita=id).count()
    
    # Verificar si el usuario actual ya ha dado "me gusta" a esta visita
    usuario_actual_id = session['usuario']['id']
    ya_dio_me_gusta = MeGusta.query.filter_by(id_visita=id, id_usuario=usuario_actual_id).first() is not None
    
    # Renderizar la plantilla con los datos
    return render_template('ver_visita.html', visita=visita, usuario=usuario, me_gusta=me_gusta, ya_dio_me_gusta=ya_dio_me_gusta)

@app.route('/dar-me-gusta/<int:id>', methods=['POST'])
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

@app.route('/quitar-me-gusta/<int:id>', methods=['POST'])
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

@app.route('/contador-me-gusta/<int:id>', methods=['GET'])
def contador_me_gusta(id):
    me_gusta = MeGusta.query.filter_by(id_visita=id).count()
    return jsonify({"me_gusta": me_gusta})

@app.route('/test-db')
def test_db():
    try:
        db.engine.connect()
        return "¡Conexión a la base de datos exitosa!"
    except Exception as e:
        return f"Error al conectar a la base de datos: {str(e)}"
  

if __name__ == '__main__':
    app.run(debug=True)
