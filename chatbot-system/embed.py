from sentence_transformers import SentenceTransformer, util
import json
import os
import torch

class Embedder:
    def __init__(self, summaries_file="summaries.json", model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.summaries = json.load(open(summaries_file, "r"))
        self.embeddings = {}
        self._prepare_embeddings()

    def _prepare_embeddings(self):
        for filename, summary in self.summaries.items():
            emb = self.model.encode(summary, convert_to_tensor=True)
            self.embeddings[filename] = emb

    def find_closest(self, query, top_k=1):
        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = {}
        for fname, emb in self.embeddings.items():
            scores[fname] = util.cos_sim(query_emb, emb).item()
        best_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return best_files

if __name__ == "__main__":
    embedder = Embedder()
    query = "What are the main sales facts and their relationships?"
    closest = embedder.find_closest(query)
    print(closest)