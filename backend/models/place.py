"""
Place model — represents a tourist attraction, restaurant, or activity.

Schema:
    places (id, name, city_id, category, cost, popularity,
            description, rating, time_required, best_time)
"""

from extensions import db

class Place(db.Model):
    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    # Foreign key to cities table
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)

    # Category: historical | food | nature | shopping | hidden_gem
    category = db.Column(db.String(50), nullable=False)

    # Entry/visit cost in PKR (0 = free)
    cost = db.Column(db.Integer, nullable=False, default=0)

    # Popularity: "famous" | "hidden"
    popularity = db.Column(db.String(20), nullable=False, default="famous")

    # Descriptive text for display and LLM explanation context
    description = db.Column(db.Text, nullable=True)

    # Rating out of 5.0 (optional)
    rating = db.Column(db.Float, nullable=True)

    # Estimated hours needed to visit
    time_required = db.Column(db.Integer, nullable=False, default=2)

    # Best time of day to visit
    best_time = db.Column(db.String(50), nullable=True)
    image_url = db.Column(db.String(500),nullable=True)


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city_id": self.city_id,
            "city_name": self.city.name if self.city else None,
            "category": self.category,
            "cost": self.cost,
            "popularity": self.popularity,
            "description": self.description,
            "rating": self.rating,
            "time_required": self.time_required,
            "best_time": self.best_time,
            "image_url": self.image_url,
        }

    def __repr__(self):
        return f"<Place {self.name} ({self.city_id})>"
