
import ReactMarkdown from "react-markdown";
import { useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function cleanMarkdown(value = "") {
  return value
    .replace(/\\([*#`_])/g, "$1")
    .replace(/\\n/g, "\n")
    .replace(/&#x20;/gi, " ");
}

export default function App() {
  const [mode, setMode] = useState("chat");
  const [text, setText] = useState("");
  const [messages, setMessages] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sourceText, setSourceText] = useState("");

  
  async function handleSubmit(e) {
    e.preventDefault();

    const submittedText = text.trim();
    if (!submittedText || loading) return;

    setError("");
    setLoading(true);

    try {
      if (mode === "chat") {
        setMessages((prev) => [
          ...prev,
          { role: "user", content: submittedText },
          { role: "assistant", content: "" },
        ]);
        setText("");

        const response = await fetch(`${API}/chat/stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: submittedText }),
        });

        if (!response.ok || !response.body) {
          throw new Error(`Streaming failed (${response.status})`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let assistantText = "";

        function updateAssistant(content) {
          assistantText += content;

          setMessages((prev) => {
            const next = [...prev];
            const last = next.length - 1;

            if (last >= 0 && next[last].role === "assistant") {
              next[last] = {
                ...next[last],
                content: assistantText,
              };
            }

            return next;
          });
        }

        function processEvent(event) {
          const lines = event.split(/\r?\n/);

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;

            const data = JSON.parse(line.slice(6));

            if (data.error) {
              throw new Error(data.error);
            }

            if (data.chunk) {
              updateAssistant(data.chunk);
            }
          }
        }

        while (true) {
          const { value, done } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });

          const events = buffer.split(/\r?\n\r?\n/);
          buffer = events.pop() || "";

          for (const event of events) {
            if (event.trim()) {
              processEvent(event);
            }
          }
        }

        buffer += decoder.decode();

        if (buffer.trim()) {
          processEvent(buffer);
        }
      } else {
        const response = await fetch(`${API}/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: submittedText }),
        });

        if (!response.ok) {
          throw new Error(`Extraction failed (${response.status})`);
        }

        const data = await response.json();

        setResult(data);
        setSourceText(submittedText);
        setText("");
      }
    } catch (err) {
      console.error("Request failed:", err);
      setError(err.message || "Something went wrong.");

      if (mode === "chat") {
        setMessages((prev) => {
          const next = [...prev];

          if (next.length && next[next.length - 1].role === "assistant") {
            next[next.length - 1] = {
              ...next[next.length - 1],
              content:
                next[next.length - 1].content ||
                "Sorry, the request failed. Please try again.",
            };
          }

          return next;
        });
      }
    } finally {
      setLoading(false);
    }
  }


  return (
    <main className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h1>Smart Extractor</h1>
            <p>AI-powered chat and structured extraction</p>
          </div>
        </div>
        <span className="status"><span /> API Workspace</span>
      </header>

      <section className="hero">
        <span className="eyebrow">YOUR AI WORKSPACE</span>
        <h2>Turn text into <span>intelligence.</span></h2>
        <p>
          Ask questions, explore ideas, or transform unstructured text into
          useful data.
        </p>
      </section>

      <section className="workspace">
        <aside className="sidebar">
          <p className="section-label">WORKSPACE</p>

          <button
            className={mode === "chat" ? "nav-item active" : "nav-item"}
            onClick={() => {
              setMode("chat");
              setError("");
            }}
          >
            <span>◉</span>
            <span><strong>AI Chat</strong><small>Ask anything</small></span>
          </button>

          <button
            className={mode === "extract" ? "nav-item active" : "nav-item"}
            onClick={() => {
              setMode("extract");
              setError("");
            }}
          >
            <span>▤</span>
            <span><strong>Text Extractor</strong><small>Get structured JSON</small></span>
          </button>

          <div className="sidebar-note">
            <span>✧</span>
            <strong>Built for clarity</strong>
            <p>Powered by your Python API and language model.</p>
          </div>

          <button
            className="clear-btn"
            onClick={() => {
              setMessages([]);
              setResult(null);
              setSourceText("");
              setError("");
              setText("");
            }}
          >
            Clear workspace
          </button>
        </aside>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="panel-icon">{mode === "chat" ? "◉" : "▤"}</span>
              <div>
                <h3>{mode === "chat" ? "AI Chat" : "Structured Extractor"}</h3>
                <p>
                  {mode === "chat"
                    ? "Have a conversation with your AI assistant."
                    : "Convert text into validated, structured information."}
                </p>
              </div>
            </div>
            <span className="mode-tag">
              {mode === "chat" ? "CHAT MODE" : "EXTRACT MODE"}
            </span>
          </div>

          {mode === "chat" ? (
            <div className="conversation">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">✦</div>
                  <h3>What would you like to explore?</h3>
                  <p>Send a message below to start your conversation.</p>
                  <div className="suggestions">
                    <button onClick={() => setText("Explain RAG in simple terms.")}>
                      Explain RAG
                    </button>
                    <button onClick={() => setText("Give me three practical AI project ideas.")}>
                      AI project ideas
                    </button>
                  </div>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div className={`message ${message.role}`} key={index}>
                    <span className="avatar">
                      {message.role === "user" ? "You" : "AI"}
                    </span>
                    <div className="message-content">
                      <strong>
                        {message.role === "user" ? "You" : "Assistant"}
                      </strong>
                      <div className="markdown-content">
                        <ReactMarkdown>
                          {cleanMarkdown(message.content)}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>
                ))
              )}
              {loading && <p className="loading-text">AI is responding...</p>}
            </div>
          ) : (
            <div className="extract-info">
              <div className="extract-symbol">{"{ }"}</div>
              <h3>Extract meaningful data</h3>
              <p>
                Paste an article, document, or any text. The AI will return a
                structured result with a title, summary, keywords, and category.
              </p>
              <div className="schema-tags">
                <span>Title</span><span>Summary</span>
                <span>Keywords</span><span>Category</span>
              </div>
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          {result && mode === "extract" && (
            <div className="extraction-results">
              <section className="source-card">
                <div className="result-heading">
                  <strong>Original text</strong>
                  <span>Source</span>
                </div>
                <p className="source-content">{sourceText}</p>
              </section>

              <section className="result-box">
                <div className="result-heading">
                  <strong>Structured extraction</strong>
                  <button
                    type="button"
                    onClick={() =>
                      navigator.clipboard.writeText(
                        JSON.stringify(result, null, 2)
                      )
                    }
                  >
                    Copy JSON
                  </button>
                </div>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </section>
            </div>
          )}

          <form className="composer" onSubmit={handleSubmit}>
            <label htmlFor="prompt">
              {mode === "chat" ? "YOUR MESSAGE" : "TEXT TO EXTRACT"}
            </label>
            <textarea
              id="prompt"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={
                mode === "chat"
                  ? "Ask your AI assistant anything..."
                  : "Paste your text here..."
              }
              rows={4}
              required
            />
            <div className="composer-footer">
              <span>
                {mode === "chat"
                  ? "AI-generated responses may need verification."
                  : "Output is validated by the backend."}
              </span>
              <button
                className="send-btn"
                disabled={loading || !text.trim()}
                type="submit"
              >
                {loading
                  ? "Processing..."
                  : mode === "chat"
                    ? "Send message ↗"
                    : "Extract data ↗"}
              </button>
            </div>
          </form>
        </section>
      </section>

      <footer>SMART EXTRACTOR <span>•</span> WEEK 2 PROJECT</footer>
    </main>
  );
}
