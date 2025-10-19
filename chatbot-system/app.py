import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import embed
import vllm_client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/query": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:8080")}})

logger.info("Starting backend; OPENAI_API_BASE=%s OPENAI_MODEL=%s",
            os.getenv("OPENAI_API_BASE"), os.getenv("OPENAI_MODEL"))

try:
    embedder = embed.Embedder()
    logger.info("Embedder initialized with %d entries", len(getattr(embedder, "embeddings", {})))
except Exception:
    logger.exception("Failed to initialize Embedder; ensure summaries.json and schema_chunks exist and are valid")
    raise

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "openai_api_base": os.getenv("OPENAI_API_BASE")}), 200

@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "Backend is running", "endpoints": ["/query", "/health"]}), 200

@app.route("/query", methods=["POST"])
def query():
    data = request.json or {}
    user_prompt = data.get("prompt")
    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    # Nearest schema summary
    closest_files = embedder.find_closest(user_prompt, top_k=1)
    best_file = closest_files[0][0]
    with open(os.path.join("schema_chunks", best_file), "r") as f:
        schema_summary = json.load(f).get("summary", "")

    prompt = f"""[same prompt you had; omitted here for brevity]
**Available Data Schema:**
{schema_summary}

**User Question:**
{user_prompt}
...
"""

    try:
        logger.info("Calling OpenAI chat via vLLM (model=%s)", os.getenv("OPENAI_MODEL") or os.getenv("VLLM_MODEL"))
        answer = vllm_client.call_vllm_chat(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.0,
        )
    except Exception as e:
        logger.exception("vLLM/OpenAI request failed: %s", e)
        return jsonify({
            "error": "LLM request failed",
            "detail": str(e),
            "openai_api_base": os.getenv("OPENAI_API_BASE", "http://vllm:8000/v1"),
        }), 500

    return jsonify({
        "best_summary_file": best_file,
        "schema_summary": schema_summary,
        "response": answer
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
