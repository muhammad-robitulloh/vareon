import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Terminal, Send, Trash2 } from 'lucide-react';

export default function TestConsoleTab() {
  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('auto');
  const [messages, setMessages] = useState<Array<{
    role: 'user' | 'assistant';
    content: string;
    model?: string;
    tokens?: number;
  }>>([]);

  const handleSend = () => {
    if (!prompt.trim()) return;

    setMessages([
      ...messages,
      { role: 'user', content: prompt },
      {
        role: 'assistant',
        content: 'This is a mock response from the model. In production, this would be the actual LLM output based on your configured routing rules.',
        model: selectedModel === 'auto' ? 'GPT-4 (auto-routed)' : selectedModel,
        tokens: Math.floor(Math.random() * 500) + 100,
      },
    ]);
    setPrompt('');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5 text-primary" />
            Test Console
          </CardTitle>
          <CardDescription>
            Test prompts and verify routing behavior
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Select value={selectedModel} onValueChange={setSelectedModel}>
              <SelectTrigger className="w-[200px]" data-testid="select-test-model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto-route</SelectItem>
                <SelectItem value="gpt-4">GPT-4</SelectItem>
                <SelectItem value="claude">Claude-3.5</SelectItem>
                <SelectItem value="codestral">Codestral</SelectItem>
                <SelectItem value="gemini">Gemini-Pro</SelectItem>
              </SelectContent>
            </Select>

            <Input
              placeholder="Enter test prompt..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              className="flex-1"
              data-testid="input-test-prompt"
            />

            <Button onClick={handleSend} data-testid="button-send-test">
              <Send className="h-4 w-4" />
            </Button>

            {messages.length > 0 && (
              <Button
                variant="outline"
                onClick={() => setMessages([])}
                data-testid="button-clear-console"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {messages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Conversation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  {message.model && (
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="text-xs">
                        {message.model}
                      </Badge>
                      {message.tokens && (
                        <span className="text-xs text-muted-foreground">
                          {message.tokens} tokens
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {messages.length === 0 && (
        <Card className="p-12">
          <div className="text-center space-y-2">
            <Terminal className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
            <h3 className="text-lg font-medium">No messages yet</h3>
            <p className="text-sm text-muted-foreground">
              Enter a prompt above to test your routing configuration
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}
