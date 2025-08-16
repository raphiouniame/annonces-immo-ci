"""
Route principale : page d'accueil affichant toutes les annonces.
"""

from flask import Blueprint, render_template, request
from models import PropertyListing

# Création du blueprint
main = Blueprint('main', __name__)


@main.route('/')
def index():
    """
    Page d'accueil : affiche les annonces triées par date (récentes en premier)
    Optionnel : pagination
    """
    # Optionnel : filtre par type
    property_type = request.args.get('type', '')
    if property_type in ['vente', 'location', 'achat']:
        listings_query = PropertyListing.query.filter_by(property_type=property_type)
    else:
        listings_query = PropertyListing.query

    # Tri et pagination (décommente si besoin)
    page = request.args.get('page', 1, type=int)
    listings = listings_query.order_by(PropertyListing.created_at.desc()).all()
    # .paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'index.html',
        listings=listings,
        current_type=property_type
        # pagination=listings  # si tu utilises paginate()
    )