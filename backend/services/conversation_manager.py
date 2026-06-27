"""
Conversation Manager
Centralized conversational behavior layer
"""

CITY_ACKS = {
    "Lahore":
        "Lahore is a wonderful choice! Sounds exciting!",

    "Islamabad":
        "Islamabad has beautiful scenery and peaceful spots 🌿",

    "Murree":
        "Murree sounds like a relaxing mountain getaway ⛰️"
}


def acknowledge_city(city):

    return CITY_ACKS.get(
        city,
        f"{city} sounds like a great choice!"
    )


def acknowledge_people(people):

    if people == 1:
        return "Solo trips can be a lot of fun."

    if people == 2:
        return "A trip for two sounds great."

    return f"{people} people — sounds like a fun group."


def acknowledge_preferences(prefs):

    if not prefs:
        return ""

    p = ", ".join(prefs)

    return f"I'll prioritize {p} places."


def build_trip_summary(ctx):

    pref_str = (
        ", ".join(ctx["preferences"])
        if ctx.get("preferences")
        else "No preference"
    )

    return f"""
📍 City: {ctx['city']}
💰 Budget: Rs {ctx['budget']:,}
📅 Days: {ctx['days']}
👥 People: {ctx['people']}
🎯 Preferences: {pref_str}
"""

FOLLOWUP_HINTS = {

    "food":
        "I'll prioritize food streets and popular restaurants.",

    "historical":
        "I'll include historical and cultural attractions.",

    "nature":
        "I'll prioritize scenic and relaxing outdoor spots.",

    "shopping":
        "I'll include shopping and local market areas."
}


def build_preference_hint(prefs):

    if not prefs:
        return ""

    hints = []

    for p in prefs:

        if p in FOLLOWUP_HINTS:
            hints.append(
                FOLLOWUP_HINTS[p]
            )

    return " ".join(hints)


def contextual_followup(ctx, missing):

    pref_hint = build_preference_hint(
        ctx.get("preferences", [])
    )

    if not pref_hint:
        return ""

    if not missing:
        return pref_hint

    return (
        pref_hint
        + " "
    )