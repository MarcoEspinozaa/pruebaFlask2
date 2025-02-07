from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from models import db, Visita, Usuario  

# Crear el Blueprint para visitas
visitas_bp = Blueprint('visitas', __name__)

@visitas_bp.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para ver la lista de visitas.', 'warning')
        return redirect(url_for('home'))
    
    id_usuario = session['usuario']['id']
    mis_visitas = Visita.query.filter_by(id_usuario=id_usuario).order_by(Visita.rating.desc()).all()
    otras_visitas = (
        db.session.query(Visita, Usuario.nombre, Usuario.apellido)
        .join(Usuario, Visita.id_usuario == Usuario.id) 
        .filter(Visita.id_usuario != id_usuario)  
        .order_by(Visita.rating.desc())  
        .all()
    )
    usuario = session.get('usuario')
    return render_template('dashboard.html', mis_visitas=mis_visitas, otras_visitas=otras_visitas, usuario=usuario)

@visitas_bp.route('/nueva', methods=['GET', 'POST'])
def crear_visita():
    fecha_hoy = datetime.now().strftime('%Y-%m-%d')
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para crear una nueva visita.', 'warning')
        return redirect(url_for('home'))

    if request.method == 'POST':
        parque = request.form['parque'].strip().lower()
        rating = request.form['rating']
        fecha_visita = request.form['fecha_visita']
        detalles = request.form['detalles']
        id_usuario = session['usuario']['id']

        if Visita.query.filter_by(parque=parque, id_usuario=id_usuario).first():
            flash('Ya has creado un parque con este nombre.', 'danger')
            return render_template('nueva_visita.html', parque=parque, rating=rating, fecha_hoy=fecha_visita, detalles=detalles, id_usuario=id_usuario)
        
        fecha_actual = datetime.now().date()
        fecha_visita_obj = datetime.strptime(fecha_visita, '%Y-%m-%d').date()

        if fecha_visita_obj > fecha_actual:
            flash('No se permiten fechas futuras. La fecha máxima es hoy.', 'danger')
            return render_template('nueva_visita.html', parque=parque, rating=rating, fecha_visita=fecha_visita, detalles=detalles, id_usuario=id_usuario)

        nueva_visita = Visita(parque=parque, rating=rating, fecha_visita=fecha_visita, detalles=detalles, id_usuario=id_usuario)
        db.session.add(nueva_visita)
        db.session.commit()
        flash('Visita creada correctamente.', 'success')
        return redirect(url_for('visitas.dashboard'))  # Cambia a 'visitas.dashboard'

    return render_template('nueva_visita.html', fecha_hoy=fecha_hoy)

@visitas_bp.route('/visita/editar/<int:id>', methods=['GET', 'POST'])
def editar_visita(id):
    if 'usuario' not in session:  
        flash('Por favor, inicia sesión para editar una visita.', 'warning')
        return redirect(url_for('home'))  
    
    visita = Visita.query.get_or_404(id)
    if request.method == 'POST':
        nuevo_parque = request.form['parque']
        if Visita.query.filter(Visita.parque == nuevo_parque, Visita.id_visita != id).first():
            flash('Ya existe un parque con ese nombre.', 'danger')
            return render_template('nueva_visita.html', visita=visita, editar=True)

        visita.parque = nuevo_parque
        visita.rating = request.form['rating']
        visita.fecha_visita = request.form['fecha_visita']
        visita.detalles = request.form['detalles']
        db.session.commit()
        flash('Visita actualizada correctamente.', 'success')
        return redirect(url_for('visitas.dashboard'))  # Cambia a 'visitas.dashboard'
    
    return render_template('nueva_visita.html', visita=visita, editar=True)

@visitas_bp.route('/visita/borrar/<int:id>', methods=['POST'])
def borrar_visita(id):
    visita = Visita.query.get_or_404(id)
    db.session.delete(visita)
    db.session.commit()
    flash('Visita borrada correctamente.', 'success')
    return redirect(url_for('visitas.dashboard'))  # Cambia a 'visitas.dashboard'

@visitas_bp.route('/ver/<int:id>', methods=['GET'])
def ver_visita(id):
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para ver los detalles de la visita.', 'warning')
        return redirect(url_for('home'))
    
    visita = Visita.query.get_or_404(id)
    return render_template('ver_visita.html', visita=visita)