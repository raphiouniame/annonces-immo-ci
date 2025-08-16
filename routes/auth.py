"""
Gestion des routes d'authentification : inscription, connexion, déconnexion.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from forms import RegisterForm, LoginForm
from models import User, db

# Création du blueprint
auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Page d'inscription d'un nouvel utilisateur.
    """
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Créer un nouvel utilisateur
        user = User(
            username=form.username.data,
            phone=form.phone.data,
            password=generate_password_hash(form.password.data),
            is_admin=False  # Par défaut, pas admin
        )
        db.session.add(user)
        db.session.commit()

        flash("✅ Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Page de connexion.
    """
    if current_user.is_authenticated:
        flash("Vous êtes déjà connecté.", "info")
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Le formulaire gère déjà la validation (y compris mot de passe)
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)

        flash(f"👋 Bienvenue, {user.username} !", "success")
        return redirect(url_for('main.index'))

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
def logout():
    """
    Déconnexion de l'utilisateur.
    """
    username = current_user.username
    logout_user()
    flash(f"👋 À bientôt, {username} ! Vous êtes déconnecté.", "info")
    return redirect(url_for('main.index'))