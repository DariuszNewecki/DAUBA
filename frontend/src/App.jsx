// DAUBA/frontend/src/App.jsx

import { useState } from "react";

function extractWriteMarker(output) {
  // Find [[write:...]]
  const marker = /\[\[write:(.+?)\]\]\s*\n?([\s\S]*)/m;
  const match = output.match(marker);
  if (match) {
    return {
      path: match[1].trim(),
      code: match[2].trim(),
    };
  }
  return null;
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [writing, setWriting] = useState(false);
  const [pendingWrite, setPendingWrite] = useState(null);

  const handleSend = async (e) => {
    e.preventDefault();
    setWriting(true);
    setResponse("...");
    setPendingWrite(null);
    try {
      const res = await fetch("http://192.168.20.22:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await res.json();
      const writeData = extractWriteMarker(data.output);
      if (writeData) {
        setPendingWrite(writeData);
        setResponse(`File to write: ${writeData.path}\n\n${writeData.code}`);
      } else {
        setResponse(data.output || data.error);
      }
    } catch (err) {
      setResponse("Error: " + err.message);
    }
    setWriting(false);
  };

  const handleApprove = async () => {
    if (!pendingWrite) return;
    setWriting(true);
    setResponse("Writing file...");
    try {
      const res = await fetch("http://192.168.20.22:8000/write_file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pendingWrite),
      });
      const data = await res.json();
      setResponse(`${pendingWrite.code}\n\n${data.write_result}`);
      setPendingWrite(null);
    } catch (err) {
      setResponse("Error: " + err.message);
    }
    setWriting(false);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        background: "#222",
        fontFamily: "sans-serif"
      }}
    >
      <div style={{ maxWidth: 540, width: "100%" }}>
        <h1 style={{ color: "#fafafa" }}>DAUBA Workbench</h1>
        <form onSubmit={handleSend} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder='Enter your prompt (e.g. "Say hello, DAUBA!")'
            disabled={writing}
          />
          <button type="submit" disabled={writing || !prompt.trim()}>
            {writing ? "Thinking..." : "Send"}
          </button>
        </form>
        <div style={{
          marginTop: 24,
          whiteSpace: "pre-wrap",
          background: "#fafafa",
          borderRadius: 8,
          padding: 16,
          minHeight: 80,
          color: "#222"
        }}>
          {response}
          {pendingWrite && (
            <div style={{ marginTop: 16 }}>
              <button onClick={handleApprove} disabled={writing}>
                Approve and Write File
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
