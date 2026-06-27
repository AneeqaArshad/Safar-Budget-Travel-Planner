"""
Conversation Manager v2
────────────────────────
Handles ALL bot reply generation:
  - Smart follow-up questions (asks only what's missing, in natural order)
  - Confirmation flow before planning
  - Proactive suggestions during collection
  - LLM explanation of the final plan (optional, falls back to template)
"""

from flask import current_app
from services.conversation_manager import (
    acknowledge_city,
    acknowledge_people,
    acknowledge_preferences,
    contextual_followup
)


# ── Confirmation summary ──────────────────────────────────────────────────

def build_confirmation(ctx: dict) -> str:
    pref_str = ", ".join(ctx["preferences"]) if ctx.get("preferences") else "no specific preference"
    return (
        f"Great, here's what I have:\n\n"
        f"📍 **City:** {ctx['city']}\n"
        f"💰 **Budget:** Rs {ctx['budget']:,}\n"
        f"📅 **Days:** {ctx['days']}\n"
        f"👥 **People:** {ctx['people']}\n"
        f"🎯 **Preferences:** {pref_str}\n\n"
        f"Shall I go ahead and generate your itinerary? _(Say yes to confirm, "
        f"or tell me anything you'd like to change.)_"
    )


# ── Smart follow-up questions ─────────────────────────────────────────────

def _next_question(missing: list, ctx: dict) -> str:
    """Ask for the single most important missing field, with helpful context."""
    if not missing:
        return "How many days are you planning?"

    
    filled = {k: v for k, v in ctx.items() if v}
    first_missing = missing[0]

    questions = {
        "city": (
            "Which city would you like to explore? "
            "I currently cover **Lahore**, **Islamabad**, and **Murree**."
        ),
        "budget": (
            "What's your total budget for this trip? "
            "_(You can say something like 'Rs 15,000' or '20k' or even just 'low budget'.)_"
        ),
        "days": (
            "How many days are you planning to travel? "
            "_(Even a range like '2-3 days' works!)_"
        ),
        "people": (
            "How many people will be travelling? "
            "_(Just you, a couple, family of 4 — anything works.)_"
        ),
    }

    # Natural multi-field questions
    if first_missing == "budget" and "days" in missing:
        return (
            "What's your budget, and how many days are you planning? "
            "_(e.g., 'Rs 20,000 for 2 days')_"
        )
    if first_missing == "days" and "people" in missing:

        city_name = ctx.get("city")

        if not city_name:
            city_name = "your destination"

        return (
            f"How many days are you staying in {city_name}, "
            f"and how many people are travelling?"
        )

    return questions.get(first_missing, "Could you give me a bit more detail?")


# ── Intent → reply dispatch ───────────────────────────────────────────────

def generate_conversational_reply(intent: str, confidence: float,
                                   missing: list, ctx: dict) -> str:
    city   = ctx.get("city", "your destination")
    budget = ctx.get("budget")
    days   = ctx.get("days")
    people = ctx.get("people")
    prefs  = ctx.get("preferences", [])

    # Greeting
    if intent == "GREETING":
        return (
            "Assalamu alaikum! I'm **Safar**, your travel planning assistant. ✦\n\n"
            "I can plan a complete day-by-day trip to **Lahore**, **Islamabad**, or **Murree** "
            "— within your exact budget, with clear explanations for every recommendation.\n\n"
            "Just tell me where you want to go, your budget, number of days, and how many "
            "people — or describe your trip in one sentence and I'll figure it out!"
        )

    # Acknowledged budget
    if intent == "SET_BUDGET" and budget and not missing:
        return build_confirmation(ctx)

    if intent == "SET_BUDGET" and budget:

        next_q = _next_question(missing, ctx)

        if not next_q:
            next_q = "How many days are you planning?"

        return (
            f"Got it — Rs {budget:,} budget noted! "
            + next_q
        )
    # Acknowledged city
    if intent == "SET_CITY" and city != "your destination":
        if not missing:
            return build_confirmation(ctx)
        reply = acknowledge_city(city)

        return (
            f"{reply} "
            + _next_question(missing, ctx)
        )

    # Acknowledged days
    if intent == "SET_DAYS" and days:
        if not missing:
            return build_confirmation(ctx)
        return f"Perfect — {days} day{'s' if days > 1 else ''} noted. " + _next_question(missing, ctx)

    # Acknowledged people
    if intent == "SET_PEOPLE" and people:
        if not missing:
            return build_confirmation(ctx)
        reply = acknowledge_people(people)

        return (
            f"{reply} "
            + _next_question(missing, ctx)
        )
    
    # Preference acknowledged
    if intent == "SET_PREFERENCE" and prefs:

        pref_str = " and ".join(prefs)

        if not missing:
            return build_confirmation(ctx)

        return (
            f"Great — I'll prioritize {pref_str} experiences. "
            + _next_question(missing, ctx)
        )

    # Low confidence / unknown — try to be helpful
    if intent == "UNKNOWN" or confidence < 0.4:
        if missing:
            return (
                "I didn't quite catch that — no worries! "
                + _next_question(missing, ctx)
            )
        return (
            "I'm not sure what you mean — but I have all your details ready. "
            "Say **'plan my trip'** to generate your itinerary, or ask me to explain anything!"
        )

    # Generic fallback with missing fields
    if missing:
        return _next_question(missing, ctx)

    return (
        "I have all the details I need! Say **'yes'** or **'plan my trip'** to generate "
        "your itinerary, or tell me if you'd like to change anything."
    )


