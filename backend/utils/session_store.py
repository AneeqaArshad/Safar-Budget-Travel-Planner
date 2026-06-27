"""
Session Store v2
────────────────
Tracks full conversation context per session:
  - budget, days, people, city, preferences
  - conversation_stage: 'collecting' | 'confirming' | 'planning' | 'done'
  - last_itinerary, confirmation_pending
  - message_history (last N turns for context)
"""

from typing import Optional
from utils.logger import logger
import time

_sessions: dict = {}
MAX_HISTORY = 20
SESSION_TIMEOUT = 60 * 60 * 3

def cleanup_sessions():

    now = time.time()

    expired = []

    for sid, data in _sessions.items():

        created = data.get("created_at", now)

        if now - created > SESSION_TIMEOUT:
            expired.append(sid)

    for sid in expired:
        del _sessions[sid]

def get_session(sid: str) -> dict:

    cleanup_sessions()

    if sid not in _sessions:
        _sessions[sid] = {
            "budget":      None,
            "days":        None,
            "people":      None,
            "city":        None,
            "preferences": [],
            "last_itinerary":      None,
            "confirmation_pending": False,
            "stage":       "collecting",   # collecting | confirming | done
            "history":     [],
            "created_at":  time.time(),
        }
    return _sessions[sid]


def update_session(sid: str, updates: dict):

    s = get_session(sid)

    for k, v in updates.items():

        # ignore empty updates
        if v in [None, "", []]:
            continue

        # safely merge preferences
        if k == "preferences":

            existing = s.get(
                "preferences",
                []
            )

            safe_existing = [
                x for x in existing
                if isinstance(x, str)
            ]

            safe_new = [
                x for x in v
                if isinstance(x, str)
            ]

            merged = list(
                set(
                    safe_existing + safe_new
                )
            )

            s["preferences"] = merged

        else:
            s[k] = v
            

def add_to_history(sid: str, role: str, text: str):
    s = get_session(sid)
    s["history"].append({"role": role, "text": text})
    if len(s["history"]) > MAX_HISTORY:
        s["history"] = s["history"][-MAX_HISTORY:]


def get_missing_fields(sid: str) -> list:
    s = get_session(sid)
    return [f for f in ["budget", "days", "people", "city"] if not s.get(f)]


def get_filled_fields(sid: str) -> dict:
    s = get_session(sid)
    return {k: s[k] for k in ["budget", "days", "people", "city", "preferences"] if s.get(k)}


def set_stage(sid: str, stage: str):
    logger.info(
        f"STAGE CHANGE: {sid} -> {stage}")
    get_session(sid)["stage"] = stage

def get_stage(sid: str) -> str:
    return get_session(sid).get("stage", "collecting")


def set_confirmation_pending(sid: str, val: bool):
    get_session(sid)["confirmation_pending"] = val


def is_confirmation_pending(sid: str) -> bool:
    return get_session(sid).get("confirmation_pending", False)


def store_itinerary(sid: str, itinerary: dict):
    get_session(sid)["last_itinerary"] = itinerary


def get_last_itinerary(sid: str) -> Optional[dict]:
    return get_session(sid).get("last_itinerary")


def clear_session(sid: str):
    if sid in _sessions:
        del _sessions[sid]
