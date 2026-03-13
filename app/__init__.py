from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    CORS(app) # Enable CORS for all routes

    from .routes import auth, patient, admin, tests
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(patient.bp, url_prefix='/api/patient')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(tests.bp, url_prefix='/api/tests')

    return app