# ── Plan confirmation reply ───────────────────────────────────────────────

def confirmation_reply(ctx: dict) -> str:
    return build_confirmation(ctx)


# ── LLM / Template explanation ────────────────────────────────────────────

def _build_prompt(itinerary: dict, ctx: dict) -> str:
    """Build LLM explanation prompt (STRICT, NO MODIFICATION ALLOWED)."""

    memory = ctx.get("memory",[])

    memory_text = ""

    if memory:

        memory_text = (
            "Previous conversation context:\n"
            + "\n".join(memory[:3])
            + "\n\n"
        )
    days_text = []
    for d in itinerary["days"]:
        places = [p["name"] for p in d["places"]]
        days_text.append(
            f"Day {d['day']}: {', '.join(places) if places else 'Free day'}"
        )

    prompt = f"""
Explain the following travel itinerary clearly and concisely.
{memory_text}
Trip Details:
- Budget: Rs {itinerary['budget_breakdown']['total_budget']}
- Days: {itinerary['budget_breakdown']['days']}
- People: {itinerary['budget_breakdown']['people']}
- City: {itinerary['city']}

Itinerary:
{chr(10).join(days_text)}

IMPORTANT:
- DO NOT modify or suggest changes
- Only explain WHY it fits the budget
- Mention value (cost vs experience)
- Keep under 100 words
- Be simple and clear
"""

    return prompt


def _fallback_explanation(itinerary):

    b = itinerary.get("budget_breakdown", {})

    transport = b.get("transport",{}).get("total_cost",0)
    hotel = b.get("hotel",{}).get("total_cost",0)
    hotel_type = b.get("hotel",{}).get("type","standard")
    food = b.get("food",{}).get( "total_cost",0)
    activities = b.get("activities",{}).get("spent",0)
    leftover = b.get("leftover",0)
    total = b.get("total", itinerary.get("total_cost", 0))

    city = itinerary.get("city", "your destination")

    return f"""
    Your {city} itinerary has been successfully generated.

    Estimated Budget:

    • Hotel ({hotel_type}): Rs {hotel}
    • Food: Rs {food}
    • Transport: Rs {transport}
    • Activities: Rs {activities}
    • Remaining: Rs {leftover}

    The itinerary was optimized to maximize experiences while staying within budget.
    """

def generate_explanation(itinerary: dict, ctx: dict) -> str:

    api_key = current_app.config.get("ANTHROPIC_API_KEY", "")

    if (not api_key or api_key == "your-api-key"):
        return _fallback_explanation(itinerary)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=160,
            messages=[{
                "role":"user",
                "content":_build_prompt(itinerary, ctx)
            }])
        return msg.content[0].text.strip()

    except Exception as e:

        current_app.logger.warning( f"LLM explanation failed: {e}")

        return _fallback_explanation(itinerary)
        
        