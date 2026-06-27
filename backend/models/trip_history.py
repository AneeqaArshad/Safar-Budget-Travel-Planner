from extensions import db

class TripHistory(db.Model):

    __tablename__ = "trip_history"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    city = db.Column(db.String(100))

    budget = db.Column(db.Integer)

    days = db.Column(db.Integer)

    people = db.Column(db.Integer)

    itinerary_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )