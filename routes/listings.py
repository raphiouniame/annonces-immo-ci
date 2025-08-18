# routes/listings.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, PropertyListing, Media
from forms import ListingForm
from cloudinary_util import upload_file, detect_resource_type

listings = Blueprint('listings', __name__, url_prefix='/listing')

@listings.route('/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    form = ListingForm()
    if form.validate_on_submit():
        # Créer l'annonce
        listing = PropertyListing(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            property_type=form.property_type.data,
            user_id=current_user.id
        )
        db.session.add(listing)
        db.session.flush()  # Pour obtenir l'id avant commit

        # Gestion de l'image
        image = request.files.get('image')
        if image and image.filename != '':
            # Détecte automatiquement que c'est une image
            result = upload_file(image, resource_type='image')
            if result:
                media_img = Media(
                    public_id=result['public_id'],
                    url=result['url'],
                    file_type='image',
                    listing_id=listing.id
                )
                db.session.add(media_img)
            else:
                flash("Échec de l'upload de l'image.", "error")

        # Gestion de la vidéo
        video = request.files.get('video')
        if video and video.filename != '':
            # Détecte automatiquement que c'est une vidéo
            result = upload_file(video, resource_type='video')
            if result:
                media_vid = Media(
                    public_id=result['public_id'],
                    url=result['url'],
                    file_type='video',
                    listing_id=listing.id
                )
                db.session.add(media_vid)
            else:
                flash("Échec de l'upload de la vidéo.", "error")

        # Sauvegarde finale
        try:
            db.session.commit()
            flash('✅ Annonce publiée avec succès !', 'success')
            return redirect(url_for('listings.listing_detail', id=listing.id))
        except Exception as e:
            db.session.rollback()
            flash('❌ Erreur lors de la sauvegarde de l\'annonce.', 'error')
            print(f"[DB Error] {e}")

    return render_template('listings/add_listing.html', form=form)

@listings.route('/<int:id>')
def listing_detail(id):
    listing = PropertyListing.query.get_or_404(id)
    return render_template('listings/listing_detail.html', listing=listing)