import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, Bot, User, Code, Terminal } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  type?: "text" | "code" | "command";
  language?: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello! I'm Arcana AI. I can help you with code generation, shell commands, or general conversation. What would you like to work on?", type: "text" }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false); // New state for typing indicator

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input, type: "text" };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8001/api/chat/demo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: currentInput }),
      });

      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }

      const data = await response.json();
      
      const aiMessage: Message = { 
        role: "assistant", 
        content: data.response || "Sorry, I couldn't get a response.",
        type: "text" // Assuming the response is always text for now
      };
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = { 
        role: "assistant", 
        content: "Sorry, something went wrong. Please try again later.",
        type: "text"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex h-[600px] flex-col rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border p-4">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-primary" />
          <span className="font-semibold text-foreground">Arcana AI</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="h-2 w-2 rounded-full bg-chart-3" />
          <span className="text-sm text-muted-foreground">Online</span>
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex animate-fade-in-up ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`flex max-w-[80%] space-x-2 ${msg.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}>
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                msg.role === "user" ? "bg-primary" : "bg-muted"
              }`}>
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-primary-foreground" />
                ) : (
                  <Bot className="h-4 w-4 text-foreground" />
                )}
              </div>
              <div
                className={`rounded-xl p-3 ${
                  msg.role === "user"
                    ? "bg-primary/20 text-foreground"
                    : msg.type === "code"
                    ? "bg-muted font-mono text-sm border border-border"
                    : msg.type === "command"
                    ? "bg-muted font-mono text-sm border border-border"
                    : "bg-muted text-foreground"
                }`}
              >
                {msg.type === "code" && (
                  <div className="mb-2 flex items-center space-x-2">
                    <Code className="h-4 w-4 text-primary" />
                    <span className="text-xs text-muted-foreground">{msg.language || "code"}</span>
                  </div>
                )}
                {msg.type === "command" && (
                  <div className="mb-2 flex items-center space-x-2">
                    <Terminal className="h-4 w-4 text-primary" />
                    <span className="text-xs text-muted-foreground">shell</span>
                  </div>
                )}
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="flex max-w-[80%] space-x-2">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
                <Bot className="h-4 w-4 text-foreground" />
              </div>
              <div className="rounded-xl p-3 bg-muted text-foreground">
                <div className="flex items-center space-x-1">
                  <span className="animate-pulse-dot">.</span>
                  <span className="animate-pulse-dot animation-delay-100">.</span>
                  <span className="animate-pulse-dot animation-delay-200">.</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-border p-4">
        <div className="flex space-x-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Arcana AI anything..."
            className="min-h-[60px] resize-none"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            data-testid="input-chat-message"
          />
          <Button onClick={handleSend} size="icon" className="shrink-0" data-testid="button-send-message">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
