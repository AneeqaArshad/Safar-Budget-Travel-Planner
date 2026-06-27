"""
Itinerary Route
───────────────
Provides read-only endpoints for browsing cities and places.
Useful for the optional dashboard / data explorer.
"""

from flask import Blueprint, jsonify, request
from models.city import City
from models.place import Place

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/cities", methods=["GET"])
def get_cities():
    """Return all available cities."""
    cities = City.query.all()
    return jsonify({"cities": [c.to_dict() for c in cities]})


@itinerary_bp.route("/places", methods=["GET"])
def get_places():
    """
    Return places, optionally filtered.
    Query params: city_id, category, max_cost
    """
    city_id = request.args.get("city_id", type=int)
    category = request.args.get("category")
    max_cost = request.args.get("max_cost", type=int)

    query = Place.query
    if city_id:
        query = query.filter_by(city_id=city_id)
    if category:
        query = query.filter_by(category=category)
    if max_cost is not None:
        query = query.filter(Place.cost <= max_cost)

    places = query.order_by(Place.rating.desc()).all()
    return jsonify({"places": [p.to_dict() for p in places]})


@itinerary_bp.route("/places/<int:place_id>", methods=["GET"])
def get_place(place_id):
    """Return a single place by ID."""
    place = Place.query.get_or_404(place_id)
    return jsonify(place.to_dict())
