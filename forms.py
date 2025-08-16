"""
Définition des formulaires web utilisés dans l'application.
Basés sur WTForms avec validation côté serveur.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    TextAreaField,
    IntegerField,
    SelectField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    ValidationError,
    Optional,
    Regexp,
)
from models import User
import re


class RegisterForm(FlaskForm):
    """
    Formulaire d'inscription pour un nouvel utilisateur.
    """
    username = StringField(
        'Nom d’utilisateur',
        validators=[
            DataRequired(message="Le nom d’utilisateur est obligatoire."),
            Length(min=3, max=50, message="Le nom doit faire entre 3 et 50 caractères.")
        ],
        render_kw={"placeholder": "Choisissez un nom d'utilisateur"}
    )
    phone = StringField(
        'Téléphone',
        validators=[
            DataRequired(message="Le numéro de téléphone est obligatoire."),
            Length(min=8, message="Le numéro semble trop court."),
            Regexp(
                r'^\+?[0-9\s\-\(\)]{8,}$',
                message="Veuillez entrer un numéro de téléphone valide (ex: +221 77 123 45 67)."
            )
        ],
        render_kw={"placeholder": "Ex: +221 77 123 45 67"}
    )
    password = PasswordField(
        'Mot de passe',
        validators=[
            DataRequired(message="Le mot de passe est obligatoire."),
            Length(min=6, message="Le mot de passe doit faire au moins 6 caractères.")
        ],
        render_kw={"placeholder": "Votre mot de passe"}
    )
    confirm = PasswordField(
        'Confirmer le mot de passe',
        validators=[
            DataRequired(message="Veuillez confirmer le mot de passe."),
            EqualTo('password', message="Les mots de passe doivent correspondre.")
        ],
        render_kw={"placeholder": "Confirmez le mot de passe"}
    )
    submit = SubmitField('S’inscrire')

    def validate_username(self, username):
        """
        Vérifie que le nom d’utilisateur n’est pas déjà pris.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d’utilisateur est déjà utilisé. Veuillez en choisir un autre.')


class LoginForm(FlaskForm):
    """
    Formulaire de connexion.
    """
    username = StringField(
        'Nom d’utilisateur',
        validators=[DataRequired(message="Ce champ est obligatoire.")],
        render_kw={"placeholder": "Votre nom d'utilisateur"}
    )
    password = PasswordField(
        'Mot de passe',
        validators=[DataRequired(message="Ce champ est obligatoire.")],
        render_kw={"placeholder": "Votre mot de passe"}
    )
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

    def validate(self, extra_validators=None):
        """
        Validation personnalisée : vérifie que l'utilisateur existe et que le mot de passe est correct.
        """
        if not super().validate():
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append("Nom d’utilisateur inconnu.")
            return False

        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password, self.password.data):
            self.password.errors.append("Mot de passe incorrect.")
            return False

        # Optionnel : stocker l'utilisateur pour un accès facile après validation
        self.user = user
        return True


class ListingForm(FlaskForm):
    """
    Formulaire pour publier une annonce immobilière.
    Les médias sont uploadés via Cloudinary (widget ou API), donc on attend les URLs.
    """
    title = StringField(
        'Titre de l’annonce',
        validators=[DataRequired(message="Le titre est obligatoire.")],
        render_kw={"placeholder": "Ex: Appartement 3 pièces à Dakar"}
    )
    description = TextAreaField(
        'Description détaillée',
        validators=[DataRequired(message="La description est obligatoire.")],
        render_kw={"rows": 5, "placeholder": "Décrivez le bien, ses équipements, sa localisation..."}
    )
    price = IntegerField(
        'Prix (en FCFA, €, $, etc.)',
        validators=[DataRequired(message="Le prix est obligatoire.")],
        render_kw={"placeholder": "Ex: 500000"}
    )
    property_type = SelectField(
        'Type d’annonce',
        choices=[
            ('', 'Sélectionnez un type'),
            ('vente', 'Vente'),
            ('location', 'Location'),
            ('achat', 'Achat')
        ],
        validators=[DataRequired(message="Veuillez choisir un type d’annonce.")],
        coerce=str
    )
    image_url = StringField(
        'URL de l’image (uploadée via Cloudinary)',
        validators=[DataRequired(message="Veuillez uploader une image.")],
        render_kw={"placeholder": "L’image sera ajoutée via le widget ci-dessous"}
    )
    video_url = StringField(
        'URL de la vidéo (optionnel)',
        validators=[Optional()],
        render_kw={"placeholder": "Optionnel : URL de la vidéo sur Cloudinary"}
    )
    submit = SubmitField('Publier l’annonce')

    def validate_image_url(self, image_url):
        """
        Valide que l'URL est bien une URL HTTPS valide et qu'elle provient de Cloudinary.
        """
        if not image_url.data:
            return  # Déjà géré par DataRequired

        # Vérifie que c'est une URL HTTP(S) valide
        if not re.match(r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.-])*(?:\?(?:[\w&=%.-])*)?(?:\#(?:[\w.-])*)?)?$', image_url.data):
            raise ValidationError("Veuillez fournir une URL web valide (ex: https://exemple.com).")

        # Force l'utilisation de Cloudinary (sécurité et cohérence)
        if 'cloudinary.com' not in image_url.data:
            raise ValidationError("L'image doit être hébergée sur Cloudinary.")