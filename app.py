from pathlib import Path

import os
import streamlit as st

from pipeline import GraphRAGPipeline

BASE_DIR = Path(__file__).resolve().parent
CORPUS_PATH = BASE_DIR / "data" / "graphrag_corpus.json"
EMBEDDINGS_PATH = BASE_DIR / "data" / "graphrag_embeddings.npy"



# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GraphRAG Multi-Hop QA",
    page_icon="🔗",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🔗 GraphRAG Multi-Hop Question Answering")

st.write(
    """
    Ask a multi-hop question and the system will combine
    **vector retrieval**, **knowledge-graph expansion**,
    **cross-encoder reranking**, and **LLM generation**
    to produce an answer.
    """
)


# ============================================================
# LOAD PIPELINE
# ============================================================

@st.cache_resource
def load_pipeline():

    return GraphRAGPipeline(
        corpus_path=str(CORPUS_PATH),
        embeddings_path=str(EMBEDDINGS_PATH),
        neo4j_uri=os.environ["NEO4J_URI"],
        neo4j_username=os.environ["NEO4J_USERNAME"],
        neo4j_password=os.environ["NEO4J_PASSWORD"]
    )


try:
    pipeline = load_pipeline()

except Exception as e:

    st.error(
        "Could not initialize the GraphRAG pipeline."
    )

    st.exception(e)

    st.stop()


# ============================================================
# QUESTION INPUT
# ============================================================

default_question = (
    "Were Scott Derrickson and Ed Wood "
    "of the same nationality?"
)

question = st.text_input(
    "Enter your question:",
    value=default_question
)


# ============================================================
# ASK BUTTON
# ============================================================

if st.button(
    "Ask GraphRAG",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Searching vector index, exploring graph "
            "and generating answer..."
        ):

            try:

                result = pipeline.ask(
                    question.strip()
                )

                # ============================================
                # FINAL ANSWER
                # ============================================

                st.subheader("Answer")

                st.success(
                    result["answer"]
                )


                # ============================================
                # SUMMARY METRICS
                # ============================================

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Vector Candidates",
                    len(result["vector_titles"])
                )

                col2.metric(
                    "Hybrid Candidates",
                    result[
                        "hybrid_candidate_count"
                    ]
                )

                col3.metric(
                    "Final Evidence",
                    len(result["final_results"])
                )


                # ============================================
                # FINAL RETRIEVED EVIDENCE
                # ============================================

                st.subheader(
                    "Final Retrieved Evidence"
                )

                for rank, item in enumerate(
                    result["final_results"],
                    start=1
                ):

                    sources = []

                    if item["from_vector"]:
                        sources.append("Vector")

                    if item["from_graph"]:
                        sources.append("Graph")

                    source_text = " + ".join(
                        sources
                    )

                    title = item["title"]

                    with st.expander(
                        f"{rank}. {title} "
                        f"— {source_text}"
                    ):

                        st.write(
                            pipeline.retriever
                            .corpus_dict[title]
                        )

                        st.caption(
                            "Cross-Encoder Score: "
                            f"{item['reranker_score']:.4f}"
                        )


                # ============================================
                # VECTOR RETRIEVAL
                # ============================================

                with st.expander(
                    "Vector Search Results"
                ):

                    for rank, title in enumerate(
                        result["vector_titles"],
                        start=1
                    ):

                        st.write(
                            f"{rank}. {title}"
                        )


                # ============================================
                # GRAPH EXPANSION
                # ============================================

                with st.expander(
                    "Knowledge Graph Expansion"
                ):

                    graph_results = result[
                        "graph_expansions"
                    ]

                    if not graph_results:

                        st.info(
                            "No additional graph "
                            "expansions were found."
                        )

                    else:

                        for row in graph_results:

                            st.write(
                                f"**{row['seed_chunk']}** "
                                f"→ {row['seed_entity']} "
                                f"→ `{row['relation']}` "
                                f"→ {row['neighbor_entity']} "
                                f"→ **{row['candidate_chunk']}**"
                            )


            except Exception as e:

                st.error(
                    "An error occurred while "
                    "processing the question."
                )

                st.exception(e)


# ============================================================
# PROJECT INFORMATION
# ============================================================

st.divider()

st.caption(
    "GraphRAG pipeline: MiniLM Vector Retrieval → "
    "Neo4j Knowledge Graph Expansion → "
    "Cross-Encoder Reranking → FLAN-T5 Generation"
)
