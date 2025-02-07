from flask import Flask, render_template, request, url_for, redirect, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

from models import db, Usuario, Visita, MeGusta 
from scripts.auth import auth_bp  
from scripts.visitas import visitas_bp  
from scripts.me_gusta import me_gusta_bp  

app = Flask(__name__)
app.secret_key = '@Admin123'

# Configuración de la base de datos MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:uatqmVilKDcIqIAblPMDtLPmxoRowowr@mysql-05hd.railway.internal:3306/railway"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prueba2.db"  # Cambia a SQLite
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# Registrar los blueprints
app.register_blueprint(auth_bp)  # Registra el Blueprint de autenticación
app.register_blueprint(visitas_bp)  # Registra el Blueprint de visitas
app.register_blueprint(me_gusta_bp)  # Registra el Blueprint de me gusta

# Ruta principal
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
