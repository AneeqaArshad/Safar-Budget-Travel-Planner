import uuid
import re
from utils.logger import logger
from flask import Blueprint, request, jsonify

from services.intent_classifier import classify_intent
from services.llm_entity_extractor import extract_entities_llm
from services.entity_extractor import extract_all_entities
from services.planning_engine import  replace_place
from utils.memory_store import store_message, retrieve_memory
from services.llm import health_check
from services.explanation_generator import (
    generate_conversational_reply,
    generate_explanation,
    confirmation_reply,
)
from utils.session_store import (
    get_session, update_session, add_to_history,
    get_missing_fields,
    get_stage, set_stage,
    set_confirmation_pending, is_confirmation_pending,
    store_itinerary, get_last_itinerary, clear_session,
)

from agent.graph import build_graph
from models.trip_history import TripHistory
from extensions import db
from flask_jwt_extended import (jwt_required,get_jwt_identity)

chat_bp = Blueprint("chat", __name__)
graph = build_graph()  # ✅ move outside (important)


@chat_bp.route("/message", methods=["POST"])
@jwt_required()
def handle_message():
        try:
            data = request.get_json()
            if not data or "message" not in data:
                return jsonify({"error": "Missing 'message'"}), 400

            user_msg = data.get("message", "").strip()
            lower_msg = user_msg.lower().strip()
            session_id = data.get("session_id") or str(uuid.uuid4())
            user_id = get_jwt_identity()
            logger.info(f"USER: {user_id}")

            if not user_msg:
                return jsonify({"error": "Empty message"}), 400

            # 🧠 Memory
            recent_memory = retrieve_memory(session_id, user_msg)
            logger.info(f"MEMORY: {recent_memory}")

            add_to_history(session_id, "user", user_msg)
            store_message(session_id, "user", user_msg)

            # ✅ Intent
            clf = classify_intent(user_msg)
            intent = clf["intent"]
            if user_msg.isdigit():
                num = int(user_msg)
                missing = get_missing_fields(session_id)
                if "people" in missing:
                    intent = "SET_PEOPLE"
                elif "days" in missing:
                    intent = "SET_DAYS"
                elif "budget" in missing:
                    intent = "SET_BUDGET"
            # 🔥 Start fresh trip if user changes city after completed plan
            if (
                get_stage(session_id) == "done"
                and intent == "SET_CITY"
            ):

                extracted = extract_all_entities(user_msg)

                clear_session(session_id)

                update_session(session_id, {
                    "city": extracted.get("city")
                })
            ctx = get_session(session_id)
            logger.info(f"RESET SESSION: {ctx}")
        
            logger.info(f"INTENT: {intent}")


            # ✅ Entities
            rule_entities = extract_all_entities(user_msg)
            logger.info(f"RULE ENTITIES: {rule_entities}")
            llm_entities = {}
            logger.info(f"LLM ENTITIES: {llm_entities}")


            if llm_entities.get("preferences"):
                existing = rule_entities.get("preferences", [])

                rule_entities["preferences"] = list(
                    set(existing + llm_entities["preferences"])
                )
                logger.info(f"AFTER MERGE: {rule_entities}")
            trip_patterns = re.findall(
                r"(lahore|islamabad|murree)",
                lower_msg
            )

            unique_cities = list(set(trip_patterns))

            if len(unique_cities) > 1:

                reply = (
                    "I can see multiple destinations in your request:\n\n"
                    + "\n".join(
                        [f"• {city.title()}" for city in unique_cities]
                    )
                    + "\n\nFor now I generate one itinerary at a time."
                    "\nWhich destination would you like me to plan first?"
                )
                clear_session(session_id)
                return jsonify({
                    "reply": reply,
                    "intent": "MULTI_TRIP",
                    "data": None,
                    "success": True,
                    "session_id": session_id
                })
            if user_msg.isdigit():
                if intent == "SET_PEOPLE":
                    rule_entities["people"] = int(user_msg)
                elif intent == "SET_DAYS":
                    rule_entities["days"] = int(user_msg)
                elif intent == "SET_BUDGET":
                    rule_entities["budget"] = int(user_msg)

            missing_after_rules = any(
                rule_entities.get(field) in [None, ""]
                for field in [
                    "budget",
                    "days",
                    "people",
                    "city"
                    ]
                )

            llm_entities = {}
            safe_llm_entities = {}

            if (
                missing_after_rules
                    or not rule_entities.get("preferences")
            ):
                logger.info("STARTING LLM ENTITY EXTRACTION")
                llm_entities = extract_entities_llm(user_msg) or {}
                logger.info(f"RULE ENTITIES: {rule_entities}")
                logger.info(f"LLM RESULT: {llm_entities}")
                
                # keep ONLY fields related to current intent

                allowed = {
                    "SET_BUDGET":[
                        "budget",
                        "people",
                        "days",
                        "city",
                        "preferences"
                    ],

                    "SET_DAYS":[
                        "days",
                        "people",
                        "budget",
                        "city",
                        "preferences"
                    ],

                    "SET_PEOPLE":[
                        "people",
                        "days",
                        "budget",
                        "city",
                        "preferences"
                    ],

                    "SET_CITY":[
                        "city",
                        "days",
                        "budget",
                        "people",
                        "preferences"
                    ],

                    "SET_PREFERENCE":[
                        "preferences",
                        "budget",
                        "days",
                        "people",
                        "city"
                    ]
                }

                allowed_fields = allowed.get(intent, [])

                llm_entities = {
                    k:v
                    for k,v in llm_entities.items()
                    if k in allowed_fields
                }

            for k, v in llm_entities.items():

                if not v:
                    continue

                if k == "preferences":

                    if isinstance(v, list):

                        cleaned = []

                        for item in v:
                            if isinstance(item, str):
                                cleaned.append(item.lower())

                        safe_llm_entities[k] = cleaned

                    continue

                if isinstance(v, (str, int, float)):
                    safe_llm_entities[k] = v

            entities = rule_entities.copy()
            logger.info(f"SAFE LLM ENTITIES: {safe_llm_entities}")

            for k, v in safe_llm_entities.items():

                existing = entities.get(k)

                # SPECIAL CASE FOR PREFERENCES
                if k == "preferences":
                    existing_prefs = entities.get("preferences", [])
                    combined = existing_prefs + v
                    entities["preferences"] = list(set(combined))
                    continue

                if existing in [None, [], ""]:
                    entities[k] = v

            
            logger.info(f"ENTITIES: {entities}")
                
            update_session(session_id, entities)
            ctx = get_session(session_id)
            ctx["memory"] = recent_memory
            logger.info(f"SESSION: {ctx}")
            missing = get_missing_fields(session_id)
            logger.info(f"MISSING FIELDS: {missing}")

            conf = clf.get("confidence", 0.0)        
            
            logger.info(f"CURRENT STAGE: {get_stage(session_id)} | INTENT: {intent}")
            
            # prevent repeated "yes" after itinerary already exists
            if get_stage(session_id) == "done" and intent == "AFFIRMATION":
                return jsonify({
                    "reply": "Your itinerary is already generated. You can modify it or start a new trip.",
                    "intent": intent,
                    "data": get_last_itinerary(session_id),
                    "success": True,
                    "session_id": session_id
                })  
            
            # ── Confirmation pending ──
            if is_confirmation_pending(session_id):
                if intent == "AFFIRMATION":
                    set_confirmation_pending(session_id, False)
                    set_stage(session_id, "planning")
                    return _run_planning(session_id, ctx)

                elif intent == "NEGATION":
                    set_confirmation_pending(session_id, False)
                    set_stage(session_id, "collecting")

                    reply = "No problem! What would you like to change?"
                    add_to_history(session_id, "bot", reply)
                    store_message(session_id, "assistant", reply)

                    return jsonify({
                        "reply": reply,
                        "intent": intent,
                        "data": None,
                        "success": True,
                        "session_id": session_id
                    })

            # ── Modify ──
            if intent == "MODIFY_REQUEST":
                return _handle_modify(session_id, ctx, data)

            # ── Explanation ──
            if intent == "EXPLANATION_REQUEST":
                last = get_last_itinerary(session_id)

                reply = generate_explanation(last, ctx) if last else \
                    "No plan yet. Say 'plan my trip' first."

                add_to_history(session_id, "bot", reply)
                store_message(session_id, "assistant", reply)

                return jsonify({
                    "reply": reply,
                    "intent": intent,
                    "data": None,
                    "success": True,
                    "session_id": session_id
                })

            # ── Plan request ──
            if intent == "PLAN_REQUEST":

                # Do NOT allow direct planning during collection
                if get_stage(session_id) == "collecting":

                    if missing:
                        reply = generate_conversational_reply(intent, conf, missing, ctx)

                        add_to_history(session_id, "bot", reply)
                        store_message(session_id, "assistant", reply)

                        return jsonify({
                            "reply": reply,
                            "intent": "NEEDS_INFO",
                            "data": None,
                            "success": True,
                            "session_id": session_id
                        })

                    # all info collected -> move to confirmation
                    set_stage(session_id, "confirming")
                    set_confirmation_pending(session_id, True)

                    reply = confirmation_reply(ctx)

                    add_to_history(session_id, "bot", reply)
                    store_message(session_id, "assistant", reply)

                    return jsonify({
                        "reply": reply,
                        "intent": "CONFIRMING",
                        "data": None,
                        "success": True,
                        "session_id": session_id
                    })

                # only confirmed users can plan
                if get_stage(session_id) != "confirming":
                    reply = "Please confirm your trip details first."

                    return jsonify({
                        "reply": reply,
                        "intent": "CONFIRM_REQUIRED",
                        "data": None,
                        "success": True,
                        "session_id": session_id
                    })

                return _run_planning(session_id, ctx)


            # ── Confirmation step ──
            # Ask preferences before confirmation

            if (
                not missing
                and not ctx.get("preferences")
                and not ctx.get("preferences_asked")
            ):
                
                update_session(session_id, {"preferences_asked": True})

                reply = (
                    "Do you have any preferences for this trip? "
                    "(food, shopping, historical, nature, luxury, adventure etc.) "
                    "You can also say 'no preference'."
                )

                add_to_history(session_id, "bot", reply)

                return jsonify({
                    "reply": reply,
                    "intent": "ASKING_PREFERENCES",
                    "data": None,
                    "session_id": session_id
                })


            # --- Confirmation step ---
            if not missing and get_stage(session_id) == "collecting":
                set_stage(session_id, "confirming")
                set_confirmation_pending(session_id, True)

                reply = confirmation_reply(ctx)

                add_to_history(session_id, "bot", reply)
                store_message(session_id, "assistant", reply)

                return jsonify({
                    "reply": reply,
                    "intent": "CONFIRMING",
                    "data": None,
                    "session_id": session_id,
                    "success": True
                })

            # ── Default ──
            reply = generate_conversational_reply(intent, conf, missing, ctx)

            add_to_history(session_id, "bot", reply)
            store_message(session_id, "assistant", reply)

            return jsonify({
                "reply": reply,
                "intent": intent,
                "data": None,
                "success": True,
                "session_id": session_id
            })
        
        except Exception as e:
            logger.exception("CHAT ROUTE ERROR")

            return jsonify({
                "success": False,
                "reply": "Something went wrong.",
                "errors": [str(e)]
            }), 500

