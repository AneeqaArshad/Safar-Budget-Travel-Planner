# Safar — Complete Project Analysis
### Agent-Based Budget-Constrained Explainable Travel Planning System

---

## 1. PROJECT OVERVIEW

### What This Website Does

Safar is a **conversational travel planning web application** for Pakistan. Users chat naturally with it — like texting a friend — and the system generates a complete, day-by-day travel itinerary that **strictly fits their budget**. Every recommendation comes with a clear, human-readable explanation of *why* that place was chosen.

### Main Features

- **Chat interface** — users type naturally ("Plan a 2-day trip to Lahore for Rs 15,000")
- **Budget enforcement** — the planning engine mathematically guarantees the total never exceeds budget
- **Smart budget splitting** — automatically divides budget into hotel, food, transport, and activities
- **Day-wise itinerary** — places are scheduled across days respecting time limits (8h/day max)
- **Per-place explanations** — every attraction shows exactly why it was picked (free entry, high rating, matches preference, hidden gem, etc.)
- **Budget breakdown panel** — animated bar charts and table showing all cost categories
- **Preference filtering** — users can request nature, historical, food, shopping, or hidden gem places
- **Session memory** — the system remembers your budget/city/days across multiple chat messages
- **LLM narration** — optionally uses Anthropic Claude to write a warm conversational summary

### Tech Stack

| Layer | Technology | Why Used |
|---|---|---|
| Frontend UI | HTML5, CSS3, Vanilla JavaScript | No framework needed for this scope |
| Fonts | DM Serif Display + DM Sans (Google Fonts) | Professional editorial aesthetic |
| Backend Framework | Python 3.12 + Flask 3.0 | Lightweight, Python-native, easy routing |
| ORM | SQLAlchemy (via Flask-SQLAlchemy) | Database-agnostic, clean model definitions |
| Database | SQLite (dev) / PostgreSQL (production) | SQLite = zero config for development |
| CORS | Flask-CORS | Allows frontend to call backend API |
| NLP (optional) | Anthropic Claude API (claude-haiku) | Explanation text generation ONLY |
| Session State | In-memory Python dict | Simple, fast for single-server use |
| Data Seeding | Hardcoded Python + sample_data.json | 23 places across 3 cities, auto-seeded |

---

## 2. PROJECT STRUCTURE

```
travel_planner/
│
├── README.md                         ← Setup and API documentation
├── PROJECT_ANALYSIS.md               ← This file
│
├── backend/                          ← All Python server code
│   ├── app.py                        ← Entry point: creates Flask app, seeds DB
│   ├── config.py                     ← All settings (budget ratios, tiers, keys)
│   ├── requirements.txt              ← Python package dependencies
│   ├── sample_data.json              ← 23 places across 3 cities (JSON format)
│   ├── db_utils.py                   ← CLI tool: seed/export/reset/schema
│   │
│   ├── models/                       ← Database table definitions
│   │   ├── __init__.py               ← Re-exports db, City, Place
│   │   ├── database.py               ← Creates the shared db = SQLAlchemy() instance
│   │   ├── city.py                   ← City table (id, name)
│   │   └── place.py                  ← Places table (id, name, city_id, category, cost, ...)
│   │
│   ├── routes/                       ← URL endpoint handlers
│   │   ├── __init__.py               ← Re-exports blueprints
│   │   ├── chat.py                   ← POST /api/chat/message and /api/chat/reset
│   │   └── itinerary.py              ← GET /api/itinerary/cities and /places
│   │
│   ├── services/                     ← Core business logic (the "brain")
│   │   ├── __init__.py               ← Re-exports all service functions
│   │   ├── intent_classifier.py      ← Detects WHAT the user wants (9 intent types)
│   │   ├── entity_extractor.py       ← Pulls numbers/names from text (budget, days, etc.)
│   │   ├── planning_engine.py        ← RULE-BASED itinerary generator (most important)
│   │   └── explanation_generator.py  ← LLM wrapper + template fallback
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── session_store.py          ← In-memory dict storing per-user conversation state
│   │
│   └── tests/
│       └── test_services.py          ← 25 unit tests for all core logic
│
└── frontend/                         ← All browser code
    ├── templates/
    │   └── index.html                ← Single HTML page (all 3 panels live here)
    └── static/
        ├── css/
        │   └── style.css             ← All styles, layout, animations, responsive rules
        └── js/
            └── app.js                ← All interactivity: chat, API calls, rendering
```

