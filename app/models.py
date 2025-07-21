from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    especialidad = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')

    def __repr__(self):
        return f'<Cita {self.nombre} {self.apellido} - {self.fecha} - {self.especialidad}>'

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)