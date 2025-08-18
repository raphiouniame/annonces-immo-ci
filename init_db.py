#!/usr/bin/env python3
"""
Script d'initialisation de la base de données pour le déploiement
Combine les migrations et la création de l'admin
"""

import os
import sys
import logging
from flask import Flask
from flask_migrate import upgrade, init as migrate_init
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialise la base de données et crée l'admin"""
    app = create_app()
    
    with app.app_context():
        try:
            # Vérifier la connexion à la base de données
            logger.info("🔍 Vérification de la connexion à la base de données...")
            db.engine.execute("SELECT 1")
            logger.info("✅ Connexion à la base de données OK")
            
            # Appliquer les migrations
            logger.info("🔄 Application des migrations...")
            try:
                upgrade()
                logger.info("✅ Migrations appliquées avec succès")
            except Exception as e:
                logger.warning(f"⚠️  Erreur lors des migrations (peut être normal) : {e}")
                # En cas d'échec, créer les tables directement
                logger.info("🔄 Création directe des tables...")
                db.create_all()
                logger.info("✅ Tables créées directement")
            
            # Créer l'admin
            logger.info("👤 Création de l'utilisateur administrateur...")
            create_admin_user()
            
            logger.info("🎉 Initialisation de la base de données terminée avec succès !")
            
        except Exception as e:
            logger.error(f"❌ Erreur critique lors de l'initialisation : {e}")
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
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création de l'admin : {e}")
        raise

if __name__ == '__main__':
    init_database()