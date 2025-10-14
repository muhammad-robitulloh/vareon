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
    { role: "assistant", content: "Hello! I'm NeuroNet AI. I can help you with code generation, shell commands, or general conversation. What would you like to work on?", type: "text" }
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: "user", content: input, type: "text" };
    setMessages(prev => [...prev, userMessage]);

    // Mock AI response
    setTimeout(() => {
      const responses = [
        { content: "I can help you with that. Here's a Python example:", type: "code" as const, language: "python" },
        { content: "Let me execute that command for you...", type: "command" as const },
        { content: "Based on my analysis, I recommend...", type: "text" as const }
      ];
      const response = responses[Math.floor(Math.random() * responses.length)];
      
      const aiMessage: Message = { 
        role: "assistant", 
        content: response.type === "code" 
          ? "def hello_world():\n    print('Hello from NeuroNet!')\n    return True" 
          : response.type === "command"
          ? "ls -la | grep .py"
          : "I've processed your request. The intent has been detected and I'm ready to proceed with the appropriate action.",
        type: response.type,
        language: response.language
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 800);

    setInput("");
  };

  return (
    <div className="flex h-[600px] flex-col rounded-xl border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border p-4">
        <div className="flex items-center space-x-2">
          <Bot className="h-5 w-5 text-primary" />
          <span className="font-semibold text-foreground">NeuroNet AI</span>
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
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
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
                    ? "bg-muted font-mono text-sm"
                    : msg.type === "command"
                    ? "bg-muted font-mono text-sm"
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
      </div>

      <div className="border-t border-border p-4">
        <div className="flex space-x-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask NeuroNet AI anything..."
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
