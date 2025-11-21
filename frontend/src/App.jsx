import { useState } from "react";

export default function App() {
  const [topic, setTopic] = useState("");
  const [maxPapers, setMaxPapers] = useState(3);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setReport(null);

    try {
      const res = await fetch("http://localhost:8000/api/analyze-topic", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic,
          max_papers: maxPapers,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch report");
      }

      const data = await res.json();
      setReport(data);
    } catch (err) {
      console.error(err);
      alert("Error connecting to backend. Check console/logs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "2rem",
        background: "#020617",
        color: "#e5e7eb",
      }}
    >
      <div style={{ maxWidth: "900px", margin: "0 auto" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: 600, marginBottom: "0.5rem" }}>
          AstroResearch Agent
        </h1>
        <p style={{ fontSize: "0.9rem", color: "#cbd5f5", marginBottom: "1.5rem" }}>
          Enter an astrophysics topic. This version calls the local FastAPI backend.
        </p>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          style={{
            background: "#020617",
            border: "1px solid #1f2937",
            borderRadius: "0.75rem",
            padding: "1rem",
            marginBottom: "2rem",
          }}
        >
          <div style={{ marginBottom: "1rem" }}>
            <label
              htmlFor="topic"
              style={{
                display: "block",
                fontSize: "0.85rem",
                marginBottom: "0.25rem",
              }}
            >
              Topic
            </label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. black hole accretion"
              required
              style={{
                width: "100%",
                padding: "0.5rem 0.75rem",
                borderRadius: "0.5rem",
                border: "1px solid #4b5563",
                background: "#020617",
                color: "#e5e7eb",
              }}
            />
          </div>

          <div style={{ marginBottom: "1rem" }}>
            <label
              htmlFor="maxPapers"
              style={{
                display: "block",
                fontSize: "0.85rem",
                marginBottom: "0.25rem",
              }}
            >
              Max papers
            </label>
            <input
              id="maxPapers"
              type="number"
              min={1}
              max={10}
              value={maxPapers}
              onChange={(e) => setMaxPapers(Number(e.target.value))}
              style={{
                width: "80px",
                padding: "0.4rem 0.5rem",
                borderRadius: "0.5rem",
                border: "1px solid #4b5563",
                background: "#020617",
                color: "#e5e7eb",
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "0.5rem 1rem",
              borderRadius: "0.5rem",
              border: "none",
              background: loading ? "#4b5563" : "#6366f1",
              color: "white",
              fontSize: "0.9rem",
              fontWeight: 500,
              cursor: loading ? "default" : "pointer",
            }}
          >
            {loading ? "Generating..." : "Generate Report"}
          </button>
        </form>

        {/* Report */}
        {report && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1.25rem",
              marginBottom: "3rem",
            }}
          >
            <section
              style={{
                border: "1px solid #1f2937",
                borderRadius: "0.75rem",
                padding: "1rem",
              }}
            >
              <h2
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 600,
                  marginBottom: "0.5rem",
                }}
              >
                Overview
              </h2>
              <p style={{ fontSize: "0.9rem" }}>{report.overview}</p>
            </section>

            <section
              style={{
                border: "1px solid #1f2937",
                borderRadius: "0.75rem",
                padding: "1rem",
              }}
            >
              <h2
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 600,
                  marginBottom: "0.75rem",
                }}
              >
                Papers
              </h2>
              {report.papers.map((paper) => (
                <div
                  key={paper.title}
                  style={{
                    marginBottom: "0.9rem",
                    paddingBottom: "0.75rem",
                    borderBottom: "1px solid #1f2937",
                  }}
                >
                  <a
                    href={paper.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      color: "#6366f1",
                      fontWeight: 500,
                      textDecoration: "none",
                    }}
                  >
                    {paper.title}
                  </a>
                  <p
                    style={{
                      fontSize: "0.75rem",
                      color: "#9ca3af",
                      marginTop: "0.25rem",
                    }}
                  >
                    {paper.authors.join(", ")} ·{" "}
                    {new Date(paper.published).toLocaleDateString()}
                  </p>
                  <p style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
                    {paper.summary}
                  </p>
                </div>
              ))}
            </section>

            <section
              style={{
                border: "1px solid #1f2937",
                borderRadius: "0.75rem",
                padding: "1rem",
              }}
            >
              <h2
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 600,
                  marginBottom: "0.75rem",
                }}
              >
                Calculations
              </h2>
              {report.calculations.map((calc) => (
                <div key={calc.label} style={{ marginBottom: "0.6rem" }}>
                  <p style={{ fontSize: "0.9rem", fontWeight: 500 }}>
                    {calc.label}:{" "}
                    <span style={{ color: "#a5b4fc" }}>{calc.value}</span>
                  </p>
                  <p
                    style={{
                      fontSize: "0.8rem",
                      color: "#d1d5db",
                      marginTop: "0.25rem",
                    }}
                  >
                    {calc.details}
                  </p>
                </div>
              ))}
            </section>

            <section
              style={{
                border: "1px solid #1f2937",
                borderRadius: "0.75rem",
                padding: "1rem",
              }}
            >
              <h2
                style={{
                  fontSize: "1.2rem",
                  fontWeight: 600,
                  marginBottom: "0.5rem",
                }}
              >
                Future Work
              </h2>
              <p style={{ fontSize: "0.9rem" }}>{report.future_work}</p>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
