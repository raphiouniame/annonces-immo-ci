from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, User, PropertyListing, Media
from cloudinary_util import delete_file
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Accès réservé aux administrateurs.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    listings = PropertyListing.query.order_by(PropertyListing.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=users, listings=listings)

@admin.route('/delete-listing/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_listing(id):
    listing = PropertyListing.query.get_or_404(id)
    
    # Supprimer les médias de Cloudinary
    for media in listing.media:
        delete_file(media.public_id)
    
    db.session.delete(listing)
    db.session.commit()
    flash('Annonce supprimée avec succès.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/delete-user/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    user = User.query.get_or_404(id)
    
    # Supprimer les médias Cloudinary de toutes les annonces de l'utilisateur
    for listing in user.listings:
        for media in listing.media:
            delete_file(media.public_id)
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Utilisateur {user.username} supprimé avec succès.', 'success')
    return redirect(url_for('admin.dashboard'))