def _run_planning(session_id, ctx):
        try:
            result = graph.invoke({
                "context": ctx
            })["plan"]
            logger.info("PLANNING RESULT =====")
            logger.info(result)
            logger.info ("===========================\n")
        except Exception as e:

            logger.exception("GRAPH EXECUTION FAILED")

            return jsonify({
                "reply": "Failed to generate itinerary.",
                "intent": "PLAN_REQUEST",
                "data": None,
                "success": False,
                "errors": [str(e)],
                "session_id": session_id
            }), 500

        if not result["success"]:
            reply = f"Hmm, issue: {result['error']}"
            add_to_history(session_id, "bot", reply)
            store_message(session_id, "assistant", reply)

            return jsonify({
                "reply": reply,
                "intent": "PLAN_REQUEST",
                "data": None,
                "success": True,
                "session_id": session_id
            })
        store_itinerary(session_id, result)
        try:
            user_id = get_jwt_identity()
            if user_id:
                history = TripHistory(
                    user_id=user_id,
                    city=result["city"],
                    budget=result["budget_breakdown"]["total_budget"],
                    days=len(result["days"]),
                    people=result["budget_breakdown"]["people"],
                    itinerary_json=result
                )

                db.session.add(history)
                db.session.commit()

        except Exception as e:
            logger.exception(
                "Failed to save trip history"
                )
        set_stage(session_id, "done")

        explanation = generate_explanation(result, ctx)
        result["ai_explanation"] = explanation

        add_to_history(session_id, "bot", explanation)
        store_message(session_id, "assistant", explanation)
        logger.info("\n===== JSON RESPONSE =====")
        logger.info({
            "reply": explanation,
            "intent": "PLAN_REQUEST",
            "data": result,
            "success": True,
            "session_id": session_id
        })
        logger.info ("=========================\n")

        return jsonify({
            "reply": explanation,
            "intent": "PLAN_REQUEST",
            "data": result,
            "success": True,
            "session_id": session_id
        })


