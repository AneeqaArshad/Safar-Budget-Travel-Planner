"""
Planning Engine v3 — Optimized + Knapsack-Based
"""

import math
from services.place_retriever import search_places
from models.place import Place
from models.city import City
from config import Config
from utils.logger import logger

# ── VALUE FUNCTION ─────────────────────────────────────
def _value_score(place, preferences):
    rating = place.rating or 3.5
    cost_denom = math.log(place.cost + 1) + 1
    pref_bonus = 1.4 if (preferences and place.category in preferences) else 1.0
    hidden_bonus = 1.25 if place.popularity == "hidden" else 1.0
    return (rating / cost_denom) * pref_bonus * hidden_bonus
            
# ── RETRIEVAL FUNCTION ──────────────────────────

def _retrieval_score(place, preferences):

    score = 0
    # rating contribution
    score += (place.rating or 3.5) * 2
    if place.popularity == "famous":
        score += 3

    # preference match
    if preferences:

        if place.category in preferences:
            score += 5

    # hidden gems bonus
    if place.popularity == "hidden":
        score += 2

    # cheaper places slight bonus
    if place.cost < 500:
        score += 1

    return score
    
# ── KNAPSACK (CORE OPTIMIZER) ──────────────────────────
def knapsack_select(places, budget, preferences):
    n = len(places)
    budget = int(max(0, budget))

    dp = [[0]*(budget+1) for _ in range(n+1)]

    for i in range(1, n+1):
        cost = int(places[i-1].cost)
        value = int(_value_score(places[i-1], preferences) * 100)

        for w in range(budget+1):
            if cost <= w:
                dp[i][w] = max(
                    value + dp[i-1][w-cost],
                    dp[i-1][w]
                )
            else:
                dp[i][w] = dp[i-1][w]

    res = []
    w = budget
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            res.append(places[i-1])
            w -= int(places[i-1].cost)

    return res


