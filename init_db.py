#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour le déploiement avec Supabase
"""

import os
import sys
import logging
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialise la base de données et crée l'admin"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier la connexion à Supabase
            logger.info("🔍 Vérification de la connexion à Supabase...")
            
            # Test de connexion plus robuste
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()
                logger.info(f"✅ Connexion Supabase OK - PostgreSQL {version[0] if version else 'version inconnue'}")
            
            # Créer toutes les tables
            logger.info("🔄 Création des tables...")
            db.create_all()
            logger.info("✅ Tables créées avec succès sur Supabase")
            
            # Vérifier que les tables existent
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"📋 Tables créées : {', '.join(tables)}")
            
            # Créer l'admin
            logger.info("👤 Création de l'utilisateur administrateur...")
            create_admin_user()
            
            logger.info("🎉 Initialisation de la base de données terminée avec succès !")
            
        except Exception as e:
            logger.error(f"❌ Erreur critique lors de l'initialisation : {e}")
            import traceback
            traceback.print_exc()
            
            # Informations de debug supplémentaires
            database_url = os.environ.get('DATABASE_URL', 'Non définie')
            if database_url != 'Non définie':
                # Masquer les credentials dans les logs
                safe_url = database_url.split('@')[-1] if '@' in database_url else 'URL malformée'
                logger.info(f"📍 Base de données cible : {safe_url}")
            
            sys.exit(1)

def create_admin_user():
    """Crée ou met à jour l'utilisateur administrateur"""
    try:
        ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin').strip()
        ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '+2250506531522').strip()
        ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'Admin2025!').strip()
        
        # Vérifications de sécurité
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            raise ValueError("ADMIN_USERNAME et ADMIN_PASSWORD sont obligatoires")
        
        # Interdire les mots de passe faibles en production
        weak_passwords = ['admin123', 'password', '123456', 'Admin2025!']
        if ADMIN_PASSWORD in weak_passwords and os.environ.get('FLASK_ENV') == 'production':
            raise ValueError(f"Mot de passe trop faible détecté en production: {ADMIN_PASSWORD}")
        
        # Vérifier si l'utilisateur existe
        existing = User.query.filter_by(username=ADMIN_USERNAME).first()
        
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                db.session.commit()
                logger.info(f"✅ Utilisateur '{ADMIN_USERNAME}' promu en administrateur")
            else:
                logger.info(f"ℹ️  Administrateur '{ADMIN_USERNAME}' existe déjà")
        else:
            # Créer le nouvel admin
            admin = User(
                username=ADMIN_USERNAME,
                phone=ADMIN_PHONE,
                password=generate_password_hash(ADMIN_PASSWORD),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info(f"✅ Administrateur '{ADMIN_USERNAME}' créé avec succès")
            
        # Vérifier que l'utilisateur a bien été créé/mis à jour
        final_admin = User.query.filter_by(username=ADMIN_USERNAME).first()
        if final_admin and final_admin.is_admin:
            logger.info(f"🔐 Admin vérifié : {ADMIN_USERNAME} (ID: {final_admin.id})")
        else:
            raise Exception("Échec de la vérification de l'admin après création")
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'admin : {e}")
        raise

def test_supabase_connection():
    """Test spécifique pour Supabase"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("❌ DATABASE_URL non définie")
            return False
        
        if not database_url.startswith('postgresql://'):
            logger.error(f"❌ URL de base de données invalide (doit commencer par postgresql://)")
            return False
        
        logger.info("✅ Configuration base de données valide")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur test connexion Supabase : {e}")
        return False

if __name__ == '__main__':
    # Test préliminaire
    if not test_supabase_connection():
        sys.exit(1)
    
    init_database()