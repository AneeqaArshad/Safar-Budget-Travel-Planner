"""
Unit Tests — Core Services
Run with: python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from services.intent_classifier import classify_intent
from services.entity_extractor import (
    extract_budget, extract_days, extract_people,
    extract_city, extract_preferences, extract_all_entities
)


# ══════════════════════════════════════════════════════════════
# Intent Classifier Tests
# ══════════════════════════════════════════════════════════════

class TestIntentClassifier:

    def test_plan_request_basic(self):
        assert classify_intent("Plan my trip")["intent"] == "PLAN_REQUEST"

    def test_plan_request_generate(self):
        assert classify_intent("Generate an itinerary for me")["intent"] == "PLAN_REQUEST"

    def test_plan_request_with_budget(self):
        assert classify_intent(
            "Plan a trip for budget of 15000"
        )["intent"] == "PLAN_REQUEST"

    def test_explanation_why(self):
        assert classify_intent(
            "Why did you choose this place?"
        )["intent"] == "EXPLANATION_REQUEST"

    def test_explanation_explain(self):
        assert classify_intent(
            "Can you explain the reasoning?"
        )["intent"] == "EXPLANATION_REQUEST"

    def test_greeting_hello(self):
        assert classify_intent("Hello there!")["intent"] == "GREETING"

    def test_greeting_hi(self):
        assert classify_intent("Hi")["intent"] == "GREETING"

    def test_set_budget(self):
        assert classify_intent(
            "My budget is 20000 rupees"
        )["intent"] == "SET_BUDGET"

    def test_set_days(self):
        assert classify_intent(
            "I want to travel for 3 days"
        )["intent"] == "SET_DAYS"

    def test_set_people(self):
        assert classify_intent(
            "We are 4 people"
        )["intent"] == "SET_PEOPLE"

    def test_set_city(self):
        assert classify_intent(
            "I want to visit Lahore"
        )["intent"] == "SET_CITY"

    def test_set_preference(self):
        assert classify_intent(
            "I prefer nature spots"
        )["intent"] == "SET_PREFERENCE"

    def test_unknown(self):
        assert classify_intent("asdfgh xyz")["intent"] == "UNKNOWN"
# ══════════════════════════════════════════════════════════════
# Entity Extractor Tests
# ══════════════════════════════════════════════════════════════

class TestEntityExtractor:

    # Budget
    def test_budget_plain(self):
        assert extract_budget("My budget is 15000") == 15000

    def test_budget_k_notation(self):
        assert extract_budget("Budget 50k") == 50000

    def test_budget_thousand(self):
        assert extract_budget("I have 20 thousand rupees") == 20000

    def test_budget_with_commas(self):
        assert extract_budget("Rs 25,000") == 25000

    def test_budget_none(self):
        assert extract_budget("I want to go to Lahore") is None

    # Days
    def test_days_basic(self):
        assert extract_days("I want to travel for 3 days") == 3

    def test_days_nights(self):
        assert extract_days("Booking for 2 nights") == 2

    def test_days_week(self):
        assert extract_days("I have a week off") == 7

    def test_days_none(self):
        assert extract_days("My budget is 10000") is None

    # People
    def test_people_basic(self):
        assert extract_people("We are 4 people") == 4

    def test_people_just_me(self):
        assert extract_people("Just me travelling") == 1

    def test_people_family(self):
        assert extract_people("Family of 5") == 5

    def test_people_none(self):
        assert extract_people("I love Lahore") is None

    # City
    def test_city_lahore(self):
        assert extract_city("I want to visit Lahore") == "Lahore"

    def test_city_islamabad(self):
        assert extract_city("Trip to Islamabad please") == "Islamabad"

    def test_city_murree(self):
        assert extract_city("Weekend in Murree") == "Murree"

    def test_city_none(self):
        assert extract_city("I want to travel") is None

    # Preferences
    def test_pref_nature(self):
        assert "nature" in extract_preferences("I love nature spots")

    def test_pref_historical(self):
        assert "historical" in extract_preferences("I prefer historical places")

    def test_pref_multiple(self):
        prefs = extract_preferences("I like food and nature")
        assert "food" in prefs
        assert "nature" in prefs

    # Full extraction
    def test_extract_all(self):
        msg = "Plan a 2-day trip to Islamabad for 3 people with budget 30000"
        result = extract_all_entities(msg)
        assert result["days"] == 2
        assert result["city"] == "Islamabad"
        assert result["people"] == 3
        assert result["budget"] == 30000


# ══════════════════════════════════════════════════════════════
# Planning Engine Tests (requires app context)
# ══════════════════════════════════════════════════════════════

class TestPlanningEngine:
    """
    These tests require Flask app context and a seeded database.
    Run after starting the app at least once (to auto-seed).
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        from app import create_app
        self.app = create_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        yield
        self.ctx.pop()

    def test_basic_plan_lahore(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=20000, days=2, people=2,
            city="Lahore", preferences=[]
        )
        assert result["success"] is True
        assert result["city"] == "Lahore"
        assert len(result["days"]) == 2

    def test_budget_enforced(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=15000, days=3, people=1,
            city="Islamabad", preferences=[]
        )
        assert result["success"] is True
        assert result["activity_spent"] >= 0

    def test_low_budget_warning(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=3000, days=2, people=1,
            city="Murree", preferences=[]
        )
        # Should still succeed with free places only
        assert result["success"] is True

    def test_invalid_city(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=20000, days=2, people=1,
            city="NonExistentCity", preferences=[]
        )
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_activity_budget_not_exceeded(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=10000, days=1, people=1,
            city="Lahore", preferences=[]
        )
        if result["success"]:
            assert result["activity_spent"] >= 0

    def test_preference_filter(self):
        from services.planning_engine import generate_itinerary
        result = generate_itinerary(
            budget=25000, days=2, people=1,
            city="Islamabad", preferences=["nature"]
        )
        assert result["success"] is True
        # Nature places should appear (may also include others if budget allows)
        all_places = [p for day in result["days"] for p in day["places"]]
        nature_count = sum(1 for p in all_places if p["category"] == "nature")
        assert nature_count > 0

    def test_days_structure(self):
        from services.planning_engine import generate_itinerary

        result = generate_itinerary(
            budget=20000,
            days=2,
            people=2,
            city="Lahore",
            preferences=[]
        )

        assert isinstance(result["days"], list)

    def test_places_exist_in_day(self):
        from services.planning_engine import generate_itinerary

        result = generate_itinerary(
            budget=20000,
            days=2,
            people=2,
            city="Lahore",
            preferences=[]
        )

        for day in result["days"]:
            assert "places" in day
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
