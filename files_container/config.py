import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///examvault.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key_here'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
