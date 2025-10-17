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

# Narrow CORS to the frontend origin by default (overridable with FRONTEND_ORIGIN)
CORS(app, resources={r"/query": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:8080")}})

logger.info("Starting backend; VLLM_URL=%s VLLM_MODEL=%s", os.getenv("VLLM_URL"), os.getenv("VLLM_MODEL"))

try:
    embedder = embed.Embedder()
    logger.info("Embedder initialized with %d entries", len(getattr(embedder, "embeddings", {})))
except Exception:
    logger.exception("Failed to initialize Embedder; ensure summaries.json and schema_chunks exist and are valid")
    raise

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    user_prompt = data.get("prompt")
    if not user_prompt:
        return jsonify({"error": "Missing prompt"}), 400

    # Find closest summary file(s)
    closest_files = embedder.find_closest(user_prompt, top_k=1)
    best_file = closest_files[0][0]

    # Load best summary content
    with open(os.path.join("schema_chunks", best_file), "r") as f:
        schema_summary = json.load(f).get("summary", "")

    prompt = f"""
You are a business intelligence expert specializing in dimensional analysis and transforming user queries into complete and actionable analytical strategies.

## Analysis Context
**Available Data Schema:**
{schema_summary}

**User Question:**
{user_prompt}

## Your Mission
Transform this question into a complete analytical strategy that fully leverages the dimensional model and BI best practices.

## Expected Response Structure

### 1. **Strategic Objective**
- Link the analysis to a clear business objective (growth, efficiency, profitability)
- Explain the potential business impact of this analysis

### 2. **Primary Analytical Approach**
- Identify the key **measures** to be analyzed
- Determine the relevant **dimensions**
- Define the analysis methodology

### 3. **Multi-Level Dimensional Analysis**
- Leverage dimensional hierarchies (drill-down, roll-up)
- Propose cross-dimensional analyses
- Identify segmentation opportunities

### 4. **Advanced BI Techniques**
Integrate relevant analytical methods:
- **Pareto analysis** (80/20 rule)
- **Trend analysis** (seasonality, growth)
- **Comparative analysis** (benchmarking, period-over-period)
- **Segmentation** (RFM, behavioral, geographic)
- **Variance analysis** (performance vs. targets)
- **Anomaly detection**

### 5. **Multi-Layered Analytical Perspectives**
- **Descriptive**: What happened? (aggregations, rankings)
- **Diagnostic**: Why did it happen? (drill-down, causal analysis)
- **Predictive**: What could happen? (trend indicators)
- **Prescriptive**: What should be done? (actionable recommendations)

### 6. **Actionable Insights**
- Concrete actions this analysis should inform
- Performance indicators to monitor
- Specific business decisions to be made

## Guiding Principles
- **Business-Oriented**: Always frame the analysis in terms of business impact
- **Multi-Dimensional**: Leverage all capabilities of the dimensional model
- **Actionable**: Ensure recommendations lead to specific decisions
- **Hierarchical**: Systematically use drill-down capabilities
- **Comparative**: Include benchmarking and trend analysis

## Response Format
Respond in English, using language that is accessible to non-technical executives. Use structured bullet points and avoid technical jargon. Focus on business insights and analytical strategies, not technical implementation.

**Tone and Approach**: Be confident and assume logical names for tables and columns, even if the schema is not fully detailed. Use your BI expertise to propose standard and consistent names (e.g., fact_sales, dim_product, measure_revenue, etc.).

## Data Element Identification
Clearly indicate which **fact tables**, **measures**, and **dimensions** are involved in your analytical strategy.

**IMPORTANT**: Even if exact names are not provided in the schema, always make smart assumptions about likely table and column names based on:
- Standard BI naming conventions (e.g., fact_sales, dim_product, dim_customer, etc.)
- The business context of the analysis
- Common practices in data warehouses

Never mention that the names are "not specified" — always assume logical and consistent names.
"""

    # Call vLLM HTTP API (vllm OpenAI-compatible server). This is mandatory.
    try:
        logger.info("Calling vLLM (model=%s)", os.getenv("VLLM_MODEL"))
        raw = vllm_client.openai_chat_completion(
            model=os.getenv("VLLM_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.0,
        )
        # Extract assistant content in OpenAI Chat style
        try:
            answer = raw["choices"][0]["message"]["content"]
        except Exception:
            # Fallbacks for alternative response shapes
            if "choices" in raw and len(raw["choices"]) > 0 and "text" in raw["choices"][0]:
                answer = raw["choices"][0]["text"]
            else:
                logger.debug("Unexpected vLLM raw response: %s", raw)
                raise RuntimeError("Unexpected vLLM response shape")
    except Exception as e:
        logger.exception("vLLM request failed: %s", e)
        return jsonify({
            "error": "vLLM request failed",
            "detail": str(e),
            "vllm_url": os.getenv("VLLM_URL", "http://vllm:8000"),
        }), 500

    return jsonify({
        "best_summary_file": best_file,
        "schema_summary": schema_summary,
        "response": answer
    })


if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)