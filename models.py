"""
Définition des modèles de base de données pour l'application immobilière.
Utilise SQLAlchemy pour ORM.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from flask_migrate import Migrate  # Ajouté ici pour éviter les imports circulaires

# Instance de base de données (initialisée dans app.py)
db = SQLAlchemy()
migrate = Migrate()  # Initialisé ici, attaché dans app.py via migrate.init_app(app, db)


class User(UserMixin, db.Model):
    """
    Modèle représentant un utilisateur (ou administrateur).
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relation avec les annonces publiées par cet utilisateur
    listings = db.relationship('PropertyListing', backref='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({'Admin' if self.is_admin else 'Utilisateur'})>"


class PropertyListing(db.Model):
    """
    Modèle pour une annonce immobilière (vente, location, achat).
    """
    __tablename__ = 'property_listing'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(20), nullable=False)  # vente / location / achat
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Relation avec les médias (images/vidéos)
    media = db.relationship('Media', backref='listing', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Annonce '{self.title}' publiée par {self.author.username}>"


class Media(db.Model):
    """
    Modèle pour stocker les médias (images ou vidéos) associés à une annonce.
    Utilise Cloudinary : on stocke l'URL et le public_id.
    """
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)  # db.Text pour les longues URLs Cloudinary
    file_type = db.Column(db.String(10), nullable=False)  # 'image' ou 'video'
    listing_id = db.Column(db.Integer, db.ForeignKey('property_listing.id'), nullable=False, index=True)

    def __repr__(self):
        return f"<Media {self.file_type}: {self.url}>"