import { useState, useRef, useEffect } from "react";
import { askQuestion, submitFeedback, getDiagnosis } from "../api/client";
import ChunkList from "../components/ChunkList";
import DiagnosisPanel from "../components/DiagnosisPanel";
import "./ChatPage.css";

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setInput("");
    setError(null);
    setLoading(true);
    try {
      const res = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          id: res.query_id ?? crypto.randomUUID(),
          question,
          answer: res.answer,
          chunks: res.chunks,
          confidence: res.confidence,
          queryId: res.query_id,
          feedback: null,
          feedbackNote: "",
          showNoteInput: false,
          diagnosis: null,
          diagnosisLoading: false,
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function patchMessage(id, patch) {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...patch } : m)));
  }

  async function handleFeedback(msg, rating) {
    if (!msg.queryId) return;
    patchMessage(msg.id, { feedback: rating });

    if (rating === "down") {
      patchMessage(msg.id, { diagnosisLoading: true });
      try {
        const res = await submitFeedback(msg.queryId, "down", msg.feedbackNote || null);
        if (res.diagnosis_id) {
          const diagnosis = await getDiagnosis(res.diagnosis_id);
          patchMessage(msg.id, { diagnosis, diagnosisLoading: false });
        } else {
          patchMessage(msg.id, { diagnosisLoading: false });
        }
      } catch (err) {
        patchMessage(msg.id, { diagnosisLoading: false });
        setError(err.message);
      }
    } else {
      submitFeedback(msg.queryId, "up", null).catch((err) => setError(err.message));
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-history">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="eyebrow">No queries yet</div>
            <p>Ask a question about the ingested documents to begin.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div className="chat-turn" key={msg.id}>
            <div className="chat-question">
              <span className="chat-question-label">you</span>
              {msg.question}
            </div>

            <div className="chat-answer panel">
              <div className="chat-answer-head">
                <span className="eyebrow">answer</span>
                {msg.confidence != null && (
                  <span className="chat-confidence">self-reported confidence {msg.confidence}/5</span>
                )}
              </div>
              <p className="chat-answer-text">{msg.answer}</p>

              <ChunkList chunks={msg.chunks} />

              <div className="chat-feedback-row">
                <button
                  className={`fb-btn ${msg.feedback === "up" ? "active-up" : ""}`}
                  onClick={() => handleFeedback(msg, "up")}
                  disabled={msg.feedback != null}
                >
                  ▲ good
                </button>
                <button
                  className={`fb-btn ${msg.feedback === "down" ? "active-down" : ""}`}
                  onClick={() => {
                    if (!msg.showNoteInput && msg.feedback == null) {
                      patchMessage(msg.id, { showNoteInput: true });
                    } else {
                      handleFeedback(msg, "down");
                    }
                  }}
                  disabled={msg.feedback != null}
                >
                  ▼ bad
                </button>
              </div>

              {msg.showNoteInput && msg.feedback == null && (
                <div className="fb-note-row">
                  <input
                    type="text"
                    placeholder="what went wrong? (optional)"
                    value={msg.feedbackNote}
                    onChange={(e) => patchMessage(msg.id, { feedbackNote: e.target.value })}
                  />
                  <button className="btn-primary" onClick={() => handleFeedback(msg, "down")}>
                    submit
                  </button>
                </div>
              )}

              {msg.diagnosisLoading && <div className="diagnosis-loading">running diagnostic agent…</div>}
              {msg.diagnosis && <DiagnosisPanel diagnosis={msg.diagnosis} documentId={msg.chunks?.[0]?.document_id} />}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form className="chat-input-row" onSubmit={handleSend}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the ingested documents…"
          disabled={loading}
        />
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? "asking…" : "ask"}
        </button>
      </form>
    </div>
  );
}
