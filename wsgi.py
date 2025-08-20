# wsgi.py
"""
Point d'entrée WSGI pour le déploiement en production.
Utilisé par Gunicorn sur Render.
"""

from app import app

if __name__ == "__main__":
    # Ce bloc s'exécute uniquement en local (pas sur Render)
    app.run()