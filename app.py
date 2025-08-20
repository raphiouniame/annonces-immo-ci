"""
Application Flask pour annonces immobilières
Optimisée pour le déploiement sur Render avec Supabase et Cloudinary
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from config import config
import cloudinary

# Initialisation des extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'


def create_app():
    """Factory pour créer l'application Flask"""
    # Déterminer l'environnement
    config_name = os.environ.get('FLASK_ENV', 'production')
    if config_name not in ['development', 'production', 'testing']:
        config_name = 'production'
    
    app_config = config[config_name]
    
    app = Flask(__name__)
    app.config.from_object(app_config)

    # Configuration du logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
        app.logger.setLevel(logging.INFO)

    # Initialisation de la base de données
    from models import db
    db.init_app(app)

    # === 🔧 FLASK-MIGRATE : ACTIVÉ DANS TOUS LES ENVIRONNEMENTS ===
    try:
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
        app.logger.info("✅ Flask-Migrate activé - 'flask db' est disponible")
    except ImportError:
        app.logger.critical("❌ Flask-Migrate non installé. Installez-le avec 'pip install Flask-Migrate'")
        if config_name == 'production':
            raise  # Interrompt le démarrage en production si Migrate est manquant

    # Initialisation de Flask-Login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Erreur chargement utilisateur {user_id}: {e}")
            return None

    # Configuration Cloudinary
    configure_cloudinary(app)

    # Enregistrement des blueprints
    register_blueprints(app)

    # Gestionnaires d'erreurs
    register_error_handlers(app)

    # === 🚫 CRÉATION DES TABLES UNIQUEMENT EN DÉVELOPPEMENT ===
    # En production, on utilise 'flask db upgrade', jamais 'db.create_all()'
    if config_name == 'development':
        with app.app_context():
            try:
                db.create_all()
                app.logger.info("🔧 Tables créées (mode développement)")
            except Exception as e:
                app.logger.error(f"❌ Erreur création tables : {e}")

    return app


def configure_cloudinary(app):
    """Configure Cloudinary à partir des variables d'environnement"""
    try:
        cloudinary_url = os.environ.get("CLOUDINARY_URL")
        if cloudinary_url:
            # Configuration via URL complète
            cloudinary.config(url=cloudinary_url)
            app.logger.info("☁️ Cloudinary configuré via CLOUDINARY_URL")
        else:
            # Configuration via variables séparées
            cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
            api_key = os.environ.get('CLOUDINARY_API_KEY')
            api_secret = os.environ.get('CLOUDINARY_API_SECRET')
            
            if all([cloud_name, api_key, api_secret]):
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    secure=True
                )
                app.logger.info("☁️ Cloudinary configuré via variables séparées")
            else:
                app.logger.warning("⚠️ Configuration Cloudinary incomplète (variables manquantes)")
                
    except Exception as e:
        app.logger.error(f"❌ Erreur configuration Cloudinary : {e}")
        if os.environ.get('FLASK_ENV') == 'production':
            app.logger.critical("💥 Cloudinary requis en production – vérifiez les variables d’environnement")


def register_blueprints(app):
    """Enregistre tous les blueprints"""
    # Blueprint principal
    from routes.main import main
    app.register_blueprint(main)
    
    # Blueprint listings
    from routes.listings import listings
    app.register_blueprint(listings, url_prefix='/listing')
    
    # Blueprint authentification
    from routes.auth import auth
    app.register_blueprint(auth, url_prefix='/auth')
    
    # Blueprint admin
    from routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')


def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs"""
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from models import db
        try:
            db.session.rollback()
        except Exception:
            pass
        app.logger.error(f'❌ Erreur serveur: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403


# Instance de l'application
app = create_app()


# Démarrage local uniquement
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])