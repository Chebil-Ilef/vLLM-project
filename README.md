# BIAssistant – AI-Powered Business Intelligence Chatbot

BIAssistant is an AI-powered assistant designed to help *non-technical users* explore and analyze business data intuitively, simply by asking questions in natural language.  
Whether you're a business analyst, a product manager, or an executive with no BI background, BIAssistant can help you understand your data warehouse and extract valuable insights.

## Setup

Follow these steps to run the project locally or with Docker Compose.

### 1 Prerequisites

- Docker and Docker Compose : running with containers
- Cuda >=12.0

### 2 Environment

Copy the example env for the backend and set secrets (do NOT commit your real keys):

```bash
cp chatbot-system/.env.example chatbot-system/.env
# Edit chatbot-system/.env and set VLLM_URL, VLLM_API_KEY, VLLM_MODEL and any other secrets
```

The important variables are:
- `VLLM_URL` — URL for the OpenAI-compatible vLLM server the backend will call (default `http://vllm:8000` when using docker-compose)
- `VLLM_API_KEY` — API key for the vLLM server (use the same key passed to the vllm container with --api-key)
- `VLLM_MODEL` — vLLM model identifier to use (example `mistralai/Mistral-7B-v0.1
`)
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` — Neo4j connection settings

### Run with Docker Compose (recommended)

From the project root, copy the example env and start the stack:

```bash
cp chatbot-system/.env.example chatbot-system/.env
# Edit chatbot-system/.env and set VLLM_URL, VLLM_API_KEY, VLLM_MODEL and any other secrets

docker compose build
docker compose up
```

What this will start:
- Neo4j (http://localhost:7474, bolt://localhost:7687)
- Backend (Flask) on http://localhost:5000
- Frontend (Vite) on http://localhost:8080

To run detached:

```bash
docker compose up -d
```

To rebuild after changes:

```bash
docker compose build --no-cache
docker compose up -d
```

## Model

By default this project is configured to use the Mistral instruct model when running the included vLLM server:

- Default model: `mistralai/Mistral-7B-v0.1
`

You can change which model the vLLM server loads in two places:

- In `chatbot-system/.env` set `VLLM_MODEL` to the desired model identifier (the backend reads this when calling the vLLM server).
- Or change the `--model` argument passed to the `vllm` container in `docker-compose.yml` (the example compose uses `mistralai/Mistral-7B-v0.1
`).

Note: larger models will require more memory and GPU resources — consult the vLLM documentation for model compatibility and recommended server/resource settings.

## Features

- *Conversational Interface* – Ask questions like:
  - "What are the top-performing products this month?"
  - "Which KPIs are underperforming this quarter?"
- *Powered by vLLM (OpenAI-compatible)* – Translates business questions into analytical strategies via the local or remote vLLM server configured by `VLLM_URL`.
- *Schema-aware* – Understands fact tables, dimensions, and measures.
- *Works with Large Schemas* – Handles 150+ tables split across multiple JSON files.
- *Vector-based Retrieval* – Uses FAISS to semantically match questions with relevant schema chunks.
-  *Modular Design* – Can be integrated with internal tools, CRMs, or analytics dashboards.


##  Tech Stack

| Layer        | Technology        |
|--------------|-------------------|
| Frontend     | React + Vite      |
| Backend      | Flask             |
| AI Model     | vLLM              |
| Database     | Neo4j             |
| Vector Store | FAISS             |


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
   - It sends those chunks along with the user's question to Gemini wth a BI-optimized prompt.
   - Gemini generates a structured response outlining:
     - Strategic objective
     - Key dimensions and measures
     - Analytical techniques
     - Actionable business insights

## Demo

![Demo](demo.gif)