### How Files Connect to Each Other

```
app.py
  ├── imports config.py          (gets settings)
  ├── imports models/database.py (gets SQLAlchemy instance)
  ├── imports routes/chat.py     (registers /api/chat/* endpoints)
  ├── imports routes/itinerary.py(registers /api/itinerary/* endpoints)
  └── serves frontend/templates/index.html at "/"

routes/chat.py
  ├── imports services/intent_classifier.py
  ├── imports services/entity_extractor.py
  ├── imports services/planning_engine.py
  ├── imports services/explanation_generator.py
  └── imports utils/session_store.py

services/planning_engine.py
  ├── imports models/place.py    (queries places from DB)
  └── imports models/city.py     (validates city name)

frontend/index.html
  ├── loads static/css/style.css
  └── loads static/js/app.js

frontend/js/app.js
  └── calls backend via fetch('/api/chat/message', ...)
```

---

## 3. FRONTEND EXPLANATION

### Layout: Three Panels in One Page

The entire UI is a single HTML page (`index.html`) with three panels that swap visibility. There are no page reloads. Everything is controlled by JavaScript.

```
┌─────────────────────────────────────────────────────┐
│  SIDEBAR (dark)          │  TOP BAR                 │
│  ✦ safar                 │  ☰  ✦ safar  [status]   │
│  ─────────────           ├──────────────────────────┤
│  💬 Chat Planner  ← active│                          │
│  📋 My Itinerary          │   ACTIVE PANEL           │
│  📊 Budget Breakdown      │   (Chat / Itinerary /    │
│  ─────────────           │    Budget)               │
│  Current trip:           │                          │
│  🏙️ City: Lahore         │                          │
│  💰 Budget: Rs 20,000    │                          │
│  📅 Days: 2              │                          │
│  👥 People: 2            │                          │
│  ─────────────           │                          │
│  [↺ New Trip]            │                          │
└─────────────────────────────────────────────────────┘
```

### Panel 1: Chat Interface (`#panelChat`)

The main interaction screen. Contains:

- **Chat window** (`#chatWindow`) — scrollable div where messages appear. Bot messages have a `✦` avatar on the left; user messages are right-aligned in dark bubbles.
- **Welcome message** with three clickable hint chips (pre-filled example queries)
- **Typing indicator** — three animated dots appear while waiting for the server
- **Input bar** — auto-growing textarea (max height 130px), send button, keyboard shortcut hint

### Panel 2: Itinerary Display (`#panelItinerary`)

Populated automatically after a plan is generated. Contains:

- **AI Summary banner** — green gradient box with the LLM explanation text
- **Warning boxes** — amber boxes if budget was too tight to afford preferred hotel tier
- **Day cards** — one card per day, dark header showing day number and daily stats
  - Each card contains **place items** with: name, cost badge (green "Free" or pink "Rs X"), category/hidden tags, description, rating, time required, best visiting time, and the rule-based explanation in an indented green block

### Panel 3: Budget Breakdown (`#panelBudget`)

Populated alongside the itinerary. Contains:

- **4 summary metric cards** — Total Budget, Total Spent, Leftover, Per Person/Day
- **4 animated progress bars** — Accommodation, Food, Transport, Activities (bars animate from 0 to their real width on load)
- **Detailed cost table** — line-by-line breakdown with hotel/food tier labels and per-unit costs

### User Interactions

| Action | What Happens |
|---|---|
| Type message + Enter | `sendMessage()` called → POST to `/api/chat/message` |
| Click hint chip | `window.sendHint(text)` → same as typing that message |
| Click nav button | `switchToPanel(name)` shows/hides panels |
| Click ☰ (mobile) | `openSidebar()` slides sidebar in over content |
| Click ↺ New Trip | POST to `/api/chat/reset`, clears all state and UI |
| Itinerary received | Auto-switches to Itinerary panel after 1.2 second delay |

