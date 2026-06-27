from langgraph.graph import StateGraph
from services.planning_engine import generate_itinerary


def build_graph():

    def validate(state):

        ctx = state["context"]

        required = ["budget", "days", "people", "city"]

        missing = [
            k for k in required
            if not ctx.get(k)
        ]

        if missing:
            state["error"] = (
                f"Missing fields: {', '.join(missing)}"
            )

        return state

    def plan(state):

        if state.get("error"):
            return state

        ctx = state["context"]

        result = generate_itinerary(
            budget=ctx["budget"],
            days=ctx["days"],
            people=ctx["people"],
            city=ctx["city"],
            preferences=ctx.get("preferences", [])
        )

        state["plan"] = result

        return state

    builder = StateGraph(dict)

    builder.add_node("validate", validate)
    builder.add_node("plan", plan)

    builder.set_entry_point("validate")

    builder.add_edge("validate", "plan")

    return builder.compile()