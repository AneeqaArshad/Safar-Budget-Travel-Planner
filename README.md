<div align="center">

# ✈️ Safar – AI-Powered Budget-Constrained Explainable Travel Planning System

### Intelligent Travel Planning using Rule-Based AI, Semantic Search, Explainable AI and Large Language Models

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange?style=for-the-badge)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-Embeddings-green?style=for-the-badge)
![JWT](https://img.shields.io/badge/JWT-Authentication-purple?style=for-the-badge)
![Ollama](https://img.shields.io/badge/Ollama-LLM-black?style=for-the-badge)

</p>

---

**Safar** is an intelligent travel planning system that generates **budget-aware, personalized, and explainable travel itineraries** through natural language conversations.

Unlike traditional travel planners, Safar combines **rule-based planning**, **semantic place retrieval**, and **optional Large Language Model explanations** to produce transparent travel recommendations that remain within the user's budget.

Designed as a Final Year Project, the system demonstrates modern AI engineering concepts including:

✨ Conversational AI

🧠 Explainable AI (XAI)

🔍 Semantic Search using Vector Embeddings

💰 Budget-Constrained Planning

🐳 Dockerized Deployment

🔐 JWT Authentication

---

# 🌟 Project Preview

The following screenshots illustrate the complete workflow of Safar, from user authentication and conversational trip planning to itinerary generation and budget visualization.

### Chat Planner

![Chat](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/chat.png)
---

### Generated Itinerary

![Itinerary](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/itinerary-overview.png)
---

### Budget Dashboard

![Budget Dashboard](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/budget-dashboard.png)
---

</div>

# 📌 Table of Contents

- Project Overview
- Features
- Screenshots
- Technology Stack
- System Architecture
- AI Planning Workflow
- Project Structure
- Installation
- Docker Deployment
- API Documentation
- Database Design
- Future Improvements
- Author

---

# 🌍 Project Overview

Planning a trip usually requires switching between multiple applications to compare attractions, estimate costs, organize schedules, and stay within budget.

**Safar** simplifies this process through a conversational interface.

Users simply describe their trip naturally, for example:

> "Plan a 2-day trip to Lahore for two people with a budget of Rs 20,000."

The system then:

- extracts important trip details,
- understands user preferences,
- retrieves relevant attractions,
- optimizes the itinerary,
- allocates the available budget,
- explains why each destination was selected,
- and presents everything in an easy-to-understand interface.

The project follows a modular AI architecture in which itinerary generation is performed using deterministic rule-based planning, 
while Large Language Models are used only to generate human-readable explanations. This separation ensures transparency, consistency, 
and explainability in every recommendation.

The planner follows a **rule-based decision engine**, ensuring that recommendations remain **deterministic, explainable, and budget-compliant** rather than relying solely on LLM-generated outputs.

---

# ✨ Features

### 🤖 AI Conversation Interface

- Natural language travel planning
- Multi-turn conversations
- Context-aware responses
- Session memory

---

### 💰 Budget-Constrained Planning

- Budget allocation
- Hotel estimation
- Food estimation
- Transport estimation
- Activity budgeting
- Remaining balance calculation

---

### 🧠 Explainable AI

Every itinerary includes an explanation describing:

- why attractions were selected
- how the budget was distributed
- how preferences influenced planning

---

### 🔍 Semantic Place Retrieval

Instead of matching only keywords,

Safar uses **Sentence Transformers** and **ChromaDB** to retrieve attractions based on semantic similarity.

Example:

```
User:
"I want historical places."

↓

System retrieves

Badshahi Mosque

Lahore Fort

Wazir Khan Mosque

instead of only exact keyword matches.
```

---

### 🛡 Authentication

- User Registration
- Login
- JWT Authentication
- Protected Routes
- Trip History

---

### 📅 Interactive Itinerary

Users can

- Generate itineraries
- Replace destinations
- Remove places
- Start new trips
- View previous trips

---

### 📊 Budget Dashboard

Automatic visualization of

- Hotel Cost
- Food Cost
- Transport Cost
- Activities Cost
- Remaining Budget
- Cost per Person

---

### 🐳 Dockerized Deployment

The complete application can be launched with a single command.

```bash
docker compose up --build
```

---

# 📸 Screenshots

## Authentication

### Create Account

![Signup](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/signup.png)
### Login

![Login](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/login.png)
---

## AI Chat Planner

![Chat](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/chat.png)

Natural language travel planning interface.

---

## Trip Confirmation

![Confirmation](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/confirmation.png)

User can review trip details before itinerary generation.

---

## Generated Itinerary

![Itinerary](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/itinerary-overview.png)

Overview of the generated trip.

---

## Day-wise Planning

![Day 1](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/day1.png)

![Day 2](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/day2.png)

Each day contains:

- attractions
- timing
- estimated cost
- rating
- category

---

## Budget Dashboard

![Budget Dashboard](https://raw.githubusercontent.com/AneeqaArshad/Safar-Budget-Travel-Planner/main/docs/Screenshots/budget-dashboard.png)

Detailed breakdown of travel expenses.

---

# 🛠 Technology Stack

| Category | Technologies |
|------------|--------------|
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite |
| ORM | SQLAlchemy |
| Authentication | Flask-JWT-Extended |
| Vector Database | ChromaDB |
| Embedding Model | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM Integration | Ollama |
| AI Framework | LangChain |
| Environment Management | python-dotenv |
| Containerization | Docker & Docker Compose |
| Version Control | Git & GitHub |

---
# 🏗️ System Architecture

Safar follows a modular architecture where each component is responsible for a single task.

```text
                    +----------------------+
                    |      Frontend        |
                    | HTML • CSS • JS      |
                    +----------+-----------+
                               |
                               |
                         REST API Requests
                               |
                               ▼
                    +----------------------+
                    |      Flask API       |
                    +----------+-----------+
                               |
          ------------------------------------------
          |                |               |
          ▼                ▼               ▼
 Authentication     Chat Controller    Itinerary API
 (JWT)              (Conversation)
          |                |
          |                ▼
          |        Intent Classification
          |                |
          |                ▼
          |        Entity Extraction
          |                |
          |                ▼
          |        Planning Engine
          |                |
          |        ------------------
          |        |                |
          |        ▼                ▼
          |   SQLite DB        ChromaDB
          |                    (Semantic Search)
          |                |
          |                ▼
          |       Explanation Generator
          |                |
          ------------------
                   |
                   ▼
            JSON Response
                   |
                   ▼
              User Interface
```

---

# 🧠 AI Planning Workflow

The following illustrates how Safar processes a user's request.

```text
User

↓

Natural Language Query

↓

Intent Classification

↓

Entity Extraction

↓

Conversation Memory Update

↓

Missing Information?

├── Yes → Ask User
│
└── No

↓

Budget Validation

↓

Planning Engine

↓

Semantic Search
(ChromaDB)

↓

Candidate Attractions

↓

Budget Optimization

↓

Hotel Allocation

↓

Food Allocation

↓

Transport Allocation

↓

Activity Selection

↓

Daily Schedule Generation

↓

Budget Breakdown

↓

LLM Explanation (Optional)

↓

Frontend Rendering
```

---

# 🤖 Explainable AI Pipeline

Unlike many chatbot-based planners, Safar separates **decision making** from **explanation generation**.

```
Planning Engine

↓

Generates itinerary

↓

Produces reasoning data

↓

Explanation Generator

↓

Large Language Model
(Optional)

↓

Natural Language Explanation
```

This architecture guarantees that:

- AI never decides the itinerary.
- The planning algorithm remains deterministic.
- LLMs are only used for explanation and natural language generation.

---

# 🔍 Semantic Search Pipeline

Safar uses embeddings instead of keyword matching.

```text
Place Dataset

↓

Sentence Transformers

↓

Vector Embeddings

↓

ChromaDB

↓

User Query

↓

Embedding

↓

Similarity Search

↓

Most Relevant Attractions

↓

Planning Engine
```

Example

```
User:

"I love historical places."

↓

Embedding Search

↓

Badshahi Mosque

↓

Lahore Fort

↓

Wazir Khan Mosque

↓

Planning Engine
```

This enables the planner to understand user intent even when the exact keywords are not present.

---

# ⚙️ Planning Engine

The planning engine is entirely rule-based.

Its responsibilities include:

- validating user budget
- estimating hotel expenses
- estimating food expenses
- estimating transportation expenses
- allocating remaining budget to attractions
- selecting attractions based on preferences
- preventing budget overflow
- distributing attractions across multiple days
- generating the final itinerary

The planner always ensures:

✔ Budget is never exceeded

✔ Daily activities remain realistic

✔ User preferences are prioritized

✔ Higher-rated attractions receive preference

---

# 💰 Budget Allocation Strategy

The planner first reserves mandatory expenses.

```
Total Budget

↓

Hotel Cost

↓

Food Cost

↓

Transport Cost

↓

Remaining Budget

↓

Activities
```

Only attractions that fit inside the remaining activity budget are selected.

This guarantees that generated itineraries remain financially feasible.

---

# 🗂️ Project Structure

```
Safar-Budget-Travel-Planner
│
├── backend
│   ├── app.py
│   ├── config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   ├── models
│   │   ├── user.py
│   │   ├── city.py
│   │   ├── place.py
│   │   └── trip_history.py
│   │
│   ├── routes
│   │   ├── auth_routes.py
│   │   ├── chat.py
│   │   └── itinerary.py
│   │
│   ├── services
│   │   ├── planning_engine.py
│   │   ├── place_retriever.py
│   │   ├── explanation_generator.py
│   │   ├── intent_classifier.py
│   │   ├── entity_extractor.py
│   │   ├── llm.py
│   │   └── conversation_manager.py
│   │
│   ├── utils
│   ├── scripts
│   ├── chroma_db
│   └── instance
│
├── frontend
│   ├── templates
│   ├── static
│   │   ├── css
│   │   ├── js
│   │   └── images
│
├── docker-compose.yml
├── README.md
└── docs
    └── screenshots
```

---

# 📂 Major Components

| Component | Purpose |
|------------|---------|
| Chat Planner | Conversational trip planning |
| Intent Classifier | Detects user intent |
| Entity Extractor | Extracts city, days, budget and preferences |
| Planning Engine | Generates budget-aware itinerary |
| ChromaDB | Semantic attraction retrieval |
| Explanation Generator | Produces explainable summaries |
| SQLite | Stores users, trips and attractions |
| JWT Authentication | Secure login and signup |
| Docker | One-command deployment |

---

# 🚀 Key Highlights

- Rule-Based AI Planning
- Explainable AI
- Semantic Search
- Vector Database
- Dockerized Deployment
- JWT Authentication
- Budget-Constrained Optimization
- Personalized Recommendations
- Modern Responsive UI
- Modular Flask Architecture

---

# 📈 Future Improvements

The following enhancements are planned for future versions:

- Google Maps integration
- Weather-aware itinerary generation
- Hotel booking APIs
- Flight integration
- Route optimization
- Collaborative trip planning
- Recommendation learning from user feedback
- Multi-language support
- Real-time traffic estimation
- Mobile application

---
# 🚀 Installation

## Clone the repository

```bash
https://github.com/AneeqaArshad/Safar-Budget-Travel-Planner.git
cd Safar-Budget-Travel-Planner
```

---

## Method 1 — Run with Docker (Recommended)

### Build the containers

```bash
docker compose up --build
```

After the first build:

```bash
docker compose up
```

Open:

```
http://127.0.0.1:5000
```

---

## Method 2 — Local Development

### Navigate to backend

```bash
cd backend
```

Create a virtual environment

```bash
python -m venv venv
```

Activate

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

# 🔐 Environment Variables

Create a `.env` file inside the **backend** directory.

```env
SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_secret

DATABASE_URL=sqlite:///travel_planner.db

OLLAMA_URL=http://host.docker.internal:11434

ANTHROPIC_API_KEY=your_api_key
```

> The planner works without an Anthropic API key. When no API key is provided, the application falls back to built-in explanation templates.

---

# 🐳 Docker Support

Safar is fully containerized using Docker.

Included configuration files:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The Dockerized application automatically:

- installs dependencies
- starts Flask
- mounts persistent volumes
- preserves SQLite database
- preserves ChromaDB vector database

---

# 📡 REST API

## Authentication

### Register

```
POST /api/auth/signup
```

Example

```json
{
    "username":"john",
    "email":"john@example.com",
    "password":"password123"
}
```

---

### Login

```
POST /api/auth/login
```

Returns:

```text
JWT Access Token
```

The access token is used to authenticate subsequent API requests.

---

## Chat

```
POST /api/chat/message
```

Example

```json
{
    "message":"Plan a 2 day trip to Lahore with a budget of 20000."
}
```

---

## Available Cities

```
GET /api/itinerary/cities
```

---

## Places

```
GET /api/itinerary/places
```

---

# 💾 Database Design

Safar uses **SQLite** with **SQLAlchemy ORM**.

Main tables:

- Users
- Cities
- Places
- Trip History

Relationships

```
City

│

├── Place

│

User

│

└── TripHistory
```

---

# 🧪 Running Tests

```bash
pytest
```

or

```bash
pytest tests/
```

---

# 🛠️ Technologies Used

### Backend

- Python
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- SQLite

### AI

- Sentence Transformers
- ChromaDB
- Ollama
- TinyLlama
- Anthropic Claude (Optional)

### Frontend

- HTML5
- CSS3
- JavaScript

### Deployment & DevOps

- Docker
- Docker Compose

---

# 🎯 Learning Outcomes

This project demonstrates practical implementation of:

- Explainable Artificial Intelligence
- Rule-Based Decision Systems
- Semantic Search
- Vector Embeddings using Sentence Transformers
- Retrieval-Augmented Recommendation
- Vector Databases
- RESTful API Development
- Authentication using JWT
- Docker Containerization
- Database Design
- Software Engineering Principles

---

# 👨‍💻 Author

**Aniqa Arshad**

Final Year Project

Bachelor of Computer Science

---

# 🙏 Acknowledgements

Special thanks to:

- Faculty Supervisor
- OpenAI
- Anthropic
- Hugging Face
- ChromaDB
- Flask Community

---

# 📄 License

This project is intended for educational and research purposes.

---

# ⭐ If you found this project interesting, consider giving it a star.