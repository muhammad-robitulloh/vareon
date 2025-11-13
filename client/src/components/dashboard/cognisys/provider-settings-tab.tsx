import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Label, Switch } from '@/components/ui';
import { Settings, Eye, EyeOff, Plus, Trash2, Save, TestTube, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/use-auth';

// --- Interfaces ---
interface LLMProvider {
  id: string;
  name: string;
  base_url: string;
  api_key_encrypted: string; // This will be handled securely on backend
  masked_api_key?: string; // New: Masked API key for display
  enabled: boolean;
  organization_id?: string;
  created_at: string;
  updated_at: string;
}

interface LLMProviderCreateUpdate {
  name: string;
  base_url: string;
  api_key?: string; // Raw key for sending to backend, now optional
  enabled: boolean;
  organization_id?: string;
}

export default function ProviderSettingsTab() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { token } = useAuth();

  const [showApiKeys, setShowApiKeys] = useState<Record<string, boolean>>({});
  const [changeApiKey, setChangeApiKey] = useState<boolean>(false);
  const [editingProviderId, setEditingProviderId] = useState<string | null>(null);
  const [providerForm, setProviderForm] = useState<LLMProviderCreateUpdate>({
    name: '',
    base_url: '',
    api_key: '',
    enabled: true,
    organization_id: '',
  });

  // --- Fetch Providers ---
  const { data: providers, isLoading, error } = useQuery<LLMProvider[]>({
    queryKey: ['cognisysLLMProviders'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/providers/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LLM providers');
      }
      return response.json();
    },
    enabled: !!token,
  });

  // --- Create Provider Mutation ---
  const createProviderMutation = useMutation({
    mutationFn: async (newProvider: LLMProviderCreateUpdate) => {
      const response = await fetch('/api/cognisys/providers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newProvider),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create LLM provider');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'LLM Provider created.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMProviders'] });
      setProviderForm({ name: '', base_url: '', api_key: '', enabled: true, organization_id: '' }); // Clear form
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    },
  });

  // --- Update Provider Mutation ---
  const updateProviderMutation = useMutation({
    mutationFn: async ({ id, updatedProvider }: { id: string; updatedProvider: LLMProviderCreateUpdate }) => {
      const response = await fetch(`/api/cognisys/providers/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(updatedProvider),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update LLM provider');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'LLM Provider updated.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMProviders'] });
      setEditingProviderId(null); // Exit editing mode
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    },
  });

  // --- Delete Provider Mutation ---
  const deleteProviderMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/cognisys/providers/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete LLM provider');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'LLM Provider deleted.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMProviders'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    },
  });

  // --- Test Connection Mutation ---
  const testConnectionMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/cognisys/providers/${id}/test-connection`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to test connection');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast({ title: 'Connection Test', description: data.message, variant: data.status === 'success' ? 'default' : 'destructive' });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Connection test failed: ${err.message}`, variant: 'destructive' });
    },
  });

  const handleEditClick = (provider: LLMProvider) => {
    setEditingProviderId(provider.id);
    setChangeApiKey(false); // Reset to false when starting edit
    setProviderForm({
      name: provider.name,
      base_url: provider.base_url,
      api_key: provider.masked_api_key || '', // Display masked key
      enabled: provider.enabled,
      organization_id: provider.organization_id || '',
    });
  };

  const handleSaveProvider = (id: string) => {
    const updatedProviderData = {
      name: providerForm.name,
      base_url: providerForm.base_url,
      enabled: providerForm.enabled,
      organization_id: providerForm.organization_id,
      ...(changeApiKey && { api_key: providerForm.api_key }), // Only include api_key if changeApiKey is true
    };
    updateProviderMutation.mutate({ id, updatedProvider: updatedProviderData });
  };

  const handleCreateProvider = () => {
    createProviderMutation.mutate(providerForm);
  };

  if (isLoading) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading providers...</div>;
  if (error) return <div className="p-4 text-center text-red-500">Error: {error.message}</div>;

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

      {/* Form for New Provider */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Plus className="h-5 w-5" /> Add New Provider
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="new-provider-name">Name</Label>
              <Input
                id="new-provider-name"
                placeholder="e.g., OpenAI, Google Gemini"
                value={providerForm.name}
                onChange={(e) => setProviderForm({ ...providerForm, name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="new-provider-base-url">Base URL</Label>
              <Input
                id="new-provider-base-url"
                placeholder="e.g., https://api.openai.com/v1"
                value={providerForm.base_url}
                onChange={(e) => setProviderForm({ ...providerForm, base_url: e.target.value })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-provider-api-key">API Key</Label>
            <div className="flex gap-2">
              <Input
                id="new-provider-api-key"
                type={showApiKeys['new'] ? 'text' : 'password'}
                placeholder="sk-..."
                value={providerForm.api_key}
                onChange={(e) => setProviderForm({ ...providerForm, api_key: e.target.value })}
              />
              <Button
                variant="outline"
                size="icon"
                onClick={() => setShowApiKeys({ ...showApiKeys, new: !showApiKeys['new'] })}
              >
                {showApiKeys['new'] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-provider-org-id">Organization ID (optional)</Label>
            <Input
              id="new-provider-org-id"
              placeholder="org-..."
              value={providerForm.organization_id}
              onChange={(e) => setProviderForm({ ...providerForm, organization_id: e.target.value })}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="new-provider-enabled"
              checked={providerForm.enabled}
              onCheckedChange={(checked) => setProviderForm({ ...providerForm, enabled: checked })}
            />
            <Label htmlFor="new-provider-enabled">Enabled</Label>
          </div>
          <Button
            className="w-full"
            onClick={handleCreateProvider}
            disabled={createProviderMutation.isPending || !providerForm.name || !providerForm.base_url || !providerForm.api_key}
          >
            {createProviderMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
            Create Provider
          </Button>
        </CardContent>
      </Card>

      {/* Existing Providers */}
      {providers?.map((provider) => (
        <Card key={provider.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">{provider.name}</CardTitle>
                <CardDescription className="text-xs mt-1">
                  {provider.base_url}
                </CardDescription>
              </div>
              <Switch
                checked={provider.enabled}
                onCheckedChange={(checked) => updateProviderMutation.mutate({
                  id: provider.id,
                  updatedProvider: { ...provider, enabled: checked, api_key: '' } // API key not sent for simple toggle
                })}
                disabled={updateProviderMutation.isPending}
              />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {editingProviderId === provider.id ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor={`edit-name-${provider.id}`}>Name</Label>
                    <Input
                      id={`edit-name-${provider.id}`}
                      value={providerForm.name}
                      onChange={(e) => setProviderForm({ ...providerForm, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor={`edit-base-url-${provider.id}`}>Base URL</Label>
                    <Input
                      id={`edit-base-url-${provider.id}`}
                      value={providerForm.base_url}
                      onChange={(e) => setProviderForm({ ...providerForm, base_url: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor={`edit-api-key-${provider.id}`}>API Key</Label>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id={`change-api-key-switch-${provider.id}`}
                      checked={changeApiKey}
                      onCheckedChange={setChangeApiKey}
                    />
                    <Label htmlFor={`change-api-key-switch-${provider.id}`}>Change API Key</Label>
                  </div>
                  {changeApiKey ? (
                    <div className="flex gap-2">
                      <Input
                        id={`edit-api-key-${provider.id}`}
                        type={showApiKeys[provider.id] ? 'text' : 'password'}
                        placeholder="sk-..."
                        value={providerForm.api_key}
                        onChange={(e) => setProviderForm({ ...providerForm, api_key: e.target.value })}
                      />
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => setShowApiKeys({ ...showApiKeys, [provider.id]: !showApiKeys[provider.id] })}
                      >
                        {showApiKeys[provider.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                    </div>
                  ) : (
                    <Input
                      id={`edit-api-key-${provider.id}`}
                      type="text"
                      value={provider.masked_api_key || ''}
                      readOnly
                      className="font-mono"
                    />
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor={`edit-org-id-${provider.id}`}>Organization ID (optional)</Label>
                  <Input
                    id={`edit-org-id-${provider.id}`}
                    value={providerForm.organization_id}
                    onChange={(e) => setProviderForm({ ...providerForm, organization_id: e.target.value })}
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => handleSaveProvider(provider.id)}
                    disabled={updateProviderMutation.isPending}
                  >
                    {updateProviderMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                    Save Changes
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => setEditingProviderId(null)}>
                    Cancel
                  </Button>
                </div>
              </>
            ) : (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => handleEditClick(provider)}>
                  <Settings className="h-4 w-4 mr-2" /> Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => testConnectionMutation.mutate(provider.id)}
                  disabled={testConnectionMutation.isPending}
                >
                  {testConnectionMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <TestTube className="h-4 w-4 mr-2" />}
                  Test Connection
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => deleteProviderMutation.mutate(provider.id)}
                  disabled={deleteProviderMutation.isPending}
                >
                  {deleteProviderMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Trash2 className="h-4 w-4 mr-2" />}
                  Delete
                </Button>
              </div>
            )}
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
