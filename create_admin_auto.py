# create_admin_auto.py
"""
Script automatisé pour créer ou promouvoir un utilisateur administrateur.
Utilise des variables d'environnement pour les identifiants.
"""

import os
import sys
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect


def create_admin():
    """Crée ou promeut un utilisateur en administrateur"""
    app = create_app()

    with app.app_context():
        try:
            # Vérifier que la table 'user' existe
            inspector = inspect(db.engine)
            if not inspector.has_table('user'):
                print("❌ ERREUR : La table 'user' n'existe pas. Appliquez les migrations (alembic upgrade head).")
                sys.exit(1)

            # Récupérer et nettoyer les variables d'environnement
            ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin').strip()
            ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '+221123456789').strip()
            ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123').strip()

            # === Vérifications de sécurité ===
            if not ADMIN_USERNAME:
                print("❌ ERREUR: ADMIN_USERNAME ne peut pas être vide.")
                sys.exit(1)

            if not ADMIN_PASSWORD:
                print("❌ ERREUR: ADMIN_PASSWORD ne peut pas être vide.")
                sys.exit(1)

            # Interdire le mot de passe par défaut en production
            if ADMIN_PASSWORD == 'admin123' and os.environ.get('FLASK_ENV') == 'production':
                print("❌ ERREUR: Mot de passe par défaut détecté en production!")
                print("   Définissez ADMIN_PASSWORD dans les variables d'environnement.")
                sys.exit(1)

            # Vérifier si l'utilisateur existe déjà
            existing = User.query.filter_by(username=ADMIN_USERNAME).first()

            if existing:
                if existing.is_admin:
                    print(f"ℹ️  L'administrateur '{ADMIN_USERNAME}' existe déjà.")
                else:
                    # Promouvoir l'utilisateur en admin
                    existing.is_admin = True
                    db.session.commit()
                    print(f"⬆️  Utilisateur '{ADMIN_USERNAME}' promu en administrateur !")
            else:
                # Créer un nouvel admin
                new_admin = User(
                    username=ADMIN_USERNAME,
                    phone=ADMIN_PHONE,
                    password=generate_password_hash(ADMIN_PASSWORD),
                    is_admin=True
                )
                db.session.add(new_admin)
                db.session.commit()
                print(f"✅ Administrateur '{ADMIN_USERNAME}' créé avec succès !")

            # Informations de connexion (sans mot de passe)
            print(f"🔑 Nom d'utilisateur: {ADMIN_USERNAME}")
            print("🔑 Mot de passe: (défini via ADMIN_PASSWORD - non affiché pour des raisons de sécurité)")

        except Exception as e:
            print(f"❌ Erreur lors de la création ou de la promotion de l'admin : {e}")
            sys.exit(1)


if __name__ == '__main__':
    create_admin()