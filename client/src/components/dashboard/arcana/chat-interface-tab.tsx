import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';

import { Card, CardContent, CardHeader, CardTitle, Button, Input, Badge, ScrollArea, Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui';
import { Send, Paperclip, ChevronDown, Sparkles, Save, Play, Activity } from 'lucide-react';
import { mockChatMessages } from '@/lib/dashboard/mockApi';
import ContextMemoryPanel from './context-memory-panel';

export default function ChatInterfaceTab() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState(mockChatMessages);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMessageMutation = useMutation({
    mutationFn: async (messageContent: string) => {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageContent }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to get reader for streaming response');
      }

      let assistantResponse = '';
      let assistantReasoning = '';
      let isReasoning = false;

      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        // Assuming the backend sends messages in a specific format, e.g.,
        // { "type": "content", "data": "..." }
        // { "type": "reasoning", "data": "..." }
        // { "type": "end" }
        try {
          const parsedChunk = JSON.parse(chunk);
          if (parsedChunk.type === 'content') {
            assistantResponse += parsedChunk.data;
          } else if (parsedChunk.type === 'reasoning') {
            isReasoning = true;
            assistantReasoning += parsedChunk.data;
          }
        } catch (e) {
          // If not JSON, treat as raw content stream
          if (!isReasoning) {
            assistantResponse += chunk;
          } else {
            assistantReasoning += chunk;
          }
        }

        setMessages((prevMessages) => {
          const lastMessage = prevMessages[prevMessages.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            return prevMessages.map((msg, index) =>
              index === prevMessages.length - 1
                ? {
                    ...msg,
                    content: assistantResponse,
                    reasoning: assistantReasoning,
                  }
                : msg
            );
          } else {
            return [
              ...prevMessages,
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: assistantResponse,
                reasoning: assistantReasoning,
                createdAt: new Date(),
              },
            ];
          }
        });
      }
      return { content: assistantResponse, reasoning: assistantReasoning };
    },
    onMutate: (messageContent: string) => {
      const userMessage = {
        id: Date.now().toString(),
        role: 'user' as const,
        content: messageContent,
        createdAt: new Date(),
      };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');
    },
    onError: (error) => {
      console.error('Chat message error:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: Date.now().toString(),
          role: 'assistant' as const,
          content: `Error: ${error.message}`,
          createdAt: new Date(),
        },
      ]);
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    sendMessageMutation.mutate(input);
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
            <Badge variant="outline">GPT-4</Badge>
          </div>
        </div>

        <ScrollArea className="flex-1 px-6 py-4">
          <div className="space-y-6 max-w-4xl mx-auto">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border'
                  }`}
                >
                  {message.reasoning && (
                    <Collapsible className="mb-3">
                      <CollapsibleTrigger className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full">
                        <Sparkles className="h-4 w-4" />
                        <span>Reasoning Process</span>
                        <ChevronDown className="h-4 w-4 ml-auto" />
                      </CollapsibleTrigger>
                      <CollapsibleContent className="mt-2 p-3 bg-muted/50 rounded-md text-sm text-muted-foreground">
                        {message.reasoning}
                      </CollapsibleContent>
                    </Collapsible>
                  )}
                  <div className="text-sm whitespace-pre-wrap leading-relaxed">
                    {message.content}
                  </div>
                  <div className="text-xs text-muted-foreground mt-2 opacity-70">
                    {new Date(message.createdAt).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        <div className="border-t p-4 bg-card/50">
          <div className="max-w-4xl mx-auto space-y-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="outline" className="text-xs">Model: GPT-4</Badge>
              <Badge variant="outline" className="text-xs">Tokens: 2,543 / 8,192</Badge>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="icon" data-testid="button-attach-file">
                <Paperclip className="h-4 w-4" />
              </Button>
              <Input
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                className="flex-1"
                data-testid="input-chat-message"
              />
              <Button onClick={handleSend} disabled={sendMessageMutation.isPending} data-testid="button-send-message">
                {sendMessageMutation.isPending ? <Activity className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <ContextMemoryPanel />
    </div>
  );
}
