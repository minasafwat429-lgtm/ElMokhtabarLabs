import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'
    # Database configuration
    # ----------------------
    # Defaulting to standard XAMPP credentials (user: root, password: empty)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost/ElMokhtabarLabs'
    
    # OPTION 2: SQL Server (If using SSMS)
    # SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://sa:password@localhost/ElMokhtabarLabs?driver=ODBC+Driver+17+for+SQL+Server'
    
    # OPTION 3: SQLite (Fallback)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///elmokhtabar.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backend', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