### How Frontend Talks to Backend

All communication is via `fetch()` — plain HTTP requests with JSON bodies. No forms, no page reloads.

```javascript
// Sending a message
fetch('/api/chat/message', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Plan my trip",
    session_id: state.sessionId   // null on first message
  })
})
.then(res => res.json())
.then(data => {
  // data.reply  → bot message text
  // data.itinerary → full plan (or null)
  // data.session_id → ID to use for next message
});
```

The `session_id` is returned by the server on the first message and stored in `state.sessionId`. Every subsequent message includes it so the server knows which user's constraints to recall.

---

## 4. BACKEND EXPLANATION

### Flask Application Structure

Flask uses the **Application Factory pattern** — `create_app()` in `app.py` builds and configures the entire application. This makes testing easier and allows different configs for dev/production.

```python
def create_app(config_class=Config):
    app = Flask(...)
    app.config.from_object(config_class)   # loads config.py settings
    db.init_app(app)                        # connects SQLAlchemy
    CORS(app)                               # allows cross-origin requests
    app.register_blueprint(chat_bp, ...)   # registers /api/chat/* routes
    app.register_blueprint(itinerary_bp, ...)  # registers /api/itinerary/* routes
    return app
```

### All API Endpoints

| Method | URL | File | Purpose |
|---|---|---|---|
| GET | `/` | `app.py` | Serves the frontend HTML page |
| POST | `/api/chat/message` | `routes/chat.py` | Main conversational endpoint |
| POST | `/api/chat/reset` | `routes/chat.py` | Clears session, starts fresh |
| GET | `/api/itinerary/cities` | `routes/itinerary.py` | Returns all cities |
| GET | `/api/itinerary/places` | `routes/itinerary.py` | Returns places (filterable) |
| GET | `/api/itinerary/places/<id>` | `routes/itinerary.py` | Returns one place by ID |

### How `/api/chat/message` Works (The Core Endpoint)

This single endpoint does the work of an entire NLP pipeline:

```
Receive JSON { message, session_id }
       ↓
Step 1: classify_intent(message)
        → returns "PLAN_REQUEST", "SET_BUDGET", "GREETING", etc.
       ↓
Step 2: extract_all_entities(message)
        → returns { budget: 20000, days: 2, city: "Lahore", ... }
       ↓
Step 3: update_session(session_id, entities)
        → merges extracted values into the user's stored context
       ↓
Step 4: Route by intent:
    if EXPLANATION_REQUEST → call generate_explanation(last_itinerary)
    if PLAN_REQUEST:
        if missing fields → ask user for them
        else → generate_itinerary(budget, days, people, city, prefs)
               → generate_explanation(result)
               → return full itinerary JSON
    else → generate_conversational_reply(intent, missing, context)
       ↓
Return JSON { reply, intent, itinerary, session_id }
```

### The Four Service Modules

**1. `intent_classifier.py` — What does the user want?**

Uses keyword matching against 8 predefined keyword lists. Checks in priority order (PLAN > EXPLAIN > GREETING > budget/days/city/etc.). Returns one of 9 string constants.

```python
text = "plan a trip to lahore"
→ "plan" is in PLAN_KEYWORDS → returns "PLAN_REQUEST"
```

**2. `entity_extractor.py` — What specific values did they give?**

Uses Python `re` (regex) to pull numbers and names from raw text. Five separate extractors for budget, days, people, city, and preferences.

```python
extract_budget("My budget is 50k")  → 50000
extract_days("for 3 nights")        → 3
extract_people("family of 4")       → 4
extract_city("trip to islamabad")   → "Islamabad"
```

**3. `planning_engine.py` — The most important file.**

