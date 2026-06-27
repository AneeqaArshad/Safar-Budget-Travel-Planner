"""
Intent Classifier v2
────────────────────
Uses a two-layer approach:
  1. Exact phrase patterns (highest priority, catches compound sentences)
  2. Weighted keyword scoring per intent (replaces simple "any keyword" matching)

Also extracts a confidence score so the chat controller can decide
whether to ask for clarification.

Intents:
    PLAN_REQUEST | EXPLANATION_REQUEST | MODIFY_REQUEST |
    SET_BUDGET | SET_DAYS | SET_PEOPLE | SET_CITY | SET_PREFERENCE |
    GREETING | AFFIRMATION | NEGATION | UNKNOWN
"""

import re

# ── Phrase patterns (tried first, in order) ───────────────────────────────
PHRASE_PATTERNS = [
    # Modify / replace
    (r"\b(remove|replace|swap|change|switch|delete)\b.*(place|spot|attraction|this|it)", "MODIFY_REQUEST"),
    (r"\b(don'?t|do not)\s+(want|like|need)\b.*\b(place|spot|this)\b", "MODIFY_REQUEST"),

    # Plan
    (r"\b(plan|generate|create|make|build)\b.*\b(itinerary|travel plan|day plan|trip plan|schedule)\b", "PLAN_REQUEST"),
    (r"\b(itinerary|travel plan|day plan)\b", "PLAN_REQUEST"),

    # Explanation
    (r"\b(why|how come|what'?s the reason|explain|tell me why|justify)\b", "EXPLANATION_REQUEST"),

    # Affirmation / Negation
    (r"^(yes|yeah|yep|sure|ok|okie|okay|sounds good|perfect|great|go ahead|do it|confirm)\b", "AFFIRMATION"),
    (r"^(no|nope|nah|not really|don'?t|never mind|cancel|stop)\b", "NEGATION"),

    # Greetings
    (r"^(hi|hello|hey|salaam|assalam|good (morning|afternoon|evening))\b", "GREETING"),

    # City Patterns
    (r"\b(lahore|islamabad|murree)\b", "SET_CITY"),]

# ── Weighted keyword scoring ───────────────────────────────────────────────
# { intent: [(keyword, weight), ...] }
KEYWORD_WEIGHTS = {
    "PLAN_REQUEST": [
        ("plan", 4), ("itinerary", 4), ("generate", 4), ("schedule", 3),("travel plan", 4), 
        ("day plan", 4), ("trip plan", 4), ("create itinerary", 5), ("plan my", 5),
        ("make itinerary", 5),
    ],
    "SET_BUDGET": [
        ("budget", 3), ("pkr", 3), ("rs", 2), ("rupee", 2), ("rupees", 2),
        ("spend", 2), ("cost", 2), ("afford", 2), ("thousand", 1),
        ("money", 1), ("price", 1), ("cheap", 1), ("low budget", 2),
    ],
    "SET_DAYS": [
        ("days", 3), ("nights", 3), ("day trip", 3), ("week", 2),
        ("weekend", 2), ("duration", 2), ("long", 1), ("short", 1),
    ],
    "SET_PEOPLE": [
        ("people", 3), ("persons", 3), ("friends", 2), ("family", 2),
        ("group", 2), ("adults", 2), ("couple", 2), ("solo", 2),
        ("alone", 2), ("just me", 3), ("with my", 1), ("members", 1),
    ],
    "SET_CITY": [
        ("lahore", 4), ("islamabad", 4), ("murree", 4), ("isb", 3),
        ("destination", 1), ("city", 1), ("where", 1),
    ],
    "SET_PREFERENCE": [
        ("nature", 3), ("historical", 3), ("food", 3), ("history", 2),
        ("heritage", 2), ("shopping", 3), ("hidden", 3), ("adventure", 2),
        ("culture", 2), ("sightseeing", 2), ("prefer", 2), ("like", 1),
        ("love", 1), ("enjoy", 1), ("chill", 2), ("relaxing", 2),
    ],
    "EXPLANATION_REQUEST": [
        ("why", 3), ("reason", 3), ("explain", 3), ("because", 2),
        ("how did", 2), ("justify", 2), ("elaborate", 2),
    ],
    "MODIFY_REQUEST": [
        ("remove", 3), ("replace", 3), ("swap", 3), ("change", 2),
        ("different", 2), ("instead", 2), ("another", 2), ("update", 2),
    ],
}

THRESHOLD = 3   # minimum score to declare an intent


def classify_intent(message: str) -> dict:
    """
    Returns { "intent": str, "confidence": float (0-1), "scores": dict }
    Confidence 1.0 = phrase match, <1 = keyword scoring.
    """
    text = message.lower().strip()
    text = re.sub(r"[^\w\s'.]", " ", text)   # keep apostrophes for contractions

    # Layer 1: phrase patterns
    for pattern, intent in PHRASE_PATTERNS:
        if re.search(pattern, text):
            return {"intent": intent, "confidence": 1.0, "scores": {intent: 99}}

    # Layer 2: weighted keyword scoring
    scores = {}
    for intent, pairs in KEYWORD_WEIGHTS.items():
        total = sum(w for kw, w in pairs if kw in text)
        if total > 0:
            scores[intent] = total

    if not scores:
        return {"intent": "UNKNOWN", "confidence": 0.0, "scores": {}}

    best_intent = max(scores, key=scores.get)
    best_score  = scores[best_intent]

    if best_score < THRESHOLD:
        return {"intent": "UNKNOWN", "confidence": best_score / THRESHOLD, "scores": scores}

    # Normalize confidence
    max_possible = max(sum(w for _, w in pairs) for pairs in KEYWORD_WEIGHTS.values())
    confidence   = min(1.0, best_score / max_possible)

    return {"intent": best_intent, "confidence": confidence, "scores": scores}
