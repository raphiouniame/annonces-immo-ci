"""
Modèles de base de données pour l'application immobilière
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime, timezone

# Instance de base de données
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Modèle utilisateur avec authentification"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Augmenté pour les hash bcrypt
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations
    listings = db.relationship('PropertyListing', backref='author', lazy=True, 
                             cascade="all, delete-orphan")

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username} ({'Admin' if self.is_admin else 'User'})>"


class PropertyListing(db.Model):
    """Modèle pour les annonces immobilières"""
    __tablename__ = 'property_listing'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Augmenté pour plus de flexibilité
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(20), nullable=False)  # vente/location/achat
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Clé étrangère
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Relations
    media = db.relationship('Media', backref='listing', lazy=True, 
                           cascade="all, delete-orphan")

    @property
    def main_image(self):
        """Retourne la première image de l'annonce"""
        for media_item in self.media:
            if media_item.file_type == 'image':
                return media_item
        return None

    @property
    def video(self):
        """Retourne la première vidéo de l'annonce"""
        for media_item in self.media:
            if media_item.file_type == 'video':
                return media_item
        return None

    def __repr__(self):
        return f"<PropertyListing '{self.title}' by {self.author.username}>"


class Media(db.Model):
    """Modèle pour les médias (images/vidéos) des annonces"""
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(200), nullable=False)  # ID Cloudinary
    url = db.Column(db.Text, nullable=False)  # URL complète
    file_type = db.Column(db.String(10), nullable=False)  # 'image' ou 'video'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Clé étrangère
    listing_id = db.Column(db.Integer, db.ForeignKey('property_listing.id'), 
                          nullable=False, index=True)

    def __repr__(self):
        return f"<Media {self.file_type}: {self.public_id}>"