Pure rule-based algorithm. No AI involved. Steps:
1. Divide total budget by number of people → `budget_per_person`
2. Match budget_per_person against hotel tier thresholds → pick hotel type
3. Same for food tier
4. Compute: `activity_budget = total - hotel_cost - food_cost - transport_cost`
5. Query database for all places in that city that cost ≤ activity_budget
6. Sort places by: rating DESC, then cost ASC (best value first)
7. Loop over days, greedily assign places respecting: budget, 8h daily limit, 4 places/day max, no repeats
8. For each assigned place, call `_explain_place_selection()` which generates a rule-based reason string

**4. `explanation_generator.py` — Make it sound friendly.**

Two paths:
- If `ANTHROPIC_API_KEY` is set: sends the finalized plan to Claude API with a strict prompt that says "explain this plan, do NOT change it". Gets back a warm paragraph.
- If no API key: uses a Python f-string template that fills in all the numbers automatically.

The LLM **never sees the database, never picks places, never touches the budget logic**. It only writes a paragraph summarizing what the rule engine already decided.

---

## 5. DATA FLOW

### Scenario A: User Visits the Website

```
Browser opens http://localhost:5000
       ↓
Flask receives GET /
       ↓
app.py → render_template("index.html")
       ↓
Browser downloads index.html
Browser downloads /static/css/style.css
Browser downloads /static/js/app.js
       ↓
JavaScript runs: DOM elements are grabbed, event listeners attached
Welcome message is shown with 3 hint chip buttons
state.sessionId = null (no session yet)
```

### Scenario B: User Sends a Message (e.g., "My budget is 15000")

```
User types "My budget is 15000" → presses Enter
       ↓
app.js: sendMessage() called
  → user's message appended to chat window (right-aligned dark bubble)
  → typing indicator (3 animated dots) appears
  → fetch POST /api/chat/message
     body: { message: "My budget is 15000", session_id: null }
       ↓
routes/chat.py: handle_message()
  Step 1: classify_intent("my budget is 15000")
          → "budget" in BUDGET_KEYWORDS → returns "SET_BUDGET"
  Step 2: extract_all_entities("my budget is 15000")
          → { budget: 15000, days: null, people: null, city: null, preferences: [] }
  Step 3: update_session(new_uuid, { budget: 15000 })
          → session["budget"] = 15000
  Step 4: intent = "SET_BUDGET" (not PLAN_REQUEST or EXPLANATION_REQUEST)
          → missing = ["days", "people", "city"]
          → reply = "Got it! I've noted your budget of Rs 15,000. 
                     Now, which city would you like to visit?"
       ↓
Response: { reply: "Got it! ...", intent: "SET_BUDGET",
            itinerary: null, session_id: "abc-123" }
       ↓
app.js:
  → typing indicator removed
  → bot reply appended to chat window
  → state.sessionId = "abc-123"  (saved for next message)
  → no itinerary → panels not updated
```

### Scenario C: User Says "Plan My Trip" (All Fields Already Set)

```
User types "Plan my trip"
       ↓
fetch POST /api/chat/message
  body: { message: "Plan my trip", session_id: "abc-123" }
       ↓
classify_intent → "PLAN_REQUEST"
extract_all_entities → all nulls (no new info in this message)
update_session → nothing changes
get_session("abc-123") → { budget:15000, days:2, city:"Lahore", people:2 }
get_missing_fields → [] (nothing missing!)
       ↓
generate_itinerary(budget=15000, days=2, people=2, city="Lahore")
  budget_per_person = 7500
  hotel_tier = "Budget guesthouse" (Rs 1500/person/night)
  food_tier  = "Local restaurants" (Rs 800/person/day)
  hotel_cost = 1500 × 2 × 2 = Rs 6,000
  food_cost  = 800  × 2 × 2 = Rs 6,400
  transport  = 500  × 2 × 2 = Rs 2,000
  fixed = 14,400
  activity_budget = 15000 - 14400 = Rs 600

  Query: Place WHERE city_id=1 AND cost <= 600
  → Badshahi Mosque (cost=0, rating=4.9) ✓
  → Wazir Khan Mosque (cost=0, rating=4.8) ✓
  → Chauburji (cost=0, rating=4.3) ✓
  → Lahore Museum (cost=200, rating=4.5) ✓
  → Lahore Fort (cost=500 > 600? No) ✗
  
  Day 1: Assign Badshahi (4.9★, free, 2h), Wazir Khan (4.8★, free, 1h),
          Museum (4.5★, Rs200, 2h), Chauburji (4.3★, free, 1h) → 6h total ✓
  Day 2: No unvisited affordable places left → empty day (warning shown)

  budget_breakdown = { total: 15000, hotel: 6000, food: 6400,
                       transport: 2000, activities: { spent: 200 },
                       leftover: 400 }
       ↓
generate_explanation(result) → "Your 2-day trip to Lahore..."
result["ai_explanation"] = explanation
       ↓
Response: { reply: "Your 2-day trip...",
            itinerary: { days: [...], budget_breakdown: {...} },
            session_id: "abc-123" }
       ↓
app.js:
  → bot message appended
  → renderItinerary(data.itinerary) → builds day cards HTML
  → renderBudget(data.itinerary) → builds bar charts and table
  → updateContextPills(data.itinerary) → updates sidebar pills
  → setTimeout → switches to Itinerary panel after 1.2s
```

