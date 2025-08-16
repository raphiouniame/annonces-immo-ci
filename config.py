# config.py
# Configuration centralisée pour l'application Flask

import os
from datetime import timedelta

class Config:
    """
    Configuration de base partagée par tous les environnements.
    """
    # Clé secrète (obligatoire pour les sessions, CSRF, etc.)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Base de données
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Désactivé pour éviter les warnings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Vérifie la connexion avant chaque requête
        'pool_recycle': 300,    # Recycle les connexions toutes les 5 min
    }

    # Durée de la session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Activation du mode debug (à désactiver en production)
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Configuration pour l'environnement de développement.
    Utilise une base SQLite locale.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'


class ProductionConfig(Config):
    """
    Configuration pour l'environnement de production (Render).
    Utilise PostgreSQL via DATABASE_URL.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # En production, la DATABASE_URL commence souvent par 'postgres://' mais SQLAlchemy 1.4+ attend 'postgresql://'
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    # Sécurité supplémentaire en production
    SESSION_COOKIE_SECURE = True      # HTTPS uniquement
    REMEMBER_COOKIE_SECURE = True     # Pour 'Se souvenir de moi'
    SESSION_COOKIE_HTTPONLY = True    # Protège contre XSS
    SESSION_COOKIE_SAMESITE = 'Lax'   # Protection CSRF


class TestingConfig(Config):
    """
    Configuration pour les tests.
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False  # Désactivé pour faciliter les tests


# Mapping des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}