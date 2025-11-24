import { useState, useRef, useEffect } from "react";
import "./App.css";

export default function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatScrollRef = useRef(null);
  const chatEndRef = useRef(null);
  const [shouldScroll, setShouldScroll] = useState(false);

  useEffect(() => {
    if (shouldScroll && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
      setShouldScroll(false);
    }
  }, [messages, shouldScroll]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: input.trim() }]);
    setInput("");
    setShouldScroll(true);
    setLoading(true);

    const API_URL = import.meta.env.VITE_API_URL;

    try {
      const res = await fetch(`${API_URL}/api/analyze-topic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: input.trim(),
          max_papers: 3,
        }),
      });

      if (!res.ok) throw new Error("Backend error: " + res.status);
      const report = await res.json();

      const botMessages = [];

      if (report.overview)
        botMessages.push({ role: "bot", content: report.overview });

      if (Array.isArray(report.papers) && report.papers.length) {
        botMessages.push({
          role: "bot",
          content:
            "<b>Papers:</b><br>" +
            report.papers
              .map(
                (p, i) =>
                  `${i + 1}. <a href="${p.url}" target="_blank">${p.title}</a>` +
                  (p.authors.length
                    ? `<br/><span class='meta'>Authors:</span> ${p.authors.join(", ")}`
                    : "") +
                  `<br/><span class='meta'>Published:</span> ${new Date(
                    p.published
                  ).toLocaleDateString()}` +
                  `<br/>${p.summary}<br/>`
              )
              .join(""),
        });
      } else {
        botMessages.push({ role: "bot", content: "No papers found." });
      }

      if (Array.isArray(report.calculations) && report.calculations.length) {
        botMessages.push({
          role: "bot",
          content:
            "<b>Calculations:</b><br>" +
            report.calculations
              .map(
                (calc) =>
                  `<b>${calc.label}:</b> ${calc.value}<br/><span class='meta'>${calc.details}</span>`
              )
              .join("<br/>"),
        });
      }

      if (report.future_work)
        botMessages.push({
          role: "bot",
          content: "<b>Next steps:</b><br>" + report.future_work,
        });

      setMessages((prev) => [...prev, ...botMessages]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content:
            "<span style='color:#ef4444'>Error: Could not fetch research papers. Backend may be down or endpoint unreachable.</span>",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Compact Header */}
      <header className="header">
        <span className="title">AstroQuery</span>
      </header>

      {/* Chat */}
      <main className="chat" ref={chatScrollRef}>
        <div className="container">
          {messages.length === 0 && !loading && (
            <div className="empty">
              <h2>Ask about astronomy research</h2>
              <p>Dark matter, exoplanets, cosmic phenomena...</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`msg ${msg.role}`}>
              <div
                className="content"
                dangerouslySetInnerHTML={{
                  __html: msg.content.replace(/\n/g, "<br/>"),
                }}
              />
            </div>
          ))}

          {loading && (
            <div className="msg bot">
              <div className="content loading">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </main>

      {/* Input */}
      <form className="input-bar" onSubmit={handleSubmit}>
        <input
          className="input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything..."
          disabled={loading}
        />
        <button
          className="send"
          type="submit"
          disabled={loading || !input.trim()}
        >
          →
        </button>
      </form>
    </div>
  );
}
