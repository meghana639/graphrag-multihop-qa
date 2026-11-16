
import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const suggestions = [
  "Were Scott Derrickson and Ed Wood of the same nationality?",
  "Which people share the same nationality?",
  "What relationships connect the entities in the knowledge graph?",
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    const text = question.trim();
    if (!text || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to generate an answer."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Cannot connect to FastAPI. Make sure your backend is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
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
            INTELLIGENT KNOWLEDGE RETRIEVAL
          </div>

          <h1>
            Go beyond search.
            <br />
            <span>Connect the knowledge.</span>
          </h1>

          <p className="subtitle">
            Explore complex questions through vector search,
            knowledge graph expansion, cross-encoder reranking,
            and AI-powered answer generation.
          </p>
        </div>

        <section className="query-card">
          <div className="card-heading">
            <div>
              <span className="section-label">YOUR QUESTION</span>
              <h2>Ask GraphRAG</h2>
            </div>
            <span className="ai-badge">✦ AI POWERED</span>
          </div>

          <form onSubmit={handleSubmit}>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a complex multi-hop question..."
              rows={4}
            />

            <div className="form-footer">
              <span>
                Discover connections across your knowledge graph
              </span>
              <button
                type="submit"
                disabled={!question.trim() || loading}
              >
                {loading ? "Generating..." : "Generate Answer"}
                <span>{loading ? "⌛" : "→"}</span>
              </button>
            </div>
          </form>
        </section>

        {loading && (
          <section className="query-card result-card">
            <span className="section-label">PROCESSING</span>
            <h2>Searching the knowledge graph...</h2>
            <p>
              Retrieving documents, exploring relationships,
              reranking evidence, and generating your answer.
            </p>
          </section>
        )}

        {error && (
          <section
            className="query-card result-card"
            role="alert"
          >
            <span className="section-label">REQUEST FAILED</span>
            <h2>Something went wrong</h2>
            <p>{error}</p>
          </section>
        )}

        {result && (
          <section className="query-card result-card">
            <div className="card-heading">
              <div>
                <span className="section-label">
                  GRAPH-ENHANCED RESPONSE
                </span>
                <h2>Generated Answer</h2>
              </div>
              <span className="ai-badge">✦ AI RESULT</span>
            </div>

            <p className="result-question">
              <strong>Question:</strong> {result.question}
            </p>

            <div className="answer-content">
              <p>{result.answer}</p>
            </div>

            <div className="result-stats">
              <div className="stat">
                <strong>
                  {result.vector_candidates?.length ?? 0}
                </strong>
                <span>Vector Matches</span>
              </div>

              <div className="stat">
                <strong>
                  {result.hybrid_candidate_count ?? 0}
                </strong>
                <span>Hybrid Candidates</span>
              </div>

              <div className="stat">
                <strong>
                  {result.evidence?.length ?? 0}
                </strong>
                <span>Evidence Documents</span>
              </div>
            </div>

            <div className="evidence-section">
              <h3>Supporting Evidence</h3>

              {result.evidence?.length ? (
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
              ) : (
                <p>No supporting evidence returned.</p>
              )}
            </div>
          </section>
        )}

        <section className="suggestions">
          <div className="section-heading">
            <span className="section-label">GET INSPIRED</span>
            <h2>Try an example question</h2>
          </div>

          <div className="suggestion-grid">
            {suggestions.map((item, index) => (
              <button
                key={index}
                className="suggestion-card"
                onClick={() => {
                  setQuestion(item);
                  setResult(null);
                  setError("");
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
      </footer>
    </div>
  );
}

export default App;
