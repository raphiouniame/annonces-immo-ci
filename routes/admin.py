"""
Routes réservées aux administrateurs.
Gère le dashboard, la suppression d'annonces et d'utilisateurs.
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import User, PropertyListing, db
import logging

# Création du blueprint
admin = Blueprint('admin', __name__)


def admin_required(f):
    """
    Décorateur personnalisé pour restreindre l'accès aux administrateurs.
    """
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("❌ Accès refusé : permissions administrateur requises.", "error")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/')
@login_required
@admin_required
def dashboard():
    """
    Page principale du tableau de bord administrateur.
    Affiche toutes les annonces et tous les utilisateurs.
    """
    users = User.query.all()
    listings = PropertyListing.query.order_by(PropertyListing.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=users, listings=listings)


@admin.route('/delete_listing/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_listing(id):
    """
    Supprime une annonce par son ID (via POST pour éviter CSRF).
    """
    listing = PropertyListing.query.get_or_404(id)
    title = listing.title

    try:
        db.session.delete(listing)
        db.session.commit()
        flash(f"🗑️ Annonce '{title}' supprimée avec succès.", "success")
        logging.info(f"[Admin] {current_user.username} a supprimé l'annonce ID={id} : {title}")
    except Exception as e:
        db.session.rollback()
        flash("❌ Une erreur est survenue lors de la suppression de l'annonce.", "error")
        logging.error(f"[Admin] Échec de suppression de l'annonce ID={id} : {e}")

    return redirect(url_for('admin.dashboard'))


@admin.route('/delete_user/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """
    Supprime un utilisateur et toutes ses annonces.
    Interdit de supprimer un autre admin ou soi-même.
    """
    user = User.query.get_or_404(id)

    if user.is_admin:
        flash("❌ Impossible de supprimer un administrateur.", "error")
        logging.warning(f"[Admin] {current_user.username} a tenté de supprimer l'admin ID={id}")
    elif user.id == current_user.id:
        flash("❌ Vous ne pouvez pas vous supprimer vous-même.", "error")
        logging.warning(f"[Admin] {current_user.username} a tenté de s'auto-supprimer")
    else:
        username = user.username
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f"✅ Utilisateur '{username}' et toutes ses annonces supprimés.", "success")
            logging.info(f"[Admin] {current_user.username} a supprimé l'utilisateur ID={id} : {username}")
        except Exception as e:
            db.session.rollback()
            flash("❌ Une erreur est survenue lors de la suppression de l'utilisateur.", "error")
            logging.error(f"[Admin] Échec de suppression de l'utilisateur ID={id} : {e}")

    return redirect(url_for('admin.dashboard'))