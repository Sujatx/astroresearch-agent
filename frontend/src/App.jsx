import { useState, useRef, useEffect } from "react";
import "./App.css";

// Backend URL: from env in prod, fallback to Render URL (and you can swap to localhost when devving)
const API_URL =
  import.meta.env.VITE_API_URL || "https://astroresearch-agent.onrender.com";

export default function App() {
  const [input, setInput] = useState("");
  const [maxPapers, setMaxPapers] = useState(3);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Refs for scrolling logic
  const chatScrollRef = useRef(null);
  const chatEndRef = useRef(null);
  // Track if user just sent a prompt
  const [shouldScroll, setShouldScroll] = useState(false);

  // Scroll to bottom only on NEW user messages
  useEffect(() => {
    if (shouldScroll && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
      setShouldScroll(false);
    }
  }, [messages, shouldScroll]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: input.trim() },
    ]);
    setInput("");
    setShouldScroll(true); // Next message scrolls to bottom
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/analyze-topic`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: input.trim(),
          max_papers: maxPapers,
        }),
      });

      if (!res.ok) throw new Error("Backend error: " + res.status);
      const report = await res.json();

      const botMessages = [];

      if (report.overview)
        botMessages.push({ role: "bot", content: report.overview });

      if (Array.isArray(report.papers) && report.papers.length)
        botMessages.push({
          role: "bot",
          content:
            "<b>Papers:</b><br>" +
            report.papers
              .map(
                (p, i) =>
                  `${i + 1}. <a href="${p.url}" target="_blank">${p.title}</a>` +
                  (p.authors.length
                    ? `<br/><span class='gpt-label'>Authors:</span> ${p.authors.join(
                        ", "
                      )}`
                    : "") +
                  `<br/><span class='gpt-label'>Published:</span> ${new Date(
                    p.published
                  ).toLocaleDateString()}` +
                  `<br/>${p.summary}<br/>`
              )
              .join(""),
        });
      else if ("papers" in report)
        botMessages.push({ role: "bot", content: "No papers found." });

      if (Array.isArray(report.calculations) && report.calculations.length)
        botMessages.push({
          role: "bot",
          content:
            "<b>Calculations:</b><br>" +
            report.calculations
              .map(
                (calc) =>
                  `<b>${calc.label}:</b> ${calc.value}<br/><span class='gpt-label'>${calc.details}</span>`
              )
              .join("<br/>"),
        });

      if (report.future_work)
        botMessages.push({
          role: "bot",
          content: "<b>Next steps:</b><br>" + report.future_work,
        });

      setMessages((prev) => [...prev, ...botMessages]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content:
            "<span style='color:#e45'>Error: Could not fetch research papers. Backend may be down or endpoint unreachable.</span>",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="gpt-bg">
      {/* Fixed HEADER */}
      <header className="gpt-header fixed-header">
        <div className="gpt-header-name">AstroQuery</div>
      </header>

      {/* Chat scroll region */}
      <main className="chat-scroll" ref={chatScrollRef}>
        <section className="gpt-chat-bubbles">
          {messages.length === 0 && !loading && (
            <div className="gpt-empty-chat">How can I help, Sujat?</div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`gpt-block ${msg.role}`}>
              <div
                className="gpt-block-content"
                dangerouslySetInnerHTML={{
                  __html: msg.content.replace(/\n/g, "<br/>"),
                }}
              />
            </div>
          ))}
          {loading && (
            <div className="gpt-block bot">
              <span className="gpt-spinner" />
            </div>
          )}
          <div ref={chatEndRef} />
        </section>
      </main>

      {/* Fixed bottom INPUT */}
      <form
        className="gpt-chat-input-row fixed-input"
        onSubmit={handleSubmit}
        autoComplete="off"
      >
        <input
          className="gpt-chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything"
          required
        />
        <button
          className="gpt-chat-send"
          type="submit"
          disabled={loading}
          aria-label="send"
        >
          →
        </button>
      </form>
    </div>
  );
}
