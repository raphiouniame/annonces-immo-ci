#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour Render/Supabase
"""

import os
import sys
import logging
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_environment():
    """Vérifie que toutes les variables d'environnement nécessaires sont présentes"""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")
        return False
    
    # Vérification spécifique de l'URL de base de données
    database_url = os.environ.get('DATABASE_URL')
    if not database_url.startswith(('postgresql://', 'postgres://')):
        logger.error("DATABASE_URL doit être une URL PostgreSQL valide")
        return False
    
    logger.info("Toutes les variables d'environnement sont présentes")
    return True


def test_database_connection():
    """Test la connexion à la base de données"""
    try:
        app = create_app()
        with app.app_context():
            # Test de connexion simple
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()
                if version:
                    logger.info(f"Connexion PostgreSQL OK - Version: {version[0][:50]}...")
                    return True
                else:
                    logger.error("Impossible de récupérer la version PostgreSQL")
                    return False
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        return False


def create_tables():
    """Crée toutes les tables de la base de données"""
    try:
        app = create_app()
        with app.app_context():
            logger.info("Création des tables...")
            db.create_all()
            
            # Vérification que les tables ont été créées
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['user', 'property_listing', 'media']
            for table in expected_tables:
                if table not in tables:
                    raise Exception(f"Table '{table}' non créée")
            
            logger.info(f"Tables créées avec succès: {', '.join(tables)}")
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables: {e}")
        return False


def create_admin_user():
    """Crée l'utilisateur administrateur initial"""
    try:
        app = create_app()
        with app.app_context():
            # Récupération des variables d'environnement
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin').strip()
            admin_phone = os.environ.get('ADMIN_PHONE', '+2250506531522').strip()
            admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin2025!').strip()
            
            # Validation
            if not admin_username or not admin_password:
                raise ValueError("ADMIN_USERNAME et ADMIN_PASSWORD sont obligatoires")
            
            # Vérifier si l'admin existe déjà
            existing = User.query.filter_by(username=admin_username).first()
            
            if existing:
                if not existing.is_admin:
                    existing.is_admin = True
                    db.session.commit()
                    logger.info(f"Utilisateur '{admin_username}' promu administrateur")
                else:
                    logger.info(f"Administrateur '{admin_username}' existe déjà")
            else:
                # Créer le nouvel administrateur
                admin = User(
                    username=admin_username,
                    phone=admin_phone,
                    password=generate_password_hash(admin_password),
                    is_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                logger.info(f"Administrateur '{admin_username}' créé avec succès")
            
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'administrateur: {e}")
        return False


def main():
    """Fonction principale d'initialisation"""
    logger.info("=== INITIALISATION DE LA BASE DE DONNÉES ===")
    
    # 1. Vérification de l'environnement
    if not verify_environment():
        logger.error("Échec de la vérification de l'environnement")
        sys.exit(1)
    
    # 2. Test de connexion
    if not test_database_connection():
        logger.error("Échec de la connexion à la base de données")
        sys.exit(1)
    
    # 3. Création des tables
    if not create_tables():
        logger.error("Échec de la création des tables")
        sys.exit(1)
    
    # 4. Création de l'administrateur
    if not create_admin_user():
        logger.error("Échec de la création de l'administrateur")
        sys.exit(1)
    
    logger.info("=== INITIALISATION TERMINÉE AVEC SUCCÈS ===")


if __name__ == '__main__':
    main()