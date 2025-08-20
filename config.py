"""
Configuration de l'application Flask pour différents environnements
"""

import os
from datetime import timedelta


class Config:
    """Configuration de base commune à tous les environnements"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Configuration des sessions
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # WTF-Forms
    WTF_CSRF_TIME_LIMIT = None


class DevelopmentConfig(Config):
    """Configuration pour le développement local"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    
    # Moins strict en développement
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuration pour la production sur Render"""
    DEBUG = False
    
    # Base de données Supabase
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    
    # Sécurité renforcée en production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Configuration pour Render
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,  # Render timeout à 300s
        'pool_timeout': 20,
        'max_overflow': 0,
        'pool_size': 5
    }


class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


# Mapping des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}