# ── MAIN ENGINE ────────────────────────────────────────
def generate_itinerary(budget, days, people, city, preferences=None):
    preferences = preferences or []
    PREFERENCE_MAP = {
        "exploring": ["historical", "natural", "adventure"],
        "nature": ["natural"],
        "adventure": ["adventure"],
        "food": ["food"],
        "shopping": ["shopping"],
        "history": ["historical"],
        "relax": ["natural"],
        "luxury": ["shopping", "food"],
    }

    expanded_preferences = []

    for pref in preferences:
        pref = pref.lower()

        expanded_preferences.append(pref)

        for key, cats in PREFERENCE_MAP.items():
            if key in pref:
                expanded_preferences.extend(cats)

    preferences = list(set(expanded_preferences))
    if budget <= 0:
        return {
            "success": False,
            "error": "Budget must be greater than zero."
            }
    if days <= 0:
        return {
            "success": False,
            "error": "Days must be at least 1."
            }

    if people <= 0:
        return {
            "success": False,
            "error": "People count must be at least 1."
            }
    minimum_required = days * people * 1500

    if budget < minimum_required:
        return {
            "success": False,
            "error": (
                f"Budget is too low for a {days}-day trip for {people} people. "
                f"Minimum suggested budget is around Rs {minimum_required:,}."
            )
        } 
    city_obj = City.query.filter(City.name.ilike(city)).first()
    if not city_obj:
        return {"success": False, "error": f"City '{city}' not found."}

    # Simple budget split (you already have advanced version)
    # ── Budget Allocation ─────────────────────

    # Minimum essentials

    food_budget = days * people * 500
    transport_budget = days * people * 200

    remaining = budget - food_budget - transport_budget

    if remaining <= 0:
        return {
            "success": False,
            "error": "Budget too low after food and transport costs."
        }

    hotel_budget = int(remaining * 0.60)
    activity_budget = int(remaining * 0.40)
    daily_cap = (
        activity_budget / days
        if days
        else activity_budget
    )    

    # ── Hotel Tier Logic ─────────────────────

    if hotel_budget < 4000:

        hotel_type = "budget"

    elif hotel_budget < 12000:

        hotel_type = "mid-range"

    else:

        hotel_type = "premium"
                #─────────────────────

    # ── Semantic retrieval ───────────────────

    query_parts = []

    if preferences:
        query_parts.extend(preferences)

    query_parts.append(city)

    retrieval_query = " ".join(query_parts)

    #  ── retrieval section  ───────────────────
    results = search_places(retrieval_query, k=40)    
    logger.info( f"RETRIEVAL QUERY: {retrieval_query}")
    
    place_ids = []

    if results["metadatas"]:
        
        for meta in results["metadatas"][0]:

            pid = meta.get("place_id")

            if pid:
                place_ids.append(pid)
    
    logger.info(f"RETRIEVED IDS: {place_ids}")   

    places = Place.query.filter(Place.id.in_(place_ids),Place.city_id == city_obj.id).all()   
    places = sorted(places,key=lambda p:_retrieval_score(p,preferences),reverse=True)
    logger.info([(p.name,_retrieval_score(p,preferences))for p in places])

    # fallback
    if not places:
        places = Place.query.filter_by(city_id=city_obj.id).all()
        places = sorted(places,key=lambda p:_retrieval_score(p,preferences),reverse=True)    
        logger.info(f"Replacement candidates: "
                f"{[(p.name,_retrieval_score(p,preferences)) for p in places]}")
    
    if not places:
        return {"success": False, "error": "No places found."}

    fallback_pool = sorted(
        places,
        key=lambda p: (
            p.cost,
            -(p.rating or 0)
        )
    )
    used_ids = set()
    days_plan = []
    total_spent = 0

    for day_num in range(1, days + 1):
        day_places = []
        day_hours = 0
        day_spent = 0

        # 🔥 AVAILABLE PLACES
        available_places = [
            p for p in places
            if p.id not in used_ids
        ]

        # 🔥 KNAPSACK SELECTION
        selected = knapsack_select(
            available_places,
            daily_cap,
            preferences
        )
        remaining_days = days - day_num + 1
        max_places_today = max(
            2,
            len(available_places) // remaining_days
        )
        selected = selected[:max_places_today]  
        
        # 🔥 APPLY CONSTRAINTS
        used_categories = set()
        for place in selected:
            if day_hours >= Config.MAX_HOURS_PER_DAY:
                break
            
            if total_spent + place.cost > activity_budget:
                continue
            
            if place.category in used_categories:
                continue

            if day_hours + place.time_required > Config.MAX_HOURS_PER_DAY:
                continue
            
            used_categories.add(place.category)
            day_places.append({
                **place.to_dict(),
                "value_score": round(_value_score(place, preferences), 2)
            })

            used_ids.add(place.id)
            day_hours += place.time_required
            day_spent += place.cost
            total_spent += place.cost

        # 🔥 FALLBACK (ensure day not empty)
        if day_hours < Config.MAX_HOURS_PER_DAY:
            for place in fallback_pool:
                if total_spent + place.cost > activity_budget:
                    continue
                if place.category in used_categories:
                    continue
                if place.id in used_ids:
                    continue
                if day_hours + place.time_required > Config.MAX_HOURS_PER_DAY:
                    continue

                day_places.append({
                    **place.to_dict(),
                    "value_score": round(_value_score(place, preferences), 2)
                })
                used_categories.add(place.category)

                used_ids.add(place.id)
                day_hours += place.time_required
                day_spent += place.cost
                total_spent += place.cost

                if day_hours >= Config.MAX_HOURS_PER_DAY:
                    break

        days_plan.append({
            "day":day_num,
            "places":day_places,
            "day_activity_cost":day_spent,
            "day_hours":day_hours
            })
        
        # 🔥 Budget breakdown for explanation generator

        leftover = budget - (hotel_budget + food_budget + transport_budget + total_spent)
        hotel_ppn = hotel_budget // max(1, people * days)
        food_ppd = food_budget // max(1, people * days)
        transport_ppd = transport_budget // max(1, people * days)

        grand_total = (
            hotel_budget
            + food_budget
            + transport_budget
            + total_spent
        )

        budget_breakdown = {
            "total_budget": budget,
            "total_spent": grand_total,

            "leftover": max(budget - grand_total, 0),
            "overspent": max(grand_total - budget, 0),
            "days":days,
            "people":people,
            "hotel":{
                "label":hotel_type.title(),
                "type":hotel_type,
                "per_person_per_night":hotel_ppn,
                "total_cost":hotel_budget
                },
            "food":{
                "label":"Meals & Drinks",
                "per_person_per_day":food_ppd,
                "total_cost":food_budget
                },
            "transport":{
                "per_person_per_day":transport_ppd,
                "total_cost":transport_budget
                },
            "activities":{
                "allocated":activity_budget,
                "spent":total_spent
                }
            }

                #─────────────────────
    return {
        "success": True,
        "city": city_obj.name,
        "days": days_plan,
        "total_places": len(used_ids),
        "activity_spent": total_spent,
        "budget_breakdown": budget_breakdown

    }

def replace_place(itinerary, day_num, place_id, preferences):
    """Replace a place in a given day with next best alternative."""

    from models.city import City
    from models.place import Place

    city_obj = City.query.filter(City.name.ilike(itinerary["city"])).first()
    if not city_obj:
        return itinerary

    # Collect already used places
    used = {
        p["id"]
        for d in itinerary["days"]
        for p in d["places"]
        if p["id"] != place_id
    }

    # Get ranked replacement candidates
    places = Place.query.filter_by(city_id=city_obj.id).all()

    places = sorted(places,key=lambda p:_retrieval_score(p,preferences),reverse=True)
    
    logger.info(
        f"Replacement candidates: "
        f"{[(p.name,_retrieval_score(p,preferences)) for p in places]}")
    
    # Find the day
    day = next((d for d in itinerary["days"] if d["day"] == day_num), None)
    if not day:
        return itinerary
    old_place = None
    for p in day["places"]:
        if p["id"] == place_id:
            old_place = p
            break

    if not old_place:
        return itinerary

    old_cost = old_place["cost"]
    

    # Remove old place
    day["places"] = [p for p in day["places"] if p["id"] != place_id]

    # Add best replacement
    for place in places:
        if place.id in used:
            continue
        if place.cost > old_cost * 1.2:
            continue
        day["places"].append({
            **place.to_dict(),
            "value_score": round(
                _value_score(place,preferences),2
            )
        })    
        break

    return itinerary