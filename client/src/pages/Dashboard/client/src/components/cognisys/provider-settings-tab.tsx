import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Settings, Eye, EyeOff } from 'lucide-react';

const providers = [
  { id: 'openai', name: 'OpenAI', baseUrl: 'https://api.openai.com/v1', enabled: true },
  { id: 'anthropic', name: 'Anthropic', baseUrl: 'https://api.anthropic.com/v1', enabled: true },
  { id: 'google', name: 'Google Gemini', baseUrl: 'https://generativelanguage.googleapis.com/v1', enabled: true },
  { id: 'openrouter', name: 'OpenRouter', baseUrl: 'https://openrouter.ai/api/v1', enabled: true },
  { id: 'huggingface', name: 'HuggingFace', baseUrl: 'https://api-inference.huggingface.co', enabled: false },
];

export default function ProviderSettingsTab() {
  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5 text-primary" />
            Provider Configuration
          </CardTitle>
          <CardDescription>
            Manage API keys and settings for LLM providers
          </CardDescription>
        </CardHeader>
      </Card>

      {providers.map((provider) => (
        <Card key={provider.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">{provider.name}</CardTitle>
                <CardDescription className="text-xs mt-1">
                  {provider.baseUrl}
                </CardDescription>
              </div>
              <Switch checked={provider.enabled} data-testid={`switch-${provider.id}`} />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>API Key</Label>
              <div className="flex gap-2">
                <Input
                  type={showApiKeys[provider.id] ? 'text' : 'password'}
                  placeholder="sk-..."
                  data-testid={`input-api-key-${provider.id}`}
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setShowApiKeys({
                    ...showApiKeys,
                    [provider.id]: !showApiKeys[provider.id]
                  })}
                  data-testid={`button-toggle-${provider.id}`}
                >
                  {showApiKeys[provider.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Base URL (optional)</Label>
                <Input defaultValue={provider.baseUrl} data-testid={`input-base-url-${provider.id}`} />
              </div>
              <div className="space-y-2">
                <Label>Organization ID (optional)</Label>
                <Input placeholder="org-..." data-testid={`input-org-id-${provider.id}`} />
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="sm" data-testid={`button-test-${provider.id}`}>
                Test Connection
              </Button>
              <Button size="sm" data-testid={`button-save-${provider.id}`}>
                Save
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Multi-Provider Benefits</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <ul className="list-disc list-inside space-y-1">
            <li>Automatic failover if one provider is down</li>
            <li>Cost optimization by routing to cheaper models</li>
            <li>Access to specialized models from different providers</li>
            <li>No vendor lock-in, freedom to switch providers</li>
            <li>Load balancing across multiple providers</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