---

## 6. DATABASE & API INTEGRATION

### Database (SQLite / PostgreSQL via SQLAlchemy)

Two tables, connected by a foreign key:

```
cities                          places
──────────────────              ─────────────────────────────────────────────
id  │ name                      id │ name             │ city_id │ category │ cost │ ...
────┼──────────                 ───┼──────────────────┼─────────┼──────────┼──────┼────
 1  │ Lahore                      1 │ Badshahi Mosque  │    1    │historical│   0  │ ...
 2  │ Islamabad                   2 │ Lahore Fort      │    1    │historical│ 500  │ ...
 3  │ Murree                      9 │ Faisal Mosque    │    2    │historical│   0  │ ...
                                  17 │ Mall Road Murree │    3    │ shopping │ 500  │ ...
```

The database is **auto-created and auto-seeded** on first run. `app.py` calls `db.create_all()` (creates tables) and `_seed_sample_data()` (inserts 3 cities + 23 places) inside `create_app()`.

To use PostgreSQL instead of SQLite, just set the environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost/travel_planner"
```
The models work identically — SQLAlchemy handles the dialect difference.

### External API (Anthropic Claude — Optional)

Used ONLY in `services/explanation_generator.py`. The call pattern:
```python
client = anthropic.Anthropic(api_key=api_key)
message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[{"role": "user", "content": prompt}]
)
return message.content[0].text.strip()
```

The prompt explicitly tells the model: "explain this plan, do NOT suggest changes." This ensures AI is used purely for communication, not decision-making. If the API call fails for any reason, `_fallback_explanation()` fills in a template string instead — the system never breaks.

No other external APIs are used. No maps API, no booking API, no weather API (these are listed in Section 10 as improvement opportunities).

---

## 7. CONFIGURATION & ENVIRONMENT

### `config.py` — All Tunable Settings

```python
class Config:
    SECRET_KEY = "..."                    # Flask session encryption key
    SQLALCHEMY_DATABASE_URI = "sqlite:///travel_planner.db"  # DB file location
    ANTHROPIC_API_KEY = ""               # Set via environment variable
    HOTEL_BUDGET_RATIO = 0.45            # Hotel gets 45% of budget (informational)
    FOOD_BUDGET_RATIO = 0.30             # Food gets 30% (informational)
    ACTIVITY_BUDGET_RATIO = 0.25         # Activities get 25% (informational)
    MAX_PLACES_PER_DAY = 4               # Max attractions scheduled per day
    DEBUG = True                         # Enable Flask debug mode
