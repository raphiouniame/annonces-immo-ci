"""
Gestion des annonces immobilières : ajout et consultation.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import ListingForm
from models import PropertyListing, Media, db
import logging

# Création du blueprint
listings = Blueprint('listings', __name__)


@listings.route('/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    """
    Permet à un utilisateur connecté de publier une nouvelle annonce.
    Les médias sont uploadés via Cloudinary (widget), on reçoit les URLs.
    """
    form = ListingForm()
    if form.validate_on_submit():
        try:
            # Récupérer les URLs et public_id (si fournis par le widget)
            image_url = form.image_url.data.strip()
            image_public_id = request.form.get('image_public_id', '').strip() or 'unknown'
            video_url = form.video_url.data.strip()
            video_public_id = request.form.get('video_public_id', '').strip() or None

            if not image_url:
                flash("❌ Une image est requise pour publier une annonce.", "error")
                return render_template('listings/add_listing.html', form=form)

            # Créer l'annonce
            listing = PropertyListing(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                property_type=form.property_type.data,
                user_id=current_user.id
            )
            db.session.add(listing)
            db.session.flush()  # Pour obtenir l'ID

            # Ajouter l'image
            media_image = Media(
                public_id=image_public_id,
                url=image_url,
                file_type='image',
                listing_id=listing.id
            )
            db.session.add(media_image)

            # Ajouter la vidéo si présente
            if video_url:
                media_video = Media(
                    public_id=video_public_id or 'unknown_video',
                    url=video_url,
                    file_type='video',
                    listing_id=listing.id
                )
                db.session.add(media_video)

            # Enregistrer tout
            db.session.commit()
            flash("✅ Annonce publiée avec succès !", "success")
            logging.info(f"[Listings] {current_user.username} a publié l'annonce ID={listing.id} : {listing.title}")
            return redirect(url_for('main.index'))

        except Exception as e:
            db.session.rollback()
            flash("❌ Une erreur est survenue lors de la publication de l'annonce. Veuillez réessayer.", "error")
            logging.error(f"[Listings] Échec de publication par {current_user.username} : {e}")

    return render_template('listings/add_listing.html', form=form)


@listings.route('/listing/<int:id>')
def listing_detail(id):
    """
    Affiche le détail d'une annonce spécifique.
    """
    listing = PropertyListing.query.get_or_404(id)
    return render_template('listings/listing_detail.html', listing=listing)