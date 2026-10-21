import ReactMarkdown from "react-markdown";
import { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

function cleanMarkdown(value = "") {
  return value
    .replace(/^(User\s+Safety:\s*safe\s*)+/gi, "")
    .replace(/\\([*#`_])/g, "$1")
    .replace(/\\n/g, "\n")
    .replace(/&#x20;/gi, " ");
}

export default function App() {
  const [mode, setMode] = useState("chat");
  const [text, setText] = useState("");

  // Saved AI Chat history (persisted across sessions)
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem("chat_messages");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Saved Extraction history (persisted across sessions)
  const [extractions, setExtractions] = useState(() => {
    try {
      const saved = localStorage.getItem("extraction_history");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const [extractStreamText, setExtractStreamText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const chatEndRef = useRef(null);
  const conversationRef = useRef(null);
  const extractEndRef = useRef(null);
  const extractContainerRef = useRef(null);

  // Sync Chat history to localStorage
  useEffect(() => {
    try {
      localStorage.setItem("chat_messages", JSON.stringify(messages));
    } catch {
      // storage unavailable
    }
  }, [messages]);

  // Sync Extraction history to localStorage
  useEffect(() => {
    try {
      localStorage.setItem("extraction_history", JSON.stringify(extractions));
    } catch {
      // storage unavailable
    }
  }, [extractions]);

  // Auto-scroll downward smoothly whenever messages, extractions, loading, or streaming content changes
  const scrollToBottom = useCallback(() => {
    if (mode === "chat") {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
      if (conversationRef.current) {
        conversationRef.current.scrollTop = conversationRef.current.scrollHeight;
      }
    } else {
      extractEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
      if (extractContainerRef.current) {
        extractContainerRef.current.scrollTop = extractContainerRef.current.scrollHeight;
      }
    }
  }, [mode]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, extractions, loading, extractStreamText, scrollToBottom]);

  // Submit action (triggered manually by clicking button or pressing Enter)
  const executeSubmission = useCallback(
    async (textToSubmit) => {
      const trimmed = (textToSubmit !== undefined ? textToSubmit : text).trim();
      if (!trimmed || loading) return;

      setError("");
      setLoading(true);

      if (mode === "chat") {
        setMessages((prev) => [
          ...prev,
          { role: "user", content: trimmed },
          { role: "assistant", content: "" },
        ]);
        setText("");

        try {
          const response = await fetch(`${API}/chat/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: trimmed }),
          });

          if (!response.ok || !response.body) {
            let errorMsg = `Streaming failed (${response.status})`;
            try {
              const errData = await response.json();
              if (errData.detail) errorMsg = errData.detail;
            } catch {
              // ignore json parse fail
            }
            throw new Error(errorMsg);
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
            scrollToBottom();
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
        } catch (err) {
          console.error("Chat request failed:", err);
          setError(err.message || "Chat service error.");
          setMessages((prev) => {
            const next = [...prev];
            if (next.length && next[next.length - 1].role === "assistant") {
              next[next.length - 1] = {
                ...next[next.length - 1],
                content:
                  next[next.length - 1].content ||
                  `Sorry, the request could not be completed: ${err.message}`,
              };
            }
            return next;
          });
        } finally {
          setLoading(false);
        }
      } else {
        // mode === "extract"
        setExtractStreamText("");
        setText("");

        try {
          const response = await fetch(`${API}/extract/stream`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: trimmed }),
          });

          let receivedResult = null;

          if (response.ok && response.body) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
              const { value, done } = await reader.read();
              if (done) break;

              buffer += decoder.decode(value, { stream: true });
              const events = buffer.split(/\r?\n\r?\n/);
              buffer = events.pop() || "";

              for (const event of events) {
                if (!event.trim()) continue;
                const lines = event.split(/\r?\n/);
                for (const line of lines) {
                  if (!line.startsWith("data: ")) continue;
                  const data = JSON.parse(line.slice(6));
                  if (data.error) throw new Error(data.error);
                  if (data.chunk) {
                    setExtractStreamText((prev) => prev + data.chunk);
                  }
                  if (data.done && data.result) {
                    receivedResult = data.result;
                  }
                }
              }
            }

            buffer += decoder.decode();
            if (buffer.trim()) {
              const lines = buffer.split(/\r?\n/);
              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  const data = JSON.parse(line.slice(6));
                  if (data.done && data.result) {
                    receivedResult = data.result;
                  }
                }
              }
            }
          }

          // Fallback to non-streaming /extract if needed
          if (!receivedResult) {
            const fallbackRes = await fetch(`${API}/extract`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ text: trimmed }),
            });
            if (!fallbackRes.ok) {
              const errData = await fallbackRes.json().catch(() => ({}));
              throw new Error(errData.detail || `Extraction failed (${fallbackRes.status})`);
            }
            receivedResult = await fallbackRes.json();
          }

          if (receivedResult) {
            const newEntry = {
              id: Date.now(),
              sourceText: trimmed,
              result: receivedResult,
              timestamp: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
            };
            // Save to extraction history list (append downward: previous above, new below)
            setExtractions((prev) => [...prev, newEntry]);
          }
        } catch (err) {
          console.error("Extraction failed:", err);
          setError(err.message || "Extraction service error.");
        } finally {
          setLoading(false);
          setExtractStreamText("");
        }
      }
    },
    [text, loading, mode, scrollToBottom]
  );

  // Handle manual form submission
  function handleSubmit(e) {
    if (e) e.preventDefault();
    executeSubmission();
  }

  // Suggestion click populates input for manual submit
  function handleSuggestionClick(suggestionText) {
    setText(suggestionText);
  }

  // Handle Enter to submit (Shift+Enter for newline)
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      executeSubmission();
    }
  }

  // Delete a single extraction from history
  function handleDeleteExtraction(id) {
    setExtractions((prev) => prev.filter((item) => item.id !== id));
  }

  // Clear workspace for current mode or both
  function handleClearWorkspace() {
    if (mode === "chat") {
      setMessages([]);
      localStorage.removeItem("chat_messages");
    } else {
      setExtractions([]);
      localStorage.removeItem("extraction_history");
    }
    setExtractStreamText("");
    setError("");
    setText("");
  }

  const chatCount = messages.filter((m) => m.role === "user").length;
  const extractCount = extractions.length;

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
        <div className="topbar-actions">
          <span className="status"><span /> API Workspace</span>
        </div>
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
            <span>
              <strong>AI Chat</strong>
              <small>{chatCount} conversation{chatCount === 1 ? "" : "s"} saved</small>
            </span>
          </button>

          <button
            className={mode === "extract" ? "nav-item active" : "nav-item"}
            onClick={() => {
              setMode("extract");
              setError("");
            }}
          >
            <span>▤</span>
            <span>
              <strong>Text Extractor</strong>
              <small>{extractCount} extraction{extractCount === 1 ? "" : "s"} saved</small>
            </span>
          </button>

          <div className="sidebar-note">
            <span>✧</span>
            <strong>Auto-Saved Workspace</strong>
            <p>Both your Chat messages and Structured Extractions are saved automatically.</p>
          </div>

          <button
            className="clear-btn"
            onClick={handleClearWorkspace}
          >
            Clear {mode === "chat" ? "Chat" : "Extractions"}
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
                    ? "Interactive AI conversation with real-time word-by-word streaming."
                    : "Extract and save structured title, summary, keywords & category with live streaming."}
                </p>
              </div>
            </div>
            <span className="mode-tag">
              {mode === "chat"
                ? `CHAT (${chatCount})`
                : `EXTRACTIONS (${extractCount})`}
            </span>
          </div>

          {mode === "chat" ? (
            <div className="conversation" ref={conversationRef}>
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">✦</div>
                  <h3>What would you like to explore?</h3>
                  <p>Type a message or click a suggestion below:</p>
                  <div className="suggestions">
                    <button onClick={() => handleSuggestionClick("Explain RAG in simple terms.")}>
                      Explain RAG
                    </button>
                    <button onClick={() => handleSuggestionClick("Give me three practical AI project ideas.")}>
                      AI project ideas
                    </button>
                    <button onClick={() => handleSuggestionClick("Who is Babar Azam and what are his records?")}>
                      Babar Azam profile
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
              {loading && <p className="loading-text">✦ AI is streaming response...</p>}
              <div ref={chatEndRef} />
            </div>
          ) : (
            <div className="extract-container" ref={extractContainerRef}>
              {/* Live Streaming Extraction Chunk Preview */}
              {loading && extractStreamText && (
                <div className="streaming-extraction-box">
                  <div className="streaming-extraction-header">
                    <span>✦ Live Extraction Stream:</span>
                    <span className="pulsing-badge">Streaming tokens...</span>
                  </div>
                  <pre className="streaming-pre">{extractStreamText}</pre>
                </div>
              )}

              {extractions.length === 0 && !loading ? (
                <div className="extract-info">
                  <div className="extract-symbol">{"{ }"}</div>
                  <h3>Extract meaningful data</h3>
                  <p>
                    Paste an article, document, or biography. Each extraction will be saved
                    in your history below with title, summary, keywords, and category.
                  </p>
                  <div className="suggestions" style={{ marginTop: "12px" }}>
                    <button
                      onClick={() =>
                        handleSuggestionClick(
                          "Babar Azam is a Pakistani international cricketer and former captain, known for his prolific scoring and batting records in Tests, ODIs, and T20Is."
                        )
                      }
                    >
                      Babar Azam bio
                    </button>
                    <button
                      onClick={() =>
                        handleSuggestionClick(
                          "FastAPI is a modern, fast web framework for building APIs with Python 3.8+ based on standard Python type hints."
                        )
                      }
                    >
                      FastAPI doc
                    </button>
                  </div>
                  <div className="schema-tags">
                    <span>Title</span><span>Summary</span>
                    <span>Keywords</span><span>Category</span>
                  </div>
                </div>
              ) : (
                <div className="extraction-history-list">
                  <div className="extraction-history-header">
                    <strong>Saved Extractions ({extractCount})</strong>
                    {extractCount > 0 && (
                      <span className="history-subtext">Previous extractions above • New extractions below</span>
                    )}
                  </div>

                  {extractions.map((item, idx) => (
                    <div className="extraction-card" key={item.id}>
                      <section className="source-card">
                        <div className="result-heading">
                          <strong>Extraction #{idx + 1}</strong>
                          <div className="result-heading-actions">
                            <span className="timestamp-badge">{item.timestamp}</span>
                            <button
                              type="button"
                              className="delete-item-btn"
                              title="Delete this extraction"
                              onClick={() => handleDeleteExtraction(item.id)}
                            >
                              ✕
                            </button>
                          </div>
                        </div>
                        <p className="source-content">{item.sourceText}</p>
                      </section>

                      <section className="result-box">
                        <div className="result-heading">
                          <strong>Structured Data</strong>
                          <button
                            type="button"
                            onClick={() =>
                              navigator.clipboard.writeText(
                                JSON.stringify(item.result, null, 2)
                              )
                            }
                          >
                            Copy JSON
                          </button>
                        </div>
                        <div className="structured-display">
                          <div className="structured-item">
                            <span className="structured-label">Title</span>
                            <h4>{item.result.title}</h4>
                          </div>
                          <div className="structured-item">
                            <span className="structured-label">Category</span>
                            <span className="category-badge">{item.result.category}</span>
                          </div>
                          <div className="structured-item">
                            <span className="structured-label">Summary</span>
                            <p>{item.result.summary}</p>
                          </div>
                          <div className="structured-item">
                            <span className="structured-label">Keywords</span>
                            <div className="keyword-list">
                              {Array.isArray(item.result.keywords) &&
                                item.result.keywords.map((kw, i) => (
                                  <span key={i} className="keyword-badge">
                                    {kw}
                                  </span>
                                ))}
                            </div>
                          </div>
                        </div>
                        <pre>{JSON.stringify(item.result, null, 2)}</pre>
                      </section>
                    </div>
                  ))}
                  <div ref={extractEndRef} />
                </div>
              )}
            </div>
          )}

          {error && <div className="error-box">{error}</div>}

          <form className="composer" onSubmit={handleSubmit}>
            <label htmlFor="prompt">
              {mode === "chat" ? "YOUR MESSAGE" : "TEXT TO EXTRACT"}
            </label>
            <textarea
              id="prompt"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === "chat"
                  ? "Ask your AI assistant anything (Press Enter to send)..."
                  : "Paste text to extract structured data (Press Enter or click Extract data)..."
              }
              rows={4}
              required
            />
            <div className="composer-footer">
              <span>
                Press Enter to send, Shift+Enter for new line. Output is validated and saved.
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

      <footer>SMART EXTRACTOR <span>•</span> AI WORKSPACE</footer>
    </main>
  );
}
