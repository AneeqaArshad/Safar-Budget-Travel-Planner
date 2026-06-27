"""
Database Utility Script
───────────────────────
Standalone script for database management tasks.

Usage:
    python db_utils.py seed        # Seed from sample_data.json
    python db_utils.py export      # Export all data to JSON
    python db_utils.py reset       # Drop and recreate all tables
    python db_utils.py schema      # Print table schemas
"""

import sys
import json
import os

# Add backend to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models.city import City
from models.place import Place


def seed_from_json(filepath="sample_data.json"):
    """Import cities and places from a JSON file."""
    app = create_app()
    with app.app_context():
        with open(filepath, "r") as f:
            data = json.load(f)

        # Clear existing data
        Place.query.delete()
        City.query.delete()
        db.session.commit()

        # Insert cities
        for c in data["cities"]:
            db.session.add(City(id=c["id"], name=c["name"]))
        db.session.commit()

        # Insert places
        for p in data["places"]:
            db.session.add(Place(**p))
        db.session.commit()

        print(f"✅ Seeded {len(data['cities'])} cities and {len(data['places'])} places.")


def export_to_json(filepath="export.json"):
    """Export all data to a JSON file."""
    app = create_app()
    with app.app_context():
        cities = [c.to_dict() for c in City.query.all()]
        places = [p.to_dict() for p in Place.query.all()]
        data = {"cities": cities, "places": places}
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Exported {len(cities)} cities and {len(places)} places to {filepath}")


def reset_database():
    """Drop all tables and recreate them (data will be lost)."""
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset. All tables recreated.")


def print_schema():
    """Print the expected table structure."""
    schema = """
    ┌─────────────────────────────────────────────────────┐
    │  TABLE: cities                                      │
    ├────────────┬─────────┬─────────────────────────────┤
    │ Column     │ Type    │ Notes                       │
    ├────────────┼─────────┼─────────────────────────────┤
    │ id         │ INTEGER │ Primary key, auto-increment │
    │ name       │ STRING  │ City name, unique           │
    └────────────┴─────────┴─────────────────────────────┘

    ┌─────────────────────────────────────────────────────┐
    │  TABLE: places                                      │
    ├───────────────┬─────────┬───────────────────────── │
    │ Column        │ Type    │ Notes                     │
    ├───────────────┼─────────┼───────────────────────── │
    │ id            │ INTEGER │ Primary key               │
    │ name          │ STRING  │ Place name                │
    │ city_id       │ INTEGER │ FK → cities.id            │
    │ category      │ STRING  │ historical/food/nature/   │
    │               │         │ shopping/hidden_gem       │
    │ cost          │ INTEGER │ Entry cost in PKR (0=free)│
    │ popularity    │ STRING  │ famous / hidden           │
    │ description   │ TEXT    │ Short description         │
    │ rating        │ FLOAT   │ 0.0 – 5.0 (nullable)     │
    │ time_required │ INTEGER │ Hours needed              │
    │ best_time     │ STRING  │ Morning/Afternoon/Evening │
    └───────────────┴─────────┴───────────────────────── ┘
    """
    print(schema)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "seed":
        seed_from_json()
    elif cmd == "export":
        export_to_json()
    elif cmd == "reset":
        reset_database()
    elif cmd == "schema":
        print_schema()
    else:
        print(__doc__)
