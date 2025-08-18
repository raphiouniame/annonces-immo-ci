"""
Point d'entrée principal de l'application Flask.
Charge la configuration, initialise les extensions,
enregistre les blueprints et configure l'authentification.
"""

import os
import logging
from flask import Flask, render_template
from flask_login import LoginManager
from config import config  # On importe le mapping des configs
from dotenv import load_dotenv
load_dotenv()  # Charge les variables du .env



# Initialisation des extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'


def create_app():
    # Détermine l'environnement (default = development)
    config_name = os.environ.get('FLASK_ENV') or 'default'
    app_config = config[config_name]

    app = Flask(__name__)
    app.config.from_object(app_config)

    # === Configuration du logging ===
    if not app.debug and not app.testing:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)

    # === Initialisation des extensions ===
    from models import db, migrate  # migrate doit être ici pour éviter les imports circulaires
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)

    # === Gestion de l'utilisateur connecté ===
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"[User Loader] Échec du chargement de l'utilisateur {user_id}: {e}")
            return None

    # === Enregistrement des Blueprints ===
    from routes.main import main
    from routes.auth import auth
    from routes.listings import listings
    from routes.admin import admin

    app.register_blueprint(main)           # /
    app.register_blueprint(auth)           # /auth/*
    app.register_blueprint(listings)       # /listing/*
    app.register_blueprint(admin)          # /admin/*

    # === Initialisation de Cloudinary ===
    try:
        from cloudinary_util import init_cloudinary
        init_cloudinary()
    except Exception as e:
        app.logger.critical(f"[Cloudinary] Échec de l'initialisation : {e}")
        raise RuntimeError("Impossible de configurer Cloudinary. Vérifiez vos variables d'environnement.") from e

    # === Gestionnaires d'erreurs ===
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Erreur serveur: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    # === Création des tables (UNIQUEMENT en développement) ===
    with app.app_context():
        if app.config['DEBUG'] and config_name == 'development':
            db.create_all()
            app.logger.info("Tables créées (mode développement). Utilise Flask-Migrate en production.")

    return app


# === Instance principale ===
app = create_app()

# === Gestion du logger ===
if not app.debug:
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


# === Pour le lancement local uniquement ===
if __name__ == '__main__':
    # Render n'exécute pas ce bloc
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f"Démarrage de l'application sur le port {port} (debug={app.debug})")
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])