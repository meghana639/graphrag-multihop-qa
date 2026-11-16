
import { useState } from "react";
import "./App.css";

// Frontend-only demonstration.
// This sample was generated previously by the GraphRAG pipeline.
const sampleResult = {
  question: "Were Scott Derrickson and Ed Wood of the same nationality?",
  answer: "Yes.",
  vector_candidates: [
    "Ed Wood (film)",
    "Ed Wood",
    "Scott Parkin",
    "Adam Collis",
    "Woodson, Arkansas",
  ],
  hybrid_candidate_count: 9,
  evidence: [
    {
      title: "Scott Derrickson",
      from_vector: false,
      from_graph: true,
      reranker_score: 2.154086112976074,
    },
    {
      title: "Ed Wood",
      from_vector: true,
      from_graph: false,
      reranker_score: 0.5066560506820679,
    },
    {
      title: "Ed Wood (film)",
      from_vector: true,
      from_graph: false,
      reranker_score: -0.052937138825654984,
    },
    {
      title: "Doctor Strange (2016 film)",
      from_vector: false,
      from_graph: true,
      reranker_score: -4.008537292480469,
    },
    {
      title: "Adam Collis",
      from_vector: true,
      from_graph: false,
      reranker_score: -4.209660530090332,
    },
  ],
};

const suggestions = [
  "Were Scott Derrickson and Ed Wood of the same nationality?",
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [notice, setNotice] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();

    const text = question.trim();
    if (!text) return;

    if (text !== sampleResult.question) {
      setResult(null);
      setNotice(
        "This public demo currently contains one prerecorded example. " +
          "Select the example question below to explore the GraphRAG results. " +
          "Live AI inference is available in the local project."
      );
      return;
    }

    setNotice("");
    setResult(sampleResult);
  };

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <span className="brand-icon">✦</span>
          <span>
            GraphRAG<span className="brand-accent">AI</span>
          </span>
        </div>

        <a
          className="github-link"
          href="https://github.com/meghana639/graphrag-multihop-qa"
          target="_blank"
          rel="noreferrer"
        >
          GitHub ↗
        </a>
      </header>

      <main className="main">
        <div className="hero">
          <div className="eyebrow">
            <span className="status-dot" />
            INTERACTIVE GRAPHRAG DEMO
          </div>

          <h1>
            Go beyond search.
            <br />
            <span>Connect the knowledge.</span>
          </h1>

          <p className="subtitle">
            Explore how vector search, knowledge graph expansion,
            cross-encoder reranking, and AI-powered answer generation
            work together in a multi-hop question answering system.
          </p>
        </div>

        <section className="query-card">
          <div className="card-heading">
            <div>
              <span className="section-label">SAMPLE QUESTION</span>
              <h2>Explore GraphRAG</h2>
            </div>
            <span className="ai-badge">✦ SAMPLE DEMO</span>
          </div>

          <p className="subtitle" style={{ marginBottom: "18px" }}>
            This hosted frontend demonstrates a previously generated
            result. Live AI inference is not connected to this deployment.
          </p>

          <form onSubmit={handleSubmit}>
            <textarea
              value={question}
              onChange={(event) => {
                setQuestion(event.target.value);
                setResult(null);
                setNotice("");
              }}
              placeholder="Select the example question below..."
              rows={4}
            />

            <div className="form-footer">
              <span>
                Explore a prerecorded knowledge graph response
              </span>

              <button type="submit" disabled={!question.trim()}>
                View Sample Answer
                <span>→</span>
              </button>
            </div>
          </form>
        </section>

        {notice && (
          <section className="query-card result-card" role="status">
            <span className="section-label">DEMO INFORMATION</span>
            <h2>Example question required</h2>
            <p>{notice}</p>
          </section>
        )}

        {result && (
          <section className="query-card result-card">
            <div className="card-heading">
              <div>
                <span className="section-label">
                  PRERECORDED GRAPH-ENHANCED RESPONSE
                </span>
                <h2>Sample Answer</h2>
              </div>
              <span className="ai-badge">✦ SAMPLE RESULT</span>
            </div>

            <p className="result-question">
              <strong>Question:</strong> {result.question}
            </p>

            <div className="answer-content">
              <p>{result.answer}</p>
            </div>

            <p style={{ marginTop: "14px", opacity: 0.7 }}>
              This answer and its retrieval statistics were generated
              previously. They are displayed for demonstration only.
            </p>

            <div className="result-stats">
              <div className="stat">
                <strong>{result.vector_candidates.length}</strong>
                <span>Vector Matches</span>
              </div>

              <div className="stat">
                <strong>{result.hybrid_candidate_count}</strong>
                <span>Hybrid Candidates</span>
              </div>

              <div className="stat">
                <strong>{result.evidence.length}</strong>
                <span>Evidence Documents</span>
              </div>
            </div>

            <div className="evidence-section">
              <h3>Retrieved Evidence</h3>

              <div className="evidence-list">
                {result.evidence.map((item, index) => (
                  <div
                    className="evidence-item"
                    key={`${item.title}-${index}`}
                  >
                    <div className="evidence-heading">
                      <strong>{item.title}</strong>
                      <span>
                        Score:{" "}
                        {Number(item.reranker_score).toFixed(3)}
                      </span>
                    </div>

                    <div className="evidence-tags">
                      {item.from_vector && (
                        <span className="evidence-tag">
                          Vector Search
                        </span>
                      )}

                      {item.from_graph && (
                        <span className="evidence-tag">
                          Graph Expansion
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        <section className="suggestions">
          <div className="section-heading">
            <span className="section-label">EXPLORE AN EXAMPLE</span>
            <h2>Try a sample question</h2>
          </div>

          <div className="suggestion-grid">
            {suggestions.map((item, index) => (
              <button
                key={index}
                className="suggestion-card"
                onClick={() => {
                  setQuestion(item);
                  setResult(null);
                  setNotice("");
                }}
              >
                <span className="suggestion-icon">↗</span>
                <span>{item}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="features">
          <div className="feature">
            <span className="feature-icon">◇</span>
            <div>
              <h3>Vector Search</h3>
              <p>Find semantically relevant information</p>
            </div>
          </div>

          <div className="feature">
            <span className="feature-icon">⌘</span>
            <div>
              <h3>Graph Expansion</h3>
              <p>Discover connected entities and relationships</p>
            </div>
          </div>

          <div className="feature">
            <span className="feature-icon">✧</span>
            <div>
              <h3>AI Generation</h3>
              <p>Generate answers from retrieved evidence</p>
            </div>
          </div>
        </section>
      </main>

      <footer>
        GraphRAG Multi-Hop QA · Built with React, FastAPI & Neo4j
        <p style={{ marginTop: "8px", opacity: 0.7 }}>
          Public preview uses prerecorded results. Full AI pipeline
          runs locally.
        </p>
      </footer>
    </div>
  );
}

export default App;
