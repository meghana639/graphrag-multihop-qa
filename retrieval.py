
import json
import numpy as np
import torch

from sentence_transformers import SentenceTransformer, CrossEncoder
from neo4j import GraphDatabase


class GraphRAGRetriever:

    def __init__(
        self,
        corpus_path,
        embeddings_path,
        neo4j_uri,
        neo4j_username,
        neo4j_password
    ):

        # -----------------------------
        # Load corpus
        # -----------------------------
        with open(corpus_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        self.corpus_dict = {
            doc["title"]: doc["text"]
            for doc in self.documents
        }

        self.titles = [
            doc["title"]
            for doc in self.documents
        ]

        # -----------------------------
        # Load saved document embeddings
        # -----------------------------
        self.doc_embeddings = np.load(
            embeddings_path
        )

        # -----------------------------
        # Load embedding model
        # -----------------------------
        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device=device
        )

        # -----------------------------
        # Load cross-encoder
        # -----------------------------
        self.reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            device=device
        )

        # -----------------------------
        # Neo4j connection
        # -----------------------------
        self.driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(
                neo4j_username,
                neo4j_password
            )
        )

        self.driver.verify_connectivity()

    # =====================================================
    # VECTOR RETRIEVAL
    # =====================================================

    def vector_retrieve(
        self,
        question,
        top_k=5
    ):

        q_embedding = self.embedding_model.encode(
            [question],
            normalize_embeddings=True
        )[0]

        scores = (
            self.doc_embeddings
            @ q_embedding
        )

        top_indices = np.argsort(
            scores
        )[::-1][:top_k]

        return [
            self.titles[i]
            for i in top_indices
        ]

    # =====================================================
    # GRAPH EXPANSION
    # =====================================================

    def graph_expand_ranked(
        self,
        retrieved_titles,
        max_candidates_per_neighbor=5,
        max_neighbor_df=30
    ):

        with self.driver.session() as session:

            result = session.run(
                """
                MATCH (seed:Chunk)
                WHERE seed.title IN $titles

                MATCH (seed)-[:MENTIONS]->(e:Entity)

                WHERE e.type IN [
                    'PERSON',
                    'WORK',
                    'ORGANIZATION'
                ]

                MATCH (e)-[r:REL]-(neighbor:Entity)

                WHERE NOT r.type IN [
                    'LIVES_IN',
                    'LOCATED_IN'
                ]

                OPTIONAL MATCH
                    (allChunk:Chunk)-[:MENTIONS]->(neighbor)

                WITH
                    seed,
                    e,
                    r,
                    neighbor,
                    count(DISTINCT allChunk)
                    AS neighbor_df

                WHERE neighbor_df <= $max_neighbor_df

                CALL (seed, neighbor) {

                    MATCH
                        (candidate:Chunk)-[:MENTIONS]->(neighbor)

                    WHERE
                        candidate.doc_id <> seed.doc_id

                    RETURN candidate

                    LIMIT $max_candidates_per_neighbor
                }

                RETURN DISTINCT
                    seed.title AS seed_chunk,
                    e.name AS seed_entity,
                    e.type AS seed_entity_type,
                    r.type AS relation,
                    neighbor.name AS neighbor_entity,
                    neighbor.type AS neighbor_type,
                    neighbor_df,
                    candidate.doc_id AS candidate_doc_id,
                    candidate.title AS candidate_chunk

                ORDER BY
                    neighbor_df ASC,
                    candidate.title ASC
                """,

                titles=retrieved_titles,
                max_neighbor_df=max_neighbor_df,
                max_candidates_per_neighbor=
                    max_candidates_per_neighbor
            )

            return [
                dict(row)
                for row in result
            ]

    # =====================================================
    # HYBRID CANDIDATES
    # =====================================================

    def build_hybrid_candidates(
        self,
        vector_titles,
        graph_results
    ):

        candidates = {}

        for rank, title in enumerate(
            vector_titles,
            start=1
        ):

            candidates[title] = {
                "title": title,
                "from_vector": True,
                "vector_rank": rank,
                "from_graph": False,
                "graph_paths": []
            }

        for row in graph_results:

            title = row["candidate_chunk"]

            if title not in candidates:

                candidates[title] = {
                    "title": title,
                    "from_vector": False,
                    "vector_rank": None,
                    "from_graph": True,
                    "graph_paths": []
                }

            else:
                candidates[title][
                    "from_graph"
                ] = True

            candidates[title][
                "graph_paths"
            ].append({
                "seed_chunk":
                    row["seed_chunk"],

                "seed_entity":
                    row["seed_entity"],

                "relation":
                    row["relation"],

                "neighbor_entity":
                    row["neighbor_entity"],

                "neighbor_df":
                    row["neighbor_df"]
            })

        return list(
            candidates.values()
        )

    # =====================================================
    # CROSS-ENCODER RERANKING
    # =====================================================

    def rerank(
        self,
        question,
        candidates,
        top_k=5
    ):

        pairs = []
        valid_candidates = []

        for candidate in candidates:

            title = candidate["title"]

            if title not in self.corpus_dict:
                continue

            text = self.corpus_dict[title]

            document = (
                f"Title: {title}\n"
                f"Passage: {text}"
            )

            pairs.append([
                question,
                document
            ])

            valid_candidates.append(
                candidate
            )

        scores = self.reranker.predict(
            pairs,
            batch_size=16,
            show_progress_bar=False
        )

        scored = []

        for candidate, score in zip(
            valid_candidates,
            scores
        ):

            item = candidate.copy()

            item["reranker_score"] = float(
                score
            )

            scored.append(item)

        scored.sort(
            key=lambda x:
                x["reranker_score"],
            reverse=True
        )

        return scored[:top_k]

    # =====================================================
    # COMPLETE RETRIEVAL PIPELINE
    # =====================================================

    def retrieve(
        self,
        question,
        top_k=5
    ):

        vector_titles = self.vector_retrieve(
            question,
            top_k=5
        )

        graph_results = self.graph_expand_ranked(
            vector_titles
        )

        candidates = self.build_hybrid_candidates(
            vector_titles,
            graph_results
        )

        final_results = self.rerank(
            question,
            candidates,
            top_k=top_k
        )

        return {
            "vector_titles": vector_titles,
            "graph_results": graph_results,
            "candidate_count": len(candidates),
            "final_results": final_results
        }

    def close(self):
        self.driver.close()
