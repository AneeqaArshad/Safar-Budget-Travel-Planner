"""
LLM-based Entity Extractor
-------------------------
Uses Ollama to extract structured travel parameters.
"""

import json
import re

from services.llm import safe_llm_invoke


VALID_CITIES = [
    "lahore",
    "islamabad",
    "murree"
]

VALID_PREFERENCES = [
    "food",
    "historical",
    "nature",
    "shopping",
    "adventure",
    "family",
    "luxury",
    "culture"
]


def _clean_preferences(prefs):
    """
    Ensure preferences are ALWAYS list[str]
    """

    if not isinstance(prefs, list):
        return []

    cleaned = []

    for item in prefs:

        if not isinstance(item, str):
            continue

        item = item.strip().lower()

        if item in VALID_PREFERENCES:
            cleaned.append(item)

    return list(set(cleaned))

def extract_entities_fast(message: str):

    msg = message.lower().strip()

    result = {
        "budget": None,
        "days": None,
        "people": None,
        "city": None,
        "preferences": []
    }

    # budget
    budget_match = re.search(r'\b(\d{4,6})\b', msg)

    if budget_match:
        value = int(budget_match.group(1))

        if value >= 3000:
            result["budget"] = value

    # days
    days_match = re.search(r'(\d+)\s*(day|days)', msg)

    if days_match:
        result["days"] = int(days_match.group(1))

    # people
    people_match = re.search(r'(\d+)\s*(people|persons|travelers)', msg)

    if people_match:
        result["people"] = int(people_match.group(1))

    # city
    for city in VALID_CITIES:
        if city in msg:
            result["city"] = city.title()

    # preferences
    for pref in VALID_PREFERENCES:
        if pref in msg:
            result["preferences"].append(pref)

    return result

def extract_entities_llm(message: str) -> dict:
    fast_result = extract_entities_fast(message)
    print("FAST RESULT:", fast_result)
    if any([
        fast_result["budget"],
        fast_result["days"],
        fast_result["people"],
        fast_result["city"],
        fast_result["preferences"]
    ]):
        return fast_result

    prompt = f"""
Extract travel information from this message.

Return ONLY valid JSON.

Message:
{message}

Format:
{{
    "budget": number or null,
    "days": number or null,
    "people": number or null,
    "city": string or null,
    "preferences": []
}}
"""

    raw = safe_llm_invoke(prompt)

    if not raw:
        return {}

    try:
        cleaned = raw.strip()
        cleaned = cleaned.replace("```json", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not json_match:
            return {}

        data = json.loads(json_match.group())

        city = data.get("city")

        if isinstance(city, str):
            city = city.lower().strip()

            if city not in VALID_CITIES:
                city = None
        else:
            city = None

        result = {
            "budget": data.get("budget")
            if isinstance(data.get("budget"), int)
            else None,

            "days": data.get("days")
            if isinstance(data.get("days"), int)
            else None,

            "people": data.get("people")
            if isinstance(data.get("people"), int)
            else None,

            "city": city,

            "preferences": _clean_preferences(
                data.get("preferences", [])
            ),
        }

        return result

    except Exception as e:
        print("[LLM ENTITY ERROR]", e)
        print(raw)

        return {}