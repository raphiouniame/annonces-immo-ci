# routes/__init__.py
"""
Package contenant tous les blueprints (routes) de l'application.
Ce fichier permet d'importer facilement les blueprints dans app.py
"""

# Import des blueprints pour faciliter leur utilisation
from .main import main
from .auth import auth  
from .listings import listings
from .admin import admin

# Liste des blueprints disponibles (optionnel, pour documentation)
__all__ = ['main', 'auth', 'listings', 'admin']