def _handle_modify(session_id, ctx, data):
        last = get_last_itinerary(session_id)

        if not last:
            return jsonify({
                "reply": "No itinerary yet.",
                "intent": "MODIFY_REQUEST",
                "data": None,
                "success": True,
                "session_id": session_id
            })

        day_num = data.get("day_num")
        place_id = data.get("place_id")

        if not day_num or not place_id:
            return jsonify({
                "reply": "Use Replace button.",
                "intent": "MODIFY_REQUEST",
                "data": None,
                "session_id": session_id,
                "success": True
            })

        updated = replace_place(last, day_num, place_id, ctx.get("preferences", []))
        store_itinerary(session_id, updated)
        try:
            user_id = get_jwt_identity()

            latest_trip = (
                TripHistory.query
                .filter_by(user_id=user_id)
                .order_by(TripHistory.created_at.desc())
                .first()
            )

            if latest_trip:
                latest_trip.itinerary_json = updated
                db.session.commit()

        except Exception:
            logger.exception(
                "Failed to update trip history"
            )
        set_stage(session_id, "done")
        set_confirmation_pending(session_id, False)

        reply = "Done! Place replaced."
        add_to_history(session_id, "bot", reply)
        store_message(session_id, "assistant", reply)

        return jsonify({
            "reply": reply,
            "intent": "MODIFY_REQUEST",
            "data": updated,
            "session_id": session_id,
            "success": True
        })


@chat_bp.route("/reset", methods=["POST"])
@jwt_required()
def reset():
        data = request.get_json() or {}
        sid = data.get("session_id", "")

        if sid:
            clear_session(sid)

        return jsonify({
            "success": True,
            "reply": "Session cleared.",
            "data": None,
            "session_id": sid,
            "errors": []
        })

@chat_bp.route("/health/llm", methods=["GET"])
@jwt_required()
def llm_health():
        return {"ok": health_check()}

@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():

    user_id = get_jwt_identity()

    trips = TripHistory.query.filter_by(
        user_id=user_id
    ).order_by(
        TripHistory.created_at.desc()
    ).all()

    history = []

    for t in trips:

        history.append({
            "id": t.id,
            "city": t.city,
            "budget": t.budget,
            "days": t.days,
            "people": t.people,
            "created_at": t.created_at,
            "itinerary": t.itinerary_json
        })

    return jsonify({
        "success": True,
        "history": history
    })