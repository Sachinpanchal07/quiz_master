import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.urandom(24).hex()  # Generates a secure random key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'quiz_master.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Enable debug mode for development

app_config = Config()
