// DAUBA/frontend/src/App.jsx
import { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

function detectLanguage(path) {
  if (!path) return "plaintext";
  const ext = path.split(".").pop();
  if (["js", "jsx", "ts", "tsx"].includes(ext)) return "javascript";
  if (["py"].includes(ext)) return "python";
  if (["sh", "bash"].includes(ext)) return "bash";
  if (["json"].includes(ext)) return "json";
  if (["html"].includes(ext)) return "html";
  if (["css", "scss", "less"].includes(ext)) return "css";
  if (["md"].includes(ext)) return "markdown";
  if (["yml", "yaml"].includes(ext)) return "yaml";
  return "plaintext";
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [responseMessage, setResponseMessage] = useState("");
  const [currentWrite, setCurrentWrite] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastPromptForRejection, setLastPromptForRejection] = useState("");

  const BACKEND_URL = "http://192.168.20.22:8000";

  const handleSend = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsProcessing(true);
    setResponseMessage("Thinking...");
    setCurrentWrite(null);
    setLastPromptForRejection(prompt);

    try {
      const res = await fetch(`${BACKEND_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: `HTTP error! status: ${res.status}` }));
          throw new Error(errorData.detail);
      }
      const data = await res.json();
      if (data.pending_write_id) {
        setCurrentWrite({
          id: data.pending_write_id,
          filePath: data.file_path,
          code: data.code,
          originalPrompt: prompt
        });
        setResponseMessage("");
      } else if (data.output) {
        setResponseMessage(data.output);
      } else {
        setResponseMessage("Received an unexpected response format from the server.");
      }
    } catch (err) {
      setResponseMessage(`Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleApproveWrite = async () => {
    if (!currentWrite) return;
    setIsProcessing(true);
    setResponseMessage("Writing file...");
    try {
      const res = await fetch(`${BACKEND_URL}/confirm_write`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pending_id: currentWrite.id }),
      });
      if (!res.ok) {
          const errorData = await res.json().catch(() => ({ detail: `HTTP error! status: ${res.status}` }));
          throw new Error(errorData.detail);
      }
      const data = await res.json();
      setResponseMessage(`${currentWrite.code}\n\n---\n\n${data.write_result}`);
      setCurrentWrite(null);
    } catch (err) {
      setResponseMessage(`Error writing file: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRejectWrite = async () => {
    if (!currentWrite) return;
    setIsProcessing(true);
    setResponseMessage("Cancelling write...");
    try {
      await fetch(`${BACKEND_URL}/reject_write`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pending_id: currentWrite.id, prompt: lastPromptForRejection }),
      });
      setResponseMessage("File write cancelled.");
      setCurrentWrite(null);
    } catch (err) {
      setResponseMessage(`Error cancelling write: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const renderPendingWrite = () => (
    <div style={{ border: "1px solid #4f70d9", borderRadius: 8, padding: 16, background: "#282c34", marginBottom: 16 }}>
      <div style={{ marginBottom: 8 }}>
        <strong>Review File Change:</strong><br />
        <span style={{ color: "#4f70d9", fontWeight: 'bold' }}>{currentWrite.filePath}</span>
      </div>
      <SyntaxHighlighter language={detectLanguage(currentWrite.filePath)} style={oneDark} customStyle={{ borderRadius: 6, fontSize: 15, maxHeight: 400, overflowY: 'auto' }}>
        {currentWrite.code}
      </SyntaxHighlighter>
      <div style={{ display: "flex", gap: 16, marginTop: 16 }}>
        <button onClick={handleApproveWrite} disabled={isProcessing} style={{ backgroundColor: "#4CAF50", color: "white", padding: "10px 15px", border: "none", borderRadius: 5, cursor: "pointer" }}>
          Approve and Write File
        </button>
        <button onClick={handleRejectWrite} disabled={isProcessing} style={{ backgroundColor: "#f44336", color: "white", padding: "10px 15px", border: "none", borderRadius: 5, cursor: "pointer" }}>
          Reject
        </button>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", background: "#222", fontFamily: "sans-serif", padding: "20px", boxSizing: "border-box" }}>
      <div style={{ maxWidth: 720, width: "100%", background: "#333", padding: "20px", borderRadius: 10 }}>
        <h1 style={{ color: "#fafafa", textAlign: "center", marginBottom: "20px" }}>DAUBA Workbench</h1>
        {currentWrite && renderPendingWrite()}
        {!currentWrite && responseMessage && (
          <div style={{ whiteSpace: "pre-wrap", background: "#444", borderRadius: 8, padding: 16, minHeight: 80, color: "#fafafa", marginBottom: "20px", border: responseMessage.startsWith("Error:") ? "1px solid #f44336" : "1px solid #555" }}>
            {responseMessage}
          </div>
        )}
        <form onSubmit={handleSend} style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: "20px" }}>
          <textarea rows={6} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder='Enter your prompt...' disabled={isProcessing} style={{ padding: "12px", borderRadius: 8, border: "1px solid #555", background: "#444", color: "#fafafa", fontSize: "16px", resize: "vertical" }} />
          <button type="submit" disabled={isProcessing || !prompt.trim()} style={{ padding: "12px 20px", borderRadius: 8, background: "#007bff", color: "white", fontSize: "16px", border: "none", cursor: "pointer", opacity: isProcessing || !prompt.trim() ? 0.6 : 1 }}>
            {isProcessing ? "Processing..." : "Send Prompt"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;