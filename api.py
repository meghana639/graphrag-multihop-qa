from pathlib import Path

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pipeline import GraphRAGPipeline

BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "data" / "graphrag_corpus.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "graphrag_embeddings.npy"



# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="GraphRAG Multi-Hop QA API",
    description=(
        "Hybrid GraphRAG API using vector retrieval, "
        "Neo4j knowledge-graph expansion, "
        "cross-encoder reranking and FLAN-T5 generation."
    ),
    version="1.0.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# PIPELINE
# ============================================================

pipeline = None


@app.on_event("startup")
def startup_event():

    global pipeline

    pipeline = GraphRAGPipeline(
        corpus_path=str(CORPUS_PATH),
        embeddings_path=str(EMBEDDINGS_PATH),
        neo4j_uri=os.environ["NEO4J_URI"],
        neo4j_username=os.environ["NEO4J_USERNAME"],
        neo4j_password=os.environ["NEO4J_PASSWORD"]
    )


@app.on_event("shutdown")
def shutdown_event():

    if pipeline is not None:
        pipeline.close()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "GraphRAG Multi-Hop QA API"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "pipeline_loaded": pipeline is not None
    }


# ============================================================
# QUESTION ANSWERING
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = pipeline.ask(question)

        evidence = []

        for item in result["final_results"]:

            evidence.append({
                "title": item["title"],
                "from_vector": item["from_vector"],
                "from_graph": item["from_graph"],
                "reranker_score": item["reranker_score"]
            })

        return {
            "question": question,
            "answer": result["answer"],
            "vector_candidates": result["vector_titles"],
            "hybrid_candidate_count":
                result["hybrid_candidate_count"],
            "evidence": evidence
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
