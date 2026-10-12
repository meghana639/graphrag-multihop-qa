
from retrieval import GraphRAGRetriever
from generation import AnswerGenerator


class GraphRAGPipeline:

    def __init__(
        self,
        corpus_path,
        embeddings_path,
        neo4j_uri,
        neo4j_username,
        neo4j_password
    ):

        print("Initializing GraphRAG...")

        # Retrieval system:
        # Vector Search + Neo4j + Cross-Encoder
        self.retriever = GraphRAGRetriever(
            corpus_path=corpus_path,
            embeddings_path=embeddings_path,
            neo4j_uri=neo4j_uri,
            neo4j_username=neo4j_username,
            neo4j_password=neo4j_password
        )

        # FLAN-T5 answer generator
        self.generator = AnswerGenerator()

        print("✅ GraphRAG pipeline ready")

    def ask(self, question):

        # --------------------------------
        # 1. Hybrid GraphRAG retrieval
        # --------------------------------
        retrieval = self.retriever.retrieve(
            question,
            top_k=5
        )

        final_results = retrieval[
            "final_results"
        ]

        final_titles = [
            item["title"]
            for item in final_results
        ]

        # --------------------------------
        # 2. Generate final answer
        # --------------------------------
        answer = self.generator.generate(
            question=question,
            retrieved_titles=final_titles,
            corpus_dict=self.retriever.corpus_dict
        )

        # --------------------------------
        # 3. Return answer + diagnostics
        # --------------------------------
        return {
            "question": question,
            "answer": answer,

            "vector_titles":
                retrieval["vector_titles"],

            "graph_expansions":
                retrieval["graph_results"],

            "hybrid_candidate_count":
                retrieval["candidate_count"],

            "final_titles":
                final_titles,

            "final_results":
                final_results
        }

    def close(self):
        self.retriever.close()
