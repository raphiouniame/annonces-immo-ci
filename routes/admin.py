"""
Routes d'administration - Réservées aux administrateurs
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import db, User, PropertyListing

admin = Blueprint('admin', __name__)


def admin_required(f):
    """Décorateur pour restreindre l'accès aux administrateurs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès refusé : vous devez être administrateur.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Tableau de bord administrateur"""
    # Statistiques générales
    total_users = User.query.count()
    total_listings = PropertyListing.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    
    # Dernières annonces
    recent_listings = PropertyListing.query.order_by(
        PropertyListing.created_at.desc()
    ).limit(5).all()
    
    # Derniers utilisateurs
    recent_users = User.query.order_by(
        User.id.desc()
    ).limit(5).all()
    
    stats = {
        'total_users': total_users,
        'total_listings': total_listings,
        'total_admins': total_admins,
        'recent_listings': recent_listings,
        'recent_users': recent_users
    }
    
    return render_template('admin/dashboard.html', **stats)


@admin.route('/users')
@login_required
@admin_required
def users():
    """Gestion des utilisateurs"""
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    return render_template('admin/users.html', users=users)


@admin.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Basculer le statut administrateur d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    # Empêcher de se retirer ses propres droits admin
    if user.id == current_user.id:
        flash('Vous ne pouvez pas modifier votre propre statut administrateur.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    action = 'promu administrateur' if user.is_admin else 'retiré des administrateurs'
    
    try:
        db.session.commit()
        flash(f'Utilisateur {user.username} {action}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la modification du statut.', 'error')
    
    return redirect(url_for('admin.users'))


@admin.route('/listings')
@login_required
@admin_required
def listings():
    """Gestion des annonces"""
    page = request.args.get('page', 1, type=int)
    listings = PropertyListing.query.order_by(
        PropertyListing.created_at.desc()
    ).paginate(
        page=page,
        per_page=20,
        error_out=False
    )
    return render_template('admin/listings.html', listings=listings)


@admin.route('/listings/<int:listing_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_listing(listing_id):
    """Supprimer une annonce (admin)"""
    listing = PropertyListing.query.get_or_404(listing_id)
    
    try:
        # Supprimer les médias de Cloudinary
        for media in listing.media:
            from cloudinary_util import delete_file
            delete_file(media.public_id)
        
        # Supprimer de la base de données
        title = listing.title
        db.session.delete(listing)
        db.session.commit()
        
        flash(f'Annonce "{title}" supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erreur lors de la suppression.', 'error')
    
    return redirect(url_for('admin.listings'))