```

The ratios at the bottom are defined here but the actual allocation happens via the tier system in `planning_engine.py`. They serve as documentation.

### `requirements.txt` — Python Dependencies

```
flask==3.0.3           # Web framework
flask-sqlalchemy==3.1.1 # ORM integration for Flask
flask-cors==4.0.1       # Allow cross-origin API requests
sqlalchemy==2.0.30      # Database ORM
anthropic==0.25.0       # Claude API client (only needed if using LLM)
python-dotenv==1.0.1    # Load .env files (optional but recommended)
gunicorn==22.0.0        # Production WSGI server (for deployment)
```

### Environment Variables

| Variable | Where Used | Default | Required? |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | `config.py` → `explanation_generator.py` | `""` | No (fallback works) |
| `DATABASE_URL` | `config.py` | `sqlite:///travel_planner.db` | No (SQLite default) |
| `SECRET_KEY` | `config.py` | hardcoded dev key | No (change for production) |
| `FLASK_DEBUG` | `config.py` | `"True"` | No |

### Recommended `.env` file (not currently in project — add this)

```bash
# Create: backend/.env
ANTHROPIC_API_KEY=sk-ant-your-key-here
DATABASE_URL=sqlite:///travel_planner.db
SECRET_KEY=your-random-secret-key-here
FLASK_DEBUG=True
```

Then add this to the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 8. CODE RELATIONSHIPS

### The Complete Request-Response Flow

```
BROWSER                        FLASK SERVER                      DATABASE
───────                        ────────────                      ────────
User types message
    │
    │  POST /api/chat/message
    │  { message, session_id }
    ├─────────────────────────►  routes/chat.py
    │                             │
    │                             ├─► intent_classifier.py
    │                             │     keyword matching
    │                             │     returns "PLAN_REQUEST"
    │                             │
    │                             ├─► entity_extractor.py
    │                             │     regex extraction
    │                             │     returns { budget, days... }
    │                             │
    │                             ├─► session_store.py
    │                             │     merges entities into dict
    │                             │
    │                             ├─► planning_engine.py
    │                             │     ├─────────────────────────► City.query
    │                             │     │                         ◄─ City object
    │                             │     ├─────────────────────────► Place.query
    │                             │     │                         ◄─ Place list
    │                             │     └─ generates itinerary dict
    │                             │
    │                             └─► explanation_generator.py
    │                                   ├─ Anthropic API (if key set)
    │                                   └─ or: template string
    │
    │  { reply, itinerary, session_id }
    │◄─────────────────────────────────
    │
    ├─► appendMessage(reply, 'bot')
    ├─► renderItinerary(itinerary)
    ├─► renderBudget(itinerary)
    └─► switchToPanel('itinerary')
```

### Which File Calls Which

```
app.py
  └── creates app, registers blueprints, seeds DB

routes/chat.py        (orchestrator)
  ├── calls: intent_classifier.classify_intent()
  ├── calls: entity_extractor.extract_all_entities()
  ├── calls: session_store.update_session()
  ├── calls: planning_engine.generate_itinerary()
  └── calls: explanation_generator.generate_explanation()

services/planning_engine.py  (core brain)
  ├── queries: models/city.py → City.query
  └── queries: models/place.py → Place.query

services/explanation_generator.py
  └── calls: anthropic Python SDK (external)

frontend/app.js
  ├── calls: POST /api/chat/message
  ├── calls: POST /api/chat/reset
  ├── renders: itinerary HTML dynamically
  └── renders: budget charts dynamically
```

---

## 9. WHERE TO MAKE CHANGES

### UI Design Changes → `frontend/static/css/style.css`

| What to Change | CSS Section to Edit |
|---|---|
| Color palette | Lines 1–25: `:root { --cream, --sage, --blush... }` |
| Fonts | Change Google Fonts link in `index.html` + `--serif`/`--sans` vars |
| Sidebar width | `--sidebar-w: 260px` in `:root` |
| Chat bubble colors | `.msg-bubble` and `.msg-user .msg-bubble` |
| Day card styling | `.day-card`, `.day-header`, `.place-item` |
| Budget bar colors | `renderBudget()` in `app.js` — the `bars` array with `accent` colors |
| Mobile breakpoint | `@media (max-width: 768px)` at bottom of CSS |
| Button styles | `.send-btn`, `.hint-chip`, `.nav-btn`, `.reset-btn` |

