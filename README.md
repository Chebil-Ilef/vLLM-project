# 🧠 BIAssistant – AI-Powered Business Intelligence Chatbot

BIAssistant is an AI-powered assistant designed to help *non-technical users* explore and analyze business data intuitively — simply by asking questions in natural language.  
Whether you're a business analyst, a product manager, or an executive with no BI background, BIAssistant can help you understand your data warehouse and extract valuable insights.

## Setup

Follow these steps to run the project locally or with Docker Compose.

### 1 Prerequisites

- Python 3.11+ and npm (for local frontend build) if running locally
- Docker and Docker Compose if running with containers

### 2 Environment

Copy the example env for the backend and set secrets (do NOT commit your real keys):

```bash
cp chatbot-system/.env.example chatbot-system/.env
# Edit chatbot-system/.env and set OPENAI_API_KEY and any other secrets
```

The important variables are:
- `OPENAI_API_KEY` — OpenAI API key used by the backend
- `OPENAI_MODEL` — optional; default `gpt-4o-mini` in the example
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — Neo4j connection settings

### 3a Run locally (frontend + backend separately)

Backend (Python):

```bash
cd chatbot-system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# ensure chatbot-system/.env has OPENAI_API_KEY set
python app.py
```

Frontend (Vite):

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:5000` by default.

### 3b Run with Docker Compose (recommended)

From project root:

```bash
docker compose build
docker compose up
```

This starts Neo4j (ports 7474/7687), the backend on port 5000, and the frontend on port 8080.

To run detached:

```bash
docker compose up -d
```

To rebuild after changes:

```bash
docker compose build --no-cache
docker compose up -d
```

### 4 Notes and troubleshooting

- If you previously used a Google Gemini key, replace app config to use `OPENAI_API_KEY` and ensure `openai` is installed (the `requirements.txt` already contains `openai`).
- The compose file mounts `./chatbot-system` into the backend container for dev; for production remove the mount to rely on image contents only.
- Check container logs with `docker compose logs -f backend` and browser devtools for frontend requests to debug connectivity.

---

If you'd like, I can also update `README.md` to include example API usage or wire the `app.py` code to fully use OpenAI (I sketched the changes earlier). Which would you like next?


## Features

- *Conversational Interface* – Ask questions like:
  - "What are the top-performing products this month?"
  - "Which KPIs are underperforming this quarter?"
- *Powered by Google Gemini* – Translates business questions into analytical strategies.
- *Schema-aware* – Understands fact tables, dimensions, and measures.
- *Works with Large Schemas* – Handles 150+ tables split across multiple JSON files.
- *Vector-based Retrieval* – Uses FAISS to semantically match questions with relevant schema chunks.
-  *Modular Design* – Can be integrated with internal tools, CRMs, or analytics dashboards.

---

##  Tech Stack

| Layer        | Technology        |
|--------------|-------------------|
| Frontend     | React + Vite      |
| Backend      | Flask             |
| AI Model     | Google Gemini     |
| Database     | Neo4j             |
| Vector Store | FAISS             |

---

##  How it Works

1. *Schema Extraction*  
   Neo4j is used to model your dimensional data warehouse (fact and dimension tables). A Python script extracts the schema, chunks it into JSON files, and saves it.

2. *Schema Summarization*  
   Each JSON file (representing a chunk of the schema) is summarized using a Gemini-powered prompt, creating a business-readable description.

3. *Vector Embedding*  
   The summarized schema chunks are embedded using FAISS for fast semantic retrieval.

4. *User Question Handling*  
   - User types a natural language question in the React UI.
   - The Flask backend receives it and uses FAISS to find the most relevant schema chunks.
   - It sends those chunks along with the user's question to Gemini with a BI-optimized prompt.
   - Gemini generates a structured response outlining:
     - Strategic objective
     - Key dimensions and measures
     - Analytical techniques
     - Actionable business insights
