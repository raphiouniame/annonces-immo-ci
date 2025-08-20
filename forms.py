"""
Formulaires WTF pour l'application
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, PasswordField, TextAreaField, IntegerField, 
    SelectField, SubmitField, BooleanField
)
from wtforms.validators import (
    DataRequired, Length, EqualTo, ValidationError, 
    Optional, Regexp, NumberRange
)
from models import User
import re


class RegisterForm(FlaskForm):
    """Formulaire d'inscription"""
    username = StringField(
        'Nom d\'utilisateur',
        validators=[
            DataRequired(message="Le nom d'utilisateur est obligatoire."),
            Length(min=3, max=50, message="Entre 3 et 50 caractères.")
        ],
        render_kw={"placeholder": "Votre nom d'utilisateur", "class": "form-control"}
    )
    
    phone = StringField(
        'Téléphone',
        validators=[
            DataRequired(message="Le numéro de téléphone est obligatoire."),
            Length(min=8, max=20, message="Numéro invalide."),
            Regexp(
                r'^\+?[0-9\s\-\(\)]{8,}$',
                message="Format invalide (ex: +225 XX XX XX XX XX)."
            )
        ],
        render_kw={"placeholder": "+225 XX XX XX XX XX", "class": "form-control"}
    )
    
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(message="Le mot de passe est obligatoire."),
            Length(min=6, message="Minimum 6 caractères.")
        ],
        render_kw={"placeholder": "Votre mot de passe", "class": "form-control"}
    )
    
    confirm = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            DataRequired(message="Confirmez votre mot de passe."),
            EqualTo('password', message="Les mots de passe ne correspondent pas.")
        ],
        render_kw={"placeholder": "Confirmez le mot de passe", "class": "form-control"}
    )
    
    submit = SubmitField('S\'inscrire', render_kw={"class": "btn btn-primary"})

    def validate_username(self, username):
        """Vérifie l'unicité du nom d'utilisateur"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur existe déjà.')


class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    username = StringField(
        'Nom d\'utilisateur',
        validators=[DataRequired(message="Ce champ est obligatoire.")],
        render_kw={"placeholder": "Votre nom d'utilisateur", "class": "form-control"}
    )
    
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired(message="Ce champ est obligatoire.")],
        render_kw={"placeholder": "Votre mot de passe", "class": "form-control"}
    )
    
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter', render_kw={"class": "btn btn-primary"})


class ListingForm(FlaskForm):
    """Formulaire pour publier/modifier une annonce"""
    title = StringField(
        'Titre de l\'annonce',
        validators=[
            DataRequired(message="Le titre est obligatoire."),
            Length(min=5, max=200, message="Entre 5 et 200 caractères.")
        ],
        render_kw={"placeholder": "Ex: Appartement 3 pièces à Abidjan", "class": "form-control"}
    )
    
    description = TextAreaField(
        'Description détaillée',
        validators=[
            DataRequired(message="La description est obligatoire."),
            Length(min=20, message="Description trop courte (minimum 20 caractères).")
        ],
        render_kw={"rows": 5, "placeholder": "Décrivez le bien, ses équipements, sa localisation...", "class": "form-control"}
    )
    
    price = IntegerField(
        'Prix (en FCFA)',
        validators=[
            DataRequired(message="Le prix est obligatoire."),
            NumberRange(min=1, message="Le prix doit être supérieur à 0.")
        ],
        render_kw={"placeholder": "Ex: 500000", "class": "form-control"}
    )
    
    property_type = SelectField(
        'Type d\'annonce',
        choices=[
            ('', 'Sélectionnez un type'),
            ('vente', 'Vente'),
            ('location', 'Location'),
            ('achat', 'Achat')
        ],
        validators=[DataRequired(message="Veuillez choisir un type d'annonce.")],
        render_kw={"class": "form-select"}
    )
    
    # Fichier image (obligatoire)
    image_file = FileField(
        'Image principale',
        validators=[
            FileRequired(message="Une image est obligatoire."),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                       message="Formats acceptés: JPG, PNG, GIF, WebP")
        ],
        render_kw={"class": "form-control", "accept": "image/*"}
    )
    
    # Fichier vidéo (optionnel)
    video_file = FileField(
        'Vidéo (optionnel)',
        validators=[
            Optional(),
            FileAllowed(['mp4', 'mov', 'avi', 'webm'], 
                       message="Formats acceptés: MP4, MOV, AVI, WebM")
        ],
        render_kw={"class": "form-control", "accept": "video/*"}
    )
    
    submit = SubmitField('Publier l\'annonce', render_kw={"class": "btn btn-primary"})


class EditListingForm(FlaskForm):
    """Formulaire pour modifier une annonce existante"""
    title = StringField(
        'Titre de l\'annonce',
        validators=[
            DataRequired(message="Le titre est obligatoire."),
            Length(min=5, max=200, message="Entre 5 et 200 caractères.")
        ],
        render_kw={"class": "form-control"}
    )
    
    description = TextAreaField(
        'Description détaillée',
        validators=[
            DataRequired(message="La description est obligatoire."),
            Length(min=20, message="Description trop courte.")
        ],
        render_kw={"rows": 5, "class": "form-control"}
    )
    
    price = IntegerField(
        'Prix (en FCFA)',
        validators=[
            DataRequired(message="Le prix est obligatoire."),
            NumberRange(min=1, message="Le prix doit être supérieur à 0.")
        ],
        render_kw={"class": "form-control"}
    )
    
    property_type = SelectField(
        'Type d\'annonce',
        choices=[
            ('vente', 'Vente'),
            ('location', 'Location'),
            ('achat', 'Achat')
        ],
        validators=[DataRequired(message="Veuillez choisir un type.")],
        render_kw={"class": "form-select"}
    )
    
    # Images optionnelles pour modification
    new_image = FileField(
        'Nouvelle image (optionnel)',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'])
        ],
        render_kw={"class": "form-control", "accept": "image/*"}
    )
    
    new_video = FileField(
        'Nouvelle vidéo (optionnel)',
        validators=[
            Optional(),
            FileAllowed(['mp4', 'mov', 'avi', 'webm'])
        ],
        render_kw={"class": "form-control", "accept": "video/*"}
    )
    
    submit = SubmitField('Mettre à jour', render_kw={"class": "btn btn-primary"})