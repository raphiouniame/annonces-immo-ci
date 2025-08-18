from flask import Blueprint, render_template, request
from models import PropertyListing

main = Blueprint('main', __name__)

@main.route('/')
def index():
    type_filter = request.args.get('type', '')
    
    if type_filter:
        listings = PropertyListing.query.filter_by(property_type=type_filter).order_by(PropertyListing.created_at.desc()).all()
    else:
        listings = PropertyListing.query.order_by(PropertyListing.created_at.desc()).all()
    
    return render_template('index.html', listings=listings, current_type=type_filter)