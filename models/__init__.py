from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .usuario import Usuario
from .visita import Visita
from .me_gusta import MeGusta
