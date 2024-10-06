import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config
from os import path

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(get_remote_address)


def create_app(config_class=Config):
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)
    CORS(app, resources={r"*": {"origins": "http://localhost:4200/*"}}, supports_credentials=True)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Import and register blueprints
    from .routes.auth_route import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth/')
    from .routes.vaults_route import vaults_bp
    app.register_blueprint(vaults_bp, url_prefix='/vaults/')
    from .models import User
    with app.app_context():
        create_database()

    return app


def create_database():
    if not path.exists('../../../presgram_backend/instance/presgram.db'):
        db.create_all()
