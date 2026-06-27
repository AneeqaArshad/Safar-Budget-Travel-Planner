"""
City model — represents a travel destination city.

Schema:
    cities (id, name)
"""

from extensions import db

class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # Relationship: one city has many places
    places = db.relationship("Place", backref="city", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

    def __repr__(self):
        return f"<City {self.name}>"
