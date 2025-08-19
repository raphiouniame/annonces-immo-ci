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
import cloudinary

# Charger les variables d'environnement seulement en développement
if os.environ.get('FLASK_ENV') != 'production':
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
    from models import db
    db.init_app(app)
    
    # Migrations seulement en développement
    if config_name == 'development':
        try:
            from models import migrate
            migrate.init_app(app, db)
        except ImportError:
            app.logger.warning("Flask-Migrate non disponible")

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

    # === Configuration de Cloudinary ===
    try:
        # Priorité à CLOUDINARY_URL si définie
        cloudinary_url = os.environ.get("CLOUDINARY_URL")
        if cloudinary_url:
            cloudinary.config(url=cloudinary_url)
            app.logger.info("✅ Cloudinary configuré avec succès via CLOUDINARY_URL.")
        else:
            # Sinon utiliser les variables individuelles
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
                app.logger.info("✅ Cloudinary configuré avec succès via variables individuelles.")
            else:
                app.logger.warning("⚠️ Cloudinary non configuré : variables manquantes.")
    except Exception as e:
        app.logger.critical(f"[Cloudinary] Échec de l'initialisation : {e}")
        # En production, Cloudinary doit être configuré
        if config_name == 'production':
            raise RuntimeError("Impossible de configurer Cloudinary. Vérifiez vos variables d'environnement.") from e

    # === Enregistrement des Blueprints ===
    from routes.main import main
    from routes.listings import listings

    app.register_blueprint(main)           # /
    app.register_blueprint(listings)       # /listing/*

    # Enregistrer auth et admin seulement s'ils existent
    try:
        from routes.auth import auth
        app.register_blueprint(auth)       # /auth/*
        app.logger.info("Blueprint 'auth' enregistré")
    except ImportError:
        app.logger.warning("Blueprint 'auth' non trouvé - création d'une route temporaire")
        
        # Route temporaire pour éviter les erreurs
        @app.route('/auth/login')
        def temp_login():
            return render_template_string("""
            <h1>Authentification temporaire</h1>
            <p>Le module d'authentification n'est pas encore disponible.</p>
            <a href="/">Retour à l'accueil</a>
            """)
        
        @app.route('/auth/logout')
        def temp_logout():
            return redirect(url_for('main.index'))

    try:
        from routes.admin import admin
        app.register_blueprint(admin)      # /admin/*
        app.logger.info("Blueprint 'admin' enregistré")
    except ImportError:
        app.logger.warning("Blueprint 'admin' non trouvé")

    # === Gestionnaires d'erreurs ===
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Vérifier que db.session existe avant de faire rollback
        if hasattr(db, 'session'):
            try:
                db.session.rollback()
            except:
                pass
        app.logger.error(f'Erreur serveur: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    # === Création des tables uniquement en développement ===
    # En production, les tables sont créées par init_db.py
    with app.app_context():
        if app.config['DEBUG'] and config_name == 'development':
            try:
                db.create_all()
                app.logger.info("Tables créées (mode développement)")
            except Exception as e:
                app.logger.error(f"Erreur création tables : {e}")

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