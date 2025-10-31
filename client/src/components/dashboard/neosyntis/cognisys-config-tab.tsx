import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Network, Eye, EyeOff } from 'lucide-react';
import { mockModels } from '@/lib/dashboard/mockApi';

const modelRoles = [
  { id: 'reasoning', label: 'Reasoning Model', description: 'Deep thinking and problem solving' },
  { id: 'code_generation', label: 'Code Generation', description: 'Generate and refactor code' },
  { id: 'conversation', label: 'Conversation', description: 'Natural dialogue and chat' },
  { id: 'shell_conversion', label: 'Shell Conversion', description: 'Natural language to shell commands' },
  { id: 'summarization', label: 'Summarization', description: 'Condense and summarize content' },
  { id: 'intent_detection', label: 'Intent Detection', description: 'Understand user intentions' },
  { id: 'general', label: 'General Purpose', description: 'Universal model for naming files, etc' },
];

export default function CognisysConfigTab() {
  const [showApiKey, setShowApiKey] = useState(false);
  const [provider, setProvider] = useState('openrouter');

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-primary" />
            COGNISYS Configuration
          </CardTitle>
          <CardDescription>
            Configure API providers, model assignments, and reasoning settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>LLM Provider</Label>
              <Select value={provider} onValueChange={setProvider}>
                <SelectTrigger data-testid="select-provider">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openrouter">OpenRouter</SelectItem>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                  <SelectItem value="google">Google Gemini API</SelectItem>
                  <SelectItem value="huggingface">HuggingFace Inference</SelectItem>
                  <SelectItem value="local">Local Deployment</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>API Key</Label>
              <div className="flex gap-2">
                <Input
                  type={showApiKey ? 'text' : 'password'}
                  placeholder="sk-..."
                  data-testid="input-api-key"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowApiKey(!showApiKey)}
                  data-testid="button-toggle-api-key"
                >
                  {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>API Base URL (optional)</Label>
                <Input placeholder="https://api.openrouter.ai/v1" data-testid="input-api-url" />
              </div>
              <div className="space-y-2">
                <Label>Organization ID (optional)</Label>
                <Input placeholder="org-..." data-testid="input-org-id" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Model Assignment per Role</CardTitle>
          <CardDescription>
            Assign specific models to different tasks for optimal performance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {modelRoles.map((role) => (
            <div key={role.id} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <div className="font-medium">{role.label}</div>
                <div className="text-sm text-muted-foreground">{role.description}</div>
              </div>
              <Select defaultValue="gpt-4">
                <SelectTrigger className="w-[200px]" data-testid={`select-model-${role.id}`}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {mockModels.filter(m => m.isActive).map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      {model.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Reasoning Configuration</CardTitle>
          <CardDescription>
            Enable reasoning for specific models to improve accuracy
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Reasoning adds a thinking step before responses. Enable selectively to balance
              accuracy with token usage and inference speed.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {modelRoles.map((role) => (
                <div key={role.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <Label htmlFor={`reasoning-${role.id}`} className="flex-1 cursor-pointer">
                    {role.label}
                  </Label>
                  <Switch id={`reasoning-${role.id}`} data-testid={`switch-reasoning-${role.id}`} />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Advanced Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Token Limit</Label>
              <Input type="number" defaultValue="4096" data-testid="input-token-limit" />
            </div>
            <div className="space-y-2">
              <Label>Temperature</Label>
              <Input type="number" step="0.1" min="0" max="2" defaultValue="0.7" data-testid="input-temperature" />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Search Engine API Key (optional)</Label>
            <Input placeholder="For Serper or similar providers" data-testid="input-search-api-key" />
          </div>

          <Button className="w-full" data-testid="button-save-config">
            Save Configuration
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
