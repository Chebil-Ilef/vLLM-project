import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

# Neo4j connection config from env
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# How many nodes per chunk
CHUNK_SIZE = 50

class Neo4jSchemaExtractor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_nodes(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Table)
                RETURN n.name AS name, n.type AS type, n.measures AS measures
                ORDER BY n.name
            """)
            return [record.data() for record in result]

    def get_relationships(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Table)-[r]->(b:Table)
                RETURN a.name AS from, b.name AS to, type(r) AS rel_type, r.type AS rel_property_type
            """)
            return [record.data() for record in result]

def summarize_chunk(chunk):
    node_types = [node['type'] for node in chunk['nodes']]
    facts = node_types.count("Fact")
    dims = node_types.count("Dimension")
    rel_types = set(rel.get('type') or rel.get('rel_property_type') for rel in chunk['relationships'])
    summary = (
        f"Chunk Summary:\n"
        f"- Nodes: {len(chunk['nodes'])} (Facts: {facts}, Dimensions: {dims})\n"
        f"- Relationship types: {', '.join(rel_types)}"
    )
    return summary

def chunk_data(nodes, relationships, chunk_size):
    chunks = []
    for i in range(0, len(nodes), chunk_size):
        chunk_nodes = nodes[i:i+chunk_size]
        node_names = {node['name'] for node in chunk_nodes}
        chunk_rels = [rel for rel in relationships if rel['from'] in node_names and rel['to'] in node_names]
        chunks.append({
            "nodes": chunk_nodes,
            "relationships": chunk_rels
        })
    return chunks

def main():
    extractor = Neo4jSchemaExtractor(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        print("Extracting nodes...")
        nodes = extractor.get_nodes()
        print(f"Found {len(nodes)} nodes.")

        print("Extracting relationships...")
        relationships = extractor.get_relationships()
        print(f"Found {len(relationships)} relationships.")

        print("Splitting data into chunks...")
        chunks = chunk_data(nodes, relationships, CHUNK_SIZE)

        for idx, chunk in enumerate(chunks, start=1):
            summary = summarize_chunk(chunk)
            print(f"\n--- Chunk {idx} ---")
            print(summary)

            filename = f"schema_chunk_{idx:03d}.json"
            with open(filename, "w") as f:
                json.dump(chunk, f, indent=2)
            print(f"Saved chunk to {filename}")

    finally:
        extractor.close()

if __name__ == "__main__":
    main()
