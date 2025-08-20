"""
Routes pour la gestion des annonces immobilières
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from models import db, PropertyListing, Media
from forms import ListingForm
from cloudinary_util import upload_file, detect_resource_type
import os

listings = Blueprint('listings', __name__)


@listings.route('/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    """Ajouter une nouvelle annonce"""
    form = ListingForm()
    
    if form.validate_on_submit():
        try:
            # Créer l'annonce
            listing = PropertyListing(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                property_type=form.property_type.data,
                user_id=current_user.id
            )
            db.session.add(listing)
            db.session.flush()  # Pour obtenir l'ID de l'annonce
            
            # Upload des fichiers
            uploaded_files = []
            
            # Traiter l'image principale
            if 'image_file' in request.files:
                image_file = request.files['image_file']
                if image_file and image_file.filename:
                    result = upload_file(image_file, 'image')
                    if result:
                        media = Media(
                            public_id=result['public_id'],
                            url=result['url'],
                            file_type='image',
                            listing_id=listing.id
                        )
                        db.session.add(media)
                        uploaded_files.append(result['public_id'])
            
            # Traiter la vidéo (optionnelle)
            if 'video_file' in request.files:
                video_file = request.files['video_file']
                if video_file and video_file.filename:
                    result = upload_file(video_file, 'video')
                    if result:
                        media = Media(
                            public_id=result['public_id'],
                            url=result['url'],
                            file_type='video',
                            listing_id=listing.id
                        )
                        db.session.add(media)
                        uploaded_files.append(result['public_id'])
            
            db.session.commit()
            
            flash(f'Annonce "{listing.title}" publiée avec succès !', 'success')
            return redirect(url_for('listings.listing_detail', id=listing.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur création annonce : {e}")
            flash('Erreur lors de la publication. Veuillez réessayer.', 'error')
    
    return render_template('listings/add_listing.html', form=form)


@listings.route('/<int:id>')
def listing_detail(id):
    """Afficher les détails d'une annonce"""
    listing = PropertyListing.query.get_or_404(id)
    return render_template('listings/listing_detail.html', listing=listing)


@listings.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    """Modifier une annonce (propriétaire seulement)"""
    listing = PropertyListing.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est le propriétaire ou admin
    if listing.user_id != current_user.id and not current_user.is_admin:
        flash('Vous ne pouvez pas modifier cette annonce.', 'error')
        return redirect(url_for('main.index'))
    
    form = ListingForm(obj=listing)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(listing)
            db.session.commit()
            flash('Annonce mise à jour avec succès !', 'success')
            return redirect(url_for('listings.listing_detail', id=listing.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur modification annonce : {e}")
            flash('Erreur lors de la modification.', 'error')
    
    return render_template('listings/edit_listing.html', form=form, listing=listing)


@listings.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    """Supprimer une annonce"""
    listing = PropertyListing.query.get_or_404(id)
    
    # Vérifier les permissions
    if listing.user_id != current_user.id and not current_user.is_admin:
        flash('Vous ne pouvez pas supprimer cette annonce.', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Supprimer les médias de Cloudinary
        for media in listing.media:
            from cloudinary_util import delete_file
            delete_file(media.public_id)
        
        # Supprimer de la base de données
        db.session.delete(listing)
        db.session.commit()
        
        flash('Annonce supprimée avec succès.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur suppression annonce : {e}")
        flash('Erreur lors de la suppression.', 'error')
    
    return redirect(url_for('main.index'))