import os
import csv
import json
from pathlib import Path
from neo4j import GraphDatabase


BASE_DIR = Path(__file__).resolve().parent
GRAPH_DIR = BASE_DIR / "data" / "graph"

CHUNKS_FILE = GRAPH_DIR / "graphrag_chunks.csv"
ENTITIES_FILE = GRAPH_DIR / "graphrag_entities.csv"
MENTIONS_FILE = GRAPH_DIR / "graphrag_mentions.csv"
RELATIONSHIPS_FILE = GRAPH_DIR / "graphrag_relationships.csv"


def read_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def batched(rows, batch_size=500):
    for i in range(0, len(rows), batch_size):
        yield rows[i:i + batch_size]


def main():
    uri = os.environ["NEO4J_URI"]
    username = os.environ["NEO4J_USERNAME"]
    password = os.environ["NEO4J_PASSWORD"]

    driver = GraphDatabase.driver(
        uri,
        auth=(username, password)
    )

    driver.verify_connectivity()
    print("Connected to Neo4j.")

    chunks = read_csv(CHUNKS_FILE)
    entities = read_csv(ENTITIES_FILE)
    mentions = read_csv(MENTIONS_FILE)
    relationships = read_csv(RELATIONSHIPS_FILE)

    print(f"Chunks: {len(chunks)}")
    print(f"Entities: {len(entities)}")
    print(f"MENTIONS: {len(mentions)}")
    print(f"REL relationships: {len(relationships)}")

    with driver.session() as session:

        # -------------------------
        # Constraints
        # -------------------------

        session.run("""
        CREATE CONSTRAINT chunk_doc_id_unique IF NOT EXISTS
        FOR (c:Chunk)
        REQUIRE c.doc_id IS UNIQUE
        """)

        session.run("""
        CREATE CONSTRAINT entity_key_unique IF NOT EXISTS
        FOR (e:Entity)
        REQUIRE e.entity_key IS UNIQUE
        """)

        print("Constraints ready.")

        # -------------------------
        # Chunk nodes
        # -------------------------

        for batch in batched(chunks):
            rows = [
                {
                    "doc_id": int(row["doc_id"]),
                    "title": row["title"],
                    "text": row["text"]
                }
                for row in batch
            ]

            session.run("""
            UNWIND $rows AS row

            MERGE (c:Chunk {doc_id: row.doc_id})

            SET c.title = row.title,
                c.text = row.text
            """, rows=rows)

        print("Chunk nodes imported.")

        # -------------------------
        # Entity nodes
        # -------------------------

        for batch in batched(entities):
            rows = []

            for row in batch:
                document_ids = row.get("document_ids", "[]")

                try:
                    document_ids = json.loads(document_ids)
                except Exception:
                    document_ids = []

                rows.append({
                    "entity_key": row["entity_key"],
                    "name": row["name"],
                    "type": row["type"],
                    "document_ids": document_ids
                })

            session.run("""
            UNWIND $rows AS row

            MERGE (e:Entity {entity_key: row.entity_key})

            SET e.name = row.name,
                e.type = row.type,
                e.document_ids = row.document_ids
            """, rows=rows)

        print("Entity nodes imported.")

        # -------------------------
        # Chunk -> Entity MENTIONS
        # -------------------------

        for batch in batched(mentions):
            rows = [
                {
                    "doc_id": int(row["doc_id"]),
                    "entity_key": row["entity_key"]
                }
                for row in batch
            ]

            session.run("""
            UNWIND $rows AS row

            MATCH (c:Chunk {doc_id: row.doc_id})
            MATCH (e:Entity {entity_key: row.entity_key})

            MERGE (c)-[:MENTIONS]->(e)
            """, rows=rows)

        print("MENTIONS relationships imported.")

        # -------------------------
        # Entity -> Entity REL
        # -------------------------

        for batch in batched(relationships):
            rows = [
                {
                    "source_key": row["source_key"],
                    "target_key": row["target_key"],
                    "relation": row["relation"],
                    "doc_id": int(row["doc_id"]),
                    "title": row["title"]
                }
                for row in batch
            ]

            session.run("""
            UNWIND $rows AS row

            MATCH (source:Entity {
                entity_key: row.source_key
            })

            MATCH (target:Entity {
                entity_key: row.target_key
            })

            MERGE (source)-[r:REL {
                type: row.relation,
                doc_id: row.doc_id
            }]->(target)

            SET r.title = row.title
            """, rows=rows)

        print("Entity relationships imported.")

        # -------------------------
        # Verification
        # -------------------------

        result = session.run("""
        MATCH (c:Chunk)
        WITH count(c) AS chunks

        MATCH (e:Entity)
        WITH chunks, count(e) AS entities

        MATCH ()-[m:MENTIONS]->()
        WITH chunks, entities, count(m) AS mentions

        MATCH ()-[r:REL]->()

        RETURN
            chunks,
            entities,
            mentions,
            count(r) AS relationships
        """)

        stats = result.single()

        print("\nGraph verification")
        print("------------------")
        print("Chunks:", stats["chunks"])
        print("Entities:", stats["entities"])
        print("MENTIONS:", stats["mentions"])
        print("REL:", stats["relationships"])

    driver.close()

    print("\nGraph import complete.")


if __name__ == "__main__":
    main()
