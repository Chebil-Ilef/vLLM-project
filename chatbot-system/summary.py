import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_schema(data):
    nodes = data.get("nodes", [])
    relationships = data.get("relationships", [])
    
    type_counts = {}
    type_samples = {}
    total_measures = 0
    
    for node in nodes:
        ntype = node.get("type", "Unknown")
        type_counts[ntype] = type_counts.get(ntype, 0) + 1
        
        # sample node names for each type (max 3)
        if ntype not in type_samples:
            type_samples[ntype] = []
        if len(type_samples[ntype]) < 3:
            type_samples[ntype].append(node.get("name", "Unnamed"))
        
        # count measures, if measures list exists and is not None
        measures = node.get("measures")
        if isinstance(measures, list):
            total_measures += len(measures)
    
    rel_count = len(relationships)
    
    summary_lines = []
    for t, count in type_counts.items():
        samples = ", ".join(type_samples[t])
        summary_lines.append(f"{count} {t}(s) e.g. [{samples}]")
    summary_lines.append(f"Total measures across nodes: {total_measures}")
    summary_lines.append(f"Total relationships: {rel_count}")
    
    return "; ".join(summary_lines)

def summarize_with_openai(prompt, model=None, temperature=0.0):
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    messages = [{"role": "user", "content": prompt}]
    resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=temperature)
    return resp["choices"][0]["message"]["content"]

def main():
    dir_path = "schema_chunks"
    summaries = {}
    
    for filename in os.listdir(dir_path):
        if filename.endswith(".json"):
            filepath = os.path.join(dir_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    summary = summarize_schema(data)
                except Exception as e:
                    summary = f"Error parsing JSON: {str(e)}"
            summaries[filename] = summary
    
    # Save summaries
    with open("summaries.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)
    
    print("Summaries generated and saved to summaries.json")

if __name__ == "__main__":
    main()