### Adding New HTML Components → `frontend/templates/index.html`

To add a new panel (e.g., "Saved Trips"):
1. Add nav button: `<button class="nav-btn" data-panel="saved">💾 Saved Trips</button>`
2. Add panel: `<section class="panel" id="panelSaved">...</section>`
3. The existing `navBtns.forEach(...)` in `app.js` will handle it automatically

### Adding New Features → Multiple Files

**New city (e.g., Karachi):**
- `app.py` → add `karachi = City(name="Karachi")` and places in `_seed_sample_data()`
- `services/intent_classifier.py` → add `"karachi"` to `CITY_KEYWORDS`
- `services/entity_extractor.py` → add `"karachi": "Karachi"` to `CITY_ALIASES`

**New preference category (e.g., "adventure"):**
- `services/entity_extractor.py` → add to `PREFERENCE_MAP`: `"trekking": "adventure"`
- `services/planning_engine.py` → ensure the Place.category value matches

**Change max places per day:**
- `config.py` → `MAX_PLACES_PER_DAY = 5` (currently 4)

**Change hotel/food tier costs:**
- `services/planning_engine.py` → edit `HOTEL_TIERS` and `FOOD_TIERS` lists at the top

### Changing Business Logic → `services/planning_engine.py`

| What to Change | Where in File |
|---|---|
| How budget is split between hotel/food/activities | `HOTEL_TIERS`, `FOOD_TIERS`, `TRANSPORT_COST_PER_PERSON_DAY` |
| Which places get prioritized | `_filter_and_sort_places()` — change the sort key |
| Why a place is selected (explanation text) | `_explain_place_selection()` |
| Daily time budget | `max_hours_per_day = 8` in `generate_itinerary()` |
| How budget fallback works when too tight | The two `if activity_budget < 0` blocks |

### Updating API Integrations → `services/explanation_generator.py`

- Change LLM model: edit `model="claude-haiku-4-5-20251001"`
- Change explanation tone/length: edit the `_build_prompt()` function
- Switch to OpenAI: replace `anthropic.Anthropic(...)` with `openai.OpenAI(...)` and adjust the call format
- Change fallback text: edit `_fallback_explanation()`

### Changing Routes/Endpoints → `routes/` folder

- Add new endpoint: add `@chat_bp.route("/new-endpoint", methods=["GET"])` to `chat.py`
- Add place filtering: extend `routes/itinerary.py` with more query parameters

---

## 10. IMPROVEMENT SUGGESTIONS

### Performance

| Issue | Current | Recommended Fix |
|---|---|---|
| Session storage | In-memory Python dict | Use Redis (production-safe, survives restarts) |
| Database | SQLite (single-file, no concurrency) | Switch to PostgreSQL for >1 concurrent user |
| No caching | Every plan recalculates | Cache itineraries by (budget,days,people,city) key |
| No pagination | All places loaded at once | Add LIMIT/OFFSET for large datasets |

### UI/UX

- **Add a map view** — integrate Leaflet.js (free) to show place locations on an interactive map
- **Add print/export** — "Download as PDF" button using browser `window.print()` with print CSS
- **Add itinerary sharing** — generate a short URL users can copy and share
- **Add trip comparison** — show two itineraries side-by-side (e.g., Lahore vs Islamabad same budget)
- **Add image thumbnails** — attach a small photo URL to each place in the database and display it
- **Loading skeleton** — show placeholder grey boxes while itinerary is loading instead of just typing dots
- **Dark mode toggle** — the CSS variables make this easy to add with a single class on `<body>`

### Backend / Logic

- **Multi-city trips** — allow Lahore + Murree in the same itinerary
- **Persistent sessions** — use Flask-Session with a database backend so conversations survive server restarts
- **User accounts** — add Flask-Login so users can save and revisit past itineraries
- **Smarter scheduling** — consider geographic proximity when ordering places within a day
- **Transport mode** — let users specify car vs. public transport (affects transport cost tier)
- **Real pricing** — integrate a web scraping service or partner API for live hotel prices

### Advanced AI Features (Recommended for Phase 2)

