import re
from typing import Optional

CITY_ALIASES = {
    "lahore": "Lahore",
    "islamabad": "Islamabad",
    "isb": "Islamabad",
    "murree": "Murree",
}

PREFERENCE_MAP = {
    "nature": "nature",
    "historical": "historical",
    "food": "food",
    "shopping": "shopping",
    "hidden": "hidden",
}

def extract_budget(text: str) -> Optional[int]:
    text = text.lower().replace(",", "")

    # 50k → 50000
    match = re.search(r"(\d+)\s*k", text)
    if match:
        return int(match.group(1)) * 1000

    # 20 thousand → 20000
    match = re.search(r"(\d+)\s*thousand", text)
    if match:
        return int(match.group(1)) * 1000

    # plain number
    match = re.search(r"\b(\d{3,6})\b", text)
    if match:
        return int(match.group(1))

    return None


def extract_days(text: str) -> Optional[int]:
    text = text.lower()

    match = re.search(r"(\d+)[-\s]*(day|days|night|nights)", text)
    if match:
        return int(match.group(1))

    # week support
    if "week" in text:
        return 7

    return None


def extract_people(text: str) -> Optional[int]:
    text = text.lower()

    # 4 people
    match = re.search(r"(\d+)\s*(people|person)", text)
    if match:
        return int(match.group(1))

    # family of 5
    match = re.search(r"family of (\d+)", text)
    if match:
        return int(match.group(1))

    # just me / solo
    if "just me" in text or "solo" in text:
        return 1

    return None

def extract_city(text: str) -> Optional[str]:
    text = text.lower()
    for k, v in CITY_ALIASES.items():
        if k in text:
            return v
    return None


def extract_preferences(text: str) -> list:
    text = text.lower()
    prefs = []
    for k, v in PREFERENCE_MAP.items():
        if k in text:
            prefs.append(v)
    return prefs


# 🔥 THIS IS WHAT WAS MISSING
def extract_all_entities(message: str) -> dict:
    return {
        "budget": extract_budget(message),
        "days": extract_days(message),
        "people": extract_people(message),
        "city": extract_city(message),
        "preferences": extract_preferences(message),
    }