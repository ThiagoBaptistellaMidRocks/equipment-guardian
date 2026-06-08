import { Bot, Send, User, X } from "lucide-react";
import { useMemo, useState } from "react";

import { postCopilotChat } from "../services/assets";

interface CopilotPanelProps {
  isOpen: boolean;
  selectedAssetId: string | null;
  onClose: () => void;
}

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

function defaultPrompt(selectedAssetId: string | null): string {
  if (selectedAssetId) {
    return `Why is ${selectedAssetId} at risk?`;
  }
  return "Give me the current fleet risk summary.";
}

export function CopilotPanel({ isOpen, selectedAssetId, onClose }: CopilotPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emptyStatePrompt = useMemo(() => defaultPrompt(selectedAssetId), [selectedAssetId]);

  async function sendMessage(rawText: string) {
    const message = rawText.trim();
    if (!message || isSending) {
      return;
    }

    setError(null);
    setIsSending(true);
    setInput("");
    setMessages((previous) => [...previous, { role: "user", text: message }]);

    try {
      const response = await postCopilotChat({ message });
      setMessages((previous) => [...previous, { role: "assistant", text: response.response }]);
    } catch {
      setError("Unable to reach Equipment Guardian Copilot right now.");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <aside className={`copilot-panel ${isOpen ? "open" : ""}`} aria-label="Equipment Guardian Copilot">
      <header className="copilot-header">
        <div>
          <h3>Equipment Guardian Copilot</h3>
          <span>Operational Intelligence Assistant</span>
        </div>
        <button className="close-button" type="button" onClick={onClose} aria-label="Close copilot panel">
          <X size={18} />
        </button>
      </header>

      <div className="copilot-messages">
        {messages.length === 0 ? (
          <section className="copilot-empty-state">
            <p>Ask about asset health, predictions, incidents, timelines, or fleet analytics.</p>
            <button type="button" onClick={() => sendMessage(emptyStatePrompt)}>
              {emptyStatePrompt}
            </button>
          </section>
        ) : (
          messages.map((message, index) => (
            <article className={`chat-message ${message.role}`} key={`${message.role}-${index}`}>
              <span className="chat-role-icon">{message.role === "assistant" ? <Bot size={14} /> : <User size={14} />}</span>
              <p>{message.text}</p>
            </article>
          ))
        )}
      </div>

      {error ? <p className="copilot-error">{error}</p> : null}

      <form
        className="copilot-compose"
        onSubmit={(event) => {
          event.preventDefault();
          void sendMessage(input);
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask why an asset is at risk..."
          disabled={isSending}
        />
        <button type="submit" disabled={isSending || !input.trim()} aria-label="Send message">
          <Send size={15} />
        </button>
      </form>
    </aside>
  );
}
