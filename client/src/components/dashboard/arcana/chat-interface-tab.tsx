import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge, ScrollArea, Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui';
import { Send, Paperclip, ChevronDown, Sparkles, Activity, PanelRightOpen, WifiOff } from 'lucide-react';
import ContextMemoryPanel from './context-memory-panel';

// Define message structure
interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    reasoning?: string;
    createdAt: Date;
}

export default function ChatInterfaceTab() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isContextPanelOpen, setIsContextPanelOpen] = useState(true);
  const [isConnecting, setIsConnecting] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const sessionId = crypto.randomUUID();
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const accessToken = localStorage.getItem("access_token");
    const wsUrl = `${protocol}//${window.location.host}/ws-api/ws/arcana/${sessionId}?token=${accessToken}`;

    const socket = new WebSocket(wsUrl);
    ws.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
      setIsConnecting(false);
      setIsConnected(true);
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnecting(false);
      setIsConnected(false);
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnecting(false);
      setIsConnected(false);
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'chat_response') {
        setMessages(prevMessages => {
            const lastMessage = prevMessages[prevMessages.length - 1];
            // If last message is from assistant, update it (for streaming)
            if (lastMessage && lastMessage.role === 'assistant') {
                return prevMessages.map((msg, index) => 
                    index === prevMessages.length - 1 
                    ? { ...msg, content: msg.content + message.payload.response } 
                    : msg
                );
            }
            // Otherwise, add a new assistant message
            return [...prevMessages, {
                id: message.payload.message_id || crypto.randomUUID(),
                role: 'assistant',
                content: message.payload.response,
                createdAt: new Date(),
            }];
        });
      }
    };

    // Cleanup on component unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []); // Empty dependency array ensures this runs only once on mount

  const handleSend = () => {
    if (!input.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) {
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      createdAt: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    const event = {
      type: 'chat_message',
      payload: { prompt: input },
    };
    ws.current.send(JSON.stringify(event));

    // Add a placeholder for the assistant's response
    setMessages(prev => [...prev, {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '', // Start with empty content
        createdAt: new Date(),
    }]);

    setInput('');
  };

  return (
    <div className="h-full flex">
      <div className="flex-1 flex flex-col">
        <div className="border-b px-6 py-3 bg-card/50">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Chat with ARCANA</h3>
              <p className="text-sm text-muted-foreground">Cognitive AI Assistant</p>
            </div>
            <div className="flex items-center gap-2">
                {isConnecting ? <Badge variant="outline"><Activity className="h-3 w-3 mr-1 animate-spin" />Connecting...</Badge> 
                : isConnected ? <Badge variant="secondary" className="bg-green-500 text-white">Connected</Badge>
                : <Badge variant="destructive"><WifiOff className="h-3 w-3 mr-1" />Disconnected</Badge>}
                <Button variant="ghost" size="icon" onClick={() => setIsContextPanelOpen(!isContextPanelOpen)}>
                    <PanelRightOpen className="h-5 w-5" />
                </Button>
            </div>
          </div>
        </div>

        <ScrollArea className="flex-1 px-6 py-4">
          <div className="space-y-6 max-w-4xl mx-auto">
            {messages.map((message) => (
              <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg p-4 ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card border'}`}>
                  {message.reasoning && (
                    <Collapsible className="mb-3">
                      <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full">
                        <Sparkles className="h-4 w-4" /><span>Reasoning Process</span><ChevronDown className="h-4 w-4 ml-auto" />
                      </CollapsibleTrigger>
                      <CollapsibleContent className="mt-2 p-3 bg-muted/50 rounded-md text-sm text-muted-foreground">{message.reasoning}</CollapsibleContent>
                    </Collapsible>
                  )}
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">{message.content || <Activity className="h-4 w-4 animate-spin" />}</div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">{new Date(message.createdAt).toLocaleTimeString()}</div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        <div className="border-t p-4 bg-card/50">
          <div className="max-w-4xl mx-auto space-y-3">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" data-testid="button-attach-file"><Paperclip className="h-4 w-4" /></Button>
              <Input
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                className="flex-1"
                data-testid="input-chat-message"
                disabled={!isConnected}
              />
              <Button onClick={handleSend} disabled={!isConnected || isConnecting} data-testid="button-send-message">
                {isConnecting ? <Activity className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>
      </div>
      {isContextPanelOpen && <ContextMemoryPanel />}
    </div>
  );
}