- **Semantic intent classifier** — replace keyword matching with a small BERT/sentence-transformer model for better understanding of complex sentences like "something relaxing but not too pricey for my wife's birthday"
- **Named entity recognition** — replace regex with spaCy NER for more robust budget/date extraction
- **Conversational memory** — store full chat history per session and send it to the LLM for context-aware follow-up answers
- **Personalization** — build a user profile system that remembers past preferences and biases future recommendations
- **Dynamic pricing** — use an LLM with web search to fetch real current entry fees for places
- **Photo generation** — use DALL-E or Stable Diffusion to generate preview images for each place

### Security (Important Before Public Deployment)

- Set a real `SECRET_KEY` (random 32+ character string, never commit it)
- Add rate limiting on `/api/chat/message` to prevent abuse (use Flask-Limiter)
- Add input sanitization (current `escapeHtml()` in JS is good, but also validate on server)
- Move API key to `.env` and never hardcode it
- Add HTTPS (automatic if deploying to Railway, Render, or Heroku)

---

## 11. DEPLOYMENT & RUNNING

### Run Locally (Development)

```bash
# 1. Navigate to backend
cd travel_planner/backend

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set API key for LLM explanations
export ANTHROPIC_API_KEY="sk-ant-your-key"

# 5. Run
python app.py

# Output:
# ✅ Sample data seeded successfully.
# * Running on http://0.0.0.0:5000
```

Open: **http://localhost:5000**

The SQLite database file (`travel_planner.db`) is auto-created in the backend directory on first run. To reset it: `python db_utils.py reset`

### Database Management Commands

```bash
python db_utils.py seed    # Re-import from sample_data.json
python db_utils.py export  # Save current DB to export.json
python db_utils.py reset   # Drop all tables and recreate
python db_utils.py schema  # Print table structure
```

### Run Tests

```bash
cd travel_planner/backend
python -m pytest tests/ -v

# Expected output: 25 tests passing
# Tests cover: intent classifier, entity extractor, planning engine
```

### Deploy to Railway (Easiest Cloud Option)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and create project
railway login
railway init

# 3. Set environment variables in Railway dashboard:
#    ANTHROPIC_API_KEY = your-key
#    DATABASE_URL = postgresql://... (Railway provides this)
#    SECRET_KEY = your-random-secret

# 4. Deploy
railway up
```

### Deploy to Render (Free Tier Available)

1. Push code to GitHub
2. Go to render.com → New Web Service → Connect repo
3. Set:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && gunicorn app:create_app()`
4. Add environment variables in Render dashboard
5. Done — auto-deploys on every Git push

### Deploy to Heroku

```bash
# Create Procfile in project root:
echo "web: cd backend && gunicorn 'app:create_app()'" > Procfile

heroku create safar-travel-planner
heroku config:set ANTHROPIC_API_KEY=your-key
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku open
```

### Docker (Optional)

```dockerfile
# Dockerfile (create in backend/)
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t safar-planner .
docker run -p 5000:5000 -e ANTHROPIC_API_KEY=your-key safar-planner
```

---

## QUICK REFERENCE CARD

```
┌─────────────────────────────────────────────────────────────────┐
│  FILE              │ WHAT TO CHANGE                             │
├────────────────────┼────────────────────────────────────────────┤
│ config.py          │ Budget ratios, max places, hotel/food tiers │
│ planning_engine.py │ Core algorithm, tiers, sorting, scheduling │
│ intent_classifier  │ Keywords, new intents                      │
│ entity_extractor   │ New cities, regex patterns, preferences    │
│ explanation_gen.   │ LLM model, prompt, fallback text           │
│ session_store.py   │ Session fields, storage backend            │
│ routes/chat.py     │ New endpoints, routing logic               │
│ app.py             │ New cities/places in seed data             │
│ style.css          │ Colors, fonts, layout, animations          │
│ index.html         │ New panels, HTML structure                 │
│ app.js             │ UI logic, rendering, API calls             │
└────────────────────┴────────────────────────────────────────────┘
```
