from flask import Flask
from .models import db
import os
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect  # Ya importado

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message = "Por favor inicia sesión."

csrf = CSRFProtect()  # Instanciado

def create_app():
    app = Flask(__name__)

    # Clave secreta para sesiones y flash
    app.config['SECRET_KEY'] = 'clave-super-secreta-123'

    # Ruta absoluta y segura para la base de datos
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "..", "citas.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Seguridad adicional de cookies
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Inicializa extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # <<--- ESTA LÍNEA ACTIVA CSRF GLOBALMENTE

    with app.app_context():
        db.create_all()
        from .models import Usuario

        @login_manager.user_loader
        def load_user(user_id):
            return Usuario.query.get(int(user_id))

    from .routes import main
    app.register_blueprint(main)

    return app
