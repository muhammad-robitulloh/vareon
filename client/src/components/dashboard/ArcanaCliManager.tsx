import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { format } from 'date-fns';
import { Copy, Trash2, Loader2, Eye, EyeOff } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { TypewriterEffect } from '@/components/TypewriterEffect'; // Import TypewriterEffect

interface ArcanaApiKey {
  id: string;
  name: string;
  key: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
}

interface UserCliConfig {
  id: string;
  key: string;
  value: string;
  created_at: string;
  updated_at: string;
}

export default function ArcanaCliManager() {
  const { toast } = useToast();
  const [apiKeys, setApiKeys] = useState<ArcanaApiKey[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [loading, setLoading] = useState(true);
  const [generatingKey, setGeneratingKey] = useState(false);
  const [deactivatingKey, setDeactivatingKey] = useState<string | null>(null);
  const [confirmDeactivateKeyId, setConfirmDeactivateKeyId] = useState<string | null>(null); // State for confirmation dialog
  const [revealedKeyId, setRevealedKeyId] = useState<string | null>(null); // State to track revealed key

  // States for CLI Demo Animation
  const [cliDemoOutput, setCliDemoOutput] = useState<string[]>([]);
  const [showCursor, setShowCursor] = useState(false);
  const fullCliDemoScript = [
    "> arcana login --key <YOUR_API_KEY>",
    "Successfully authenticated with Arcana CLI.",
    "> arcana agent list",
    "Fetching available agents...",
    "  ID        NAME",
    "  --------------------",
    "  agent-1   CodeGenerator",
    "  agent-2   DataAnalyzer",
    "  agent-3   ResearchAssistant",
    "> arcana task create --agent CodeGenerator --prompt \"Develop a Python script for data parsing.\"",
    "Task 'develop-python-script' created successfully.",
    "Monitoring task 'develop-python-script'...",
    "Task 'develop-python-script' completed. Output saved to 'output/develop-python-script.py'."
  ];

  useEffect(() => {
    let currentScriptIndex = 0;
    let timeout: NodeJS.Timeout;

    const runScriptLine = () => {
      if (currentScriptIndex < fullCliDemoScript.length) {
        const line = fullCliDemoScript[currentScriptIndex];
        setCliDemoOutput((prev) => [...prev, line]);
        currentScriptIndex++;
        setShowCursor(true); // Show cursor while typing
        timeout = setTimeout(() => {
          setShowCursor(false); // Hide cursor after line is typed
          runScriptLine();
        }, line.length * 50 + 1000); // Adjust delay based on line length and add a pause
      }
    };

    // Initial delay before starting the demo
    const initialTimeout = setTimeout(() => {
      runScriptLine();
    }, 1000);

    return () => {
      clearTimeout(timeout);
      clearTimeout(initialTimeout);
    };
  }, []);

  // CLI Config states
  const [cliConfigs, setCliConfigs] = useState<UserCliConfig[]>([]);
  const [newConfigKey, setNewConfigKey] = useState('');
  const [newConfigValue, setNewConfigValue] = useState('');
  const [loadingConfigs, setLoadingConfigs] = useState(true);
  const [settingConfig, setSettingConfig] = useState(false);
  const [deletingConfig, setDeletingConfig] = useState<string | null>(null);

  // New states for specific CLI configurations
  const [availableAgents, setAvailableAgents] = useState<{ id: string; name: string }[]>([]);
  const [availableModels, setAvailableModels] = useState<{ id: string; name: string }[]>([]);
  const [defaultAgentId, setDefaultAgentId] = useState<string>('');
  const [preferredModel, setPreferredModel] = useState<string>('');

  const toggleRevealKey = (keyId: string) => {
    setRevealedKeyId(revealedKeyId === keyId ? null : keyId);
  };

  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const response = await api.get('/arcana/api-keys/');
      setApiKeys(response);
    } catch (error: any) {
      toast({
        title: 'Error fetching API keys',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCliConfigs = async () => {
    setLoadingConfigs(true);
    try {
      const response = await api.get('/arcana/cli-configs/');
      setCliConfigs(response);
    } catch (error: any) {
      toast({
        title: 'Error fetching CLI configurations',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setLoadingConfigs(false);
    }
  };

  const fetchAvailableAgents = async () => {
    try {
      const response = await api.get('/arcana/agents/'); // Assuming this endpoint exists
      setAvailableAgents(response);
    } catch (error: any) {
      toast({
        title: 'Error fetching agents',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    }
  };

  const fetchAvailableModels = async () => {
    try {
      const response = await api.get('/cognisys/models/'); // Assuming this endpoint exists
      setAvailableModels(response);
    } catch (error: any) {
      toast({
        title: 'Error fetching models',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    }
  };

  useEffect(() => {
    fetchApiKeys();
    fetchCliConfigs();
    fetchAvailableAgents();
    fetchAvailableModels();
  }, []);

  useEffect(() => {
    // Initialize defaultAgentId and preferredModel from fetched cliConfigs
    const defaultAgentConfig = cliConfigs.find(config => config.key === 'default_agent_id');
    if (defaultAgentConfig) {
      setDefaultAgentId(defaultAgentConfig.value);
    }
    const preferredModelConfig = cliConfigs.find(config => config.key === 'preferred_model');
    if (preferredModelConfig) {
      setPreferredModel(preferredModelConfig.value);
    }
  }, [cliConfigs]);

  const handleGenerateKey = async () => {
    if (!newKeyName.trim()) {
      toast({
        title: 'API Key name is required',
        variant: 'destructive',
      });
      return;
    }

    setGeneratingKey(true);
    try {
      const response = await api.post('/arcana/api-keys/', { name: newKeyName });
      setApiKeys((prevKeys) => [...prevKeys, response]);
      setNewKeyName('');
      toast({
        title: 'API Key generated successfully!',
        description: (
          <div className="flex items-center space-x-2">
            <span className="font-mono bg-gray-100 dark:bg-gray-700 p-1 rounded text-foreground select-all">{response.key}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                navigator.clipboard.writeText(response.key);
                toast({ title: 'Copied to clipboard!', duration: 2000 });
              }}
            >
              <Copy className="h-4 w-4 mr-2" /> Copy
            </Button>
          </div>
        ),
        duration: 10000, // Keep toast visible longer for user to copy
      });
    } catch (error: any) {
      toast({
        title: 'Error generating API key',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setGeneratingKey(false);
    }
  };

  const handleDeactivateKey = async (keyId: string) => {
    setConfirmDeactivateKeyId(keyId); // Show confirmation dialog
  };

  const confirmDeactivation = async () => {
    if (!confirmDeactivateKeyId) return;

    setDeactivatingKey(confirmDeactivateKeyId);
    try {
      await api.delete(`/arcana/api-keys/${confirmDeactivateKeyId}`);
      setApiKeys((prevKeys) =>
        prevKeys.map((key) =>
          key.id === confirmDeactivateKeyId ? { ...key, is_active: false } : key
        )
      );
      toast({
        title: 'API Key deactivated',
        description: 'The API key has been successfully deactivated.',
      });
    } catch (error: any) {
      toast({
        title: 'Error deactivating API key',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setDeactivatingKey(null);
      setConfirmDeactivateKeyId(null); // Close confirmation dialog
    }
  };

  const cancelDeactivation = () => {
    setConfirmDeactivateKeyId(null); // Close confirmation dialog
  };

  const handleSetConfig = async (key: string, value: string) => {
    if (!key.trim() || !value.trim()) {
      toast({
        title: 'Configuration key and value are required',
        variant: 'destructive',
      });
      return;
    }

    setSettingConfig(true);
    try {
      const response = await api.post('/arcana/cli-configs/', { key, value });
      setCliConfigs((prevConfigs) => {
        const existingIndex = prevConfigs.findIndex(c => c.key === response.key);
        if (existingIndex > -1) {
          const updatedConfigs = [...prevConfigs];
          updatedConfigs[existingIndex] = response;
          return updatedConfigs;
        }
        return [...prevConfigs, response];
      });
      // Clear generic inputs only if they were used
      if (key === newConfigKey && value === newConfigValue) {
        setNewConfigKey('');
        setNewConfigValue('');
      }
      toast({
        title: 'CLI Configuration set successfully!',
        description: `Key: ${response.key}, Value: ${response.value}`,
      });
    } catch (error: any) {
      toast({
        title: 'Error setting CLI configuration',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setSettingConfig(false);
    }
  };

  const handleDeleteConfig = async (keyToDelete: string) => {
    setDeletingConfig(keyToDelete);
    try {
      await api.delete(`/arcana/cli-configs/${keyToDelete}`);
      setCliConfigs((prevConfigs) => prevConfigs.filter((config) => config.key !== keyToDelete));
      toast({
        title: 'CLI Configuration deleted',
        description: `Configuration for key '${keyToDelete}' has been deleted.`,
      });
    } catch (error: any) {
      toast({
        title: 'Error deleting CLI configuration',
        description: error.message || 'An unexpected error occurred.',
        variant: 'destructive',
      });
    } finally {
      setDeletingConfig(null);
    }
  };

  return (
    <div className="space-y-8">
      <Card>
        <CardHeader>
          <CardTitle>Arcana CLI Agent</CardTitle>
          <CardDescription>
            Integrate Arcana's powerful AI capabilities directly into your terminal.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2">Installation</h3>
            <p className="text-sm text-muted-foreground mb-2">
              To install the Arcana CLI Agent, please refer to the official documentation for platform-specific instructions.
              Typically, it involves a global npm installation:
            </p>
            <div className="relative rounded-md bg-gray-800 p-3 font-mono text-sm text-white">
              <pre>npm install -g @vareon/arcana-cli-agent</pre>
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-2 text-gray-400 hover:text-white"
                onClick={() => {
                  navigator.clipboard.writeText('npm install -g @vareon/arcana-cli-agent');
                  toast({ title: 'Copied to clipboard!' });
                }}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              After installation, configure your CLI using the API Key generated below.
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Generate API Key</h3>
            <p className="text-sm text-muted-foreground mb-2">
              Generate an API key to authenticate your CLI agent with Vareon.
            </p>
            <div className="flex space-x-2">
              <Input
                placeholder="Name for your API Key (e.g., 'My Laptop CLI')"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                disabled={generatingKey}
              />
              <Button onClick={handleGenerateKey} disabled={generatingKey}>
                {generatingKey && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Generate Key
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* New Card for CLI Usage Example */}
      <Card className="bg-gray-900 text-green-400 font-mono">
        <CardHeader>
          <CardTitle className="text-green-300">Arcana CLI Usage Example</CardTitle>
          <CardDescription className="text-gray-400">
            See how to interact with the Arcana CLI Agent.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-1 p-4">
          {cliDemoOutput.map((line, index) => (
            <div key={index} className="flex items-center">
              {line.startsWith('>') ? (
                <TypewriterEffect text={line.substring(2)} prefix="> " delay={50} />
              ) : (
                <TypewriterEffect text={line} delay={30} />
              )}
            </div>
          ))}
          {showCursor && <span className="animate-blink-caret text-green-400">_</span>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>CLI Configurations</CardTitle>
          <CardDescription>
            Manage user-specific configurations for your Arcana CLI Agent.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6"> {/* Increased space-y for better separation */}
          <div className="grid gap-4"> {/* Use grid for better alignment */}
            {/* Default Agent ID Configuration */}
            <div className="grid grid-cols-[120px_1fr_auto] items-center gap-4"> {/* Specific grid columns */}
              <label htmlFor="default-agent-id" className="text-right text-sm">Default Agent:</label>
              <Select
                value={defaultAgentId}
                onValueChange={setDefaultAgentId}
                disabled={settingConfig}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a default agent" />
                </SelectTrigger>
                <SelectContent>
                  {availableAgents.length === 0 && <SelectItem value="no-agents-available" disabled>No agents available</SelectItem>}
                  {availableAgents.map((agent) => (
                    <SelectItem key={agent.id} value={agent.id}>{agent.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={() => handleSetConfig('default_agent_id', defaultAgentId)}
                disabled={settingConfig || !defaultAgentId}
              >
                {settingConfig && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Set Agent
              </Button>
            </div>

            {/* Preferred Model Configuration */}
            <div className="grid grid-cols-[120px_1fr_auto] items-center gap-4"> {/* Specific grid columns */}
              <label htmlFor="preferred-model" className="text-right text-sm">Preferred Model:</label>
              <Select
                value={preferredModel}
                onValueChange={setPreferredModel}
                disabled={settingConfig}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a preferred model" />
                </SelectTrigger>
                <SelectContent>
                  {availableModels.length === 0 && <SelectItem value="no-models-available" disabled>No models available</SelectItem>}
                  {availableModels.map((model) => (
                    <SelectItem key={model.id} value={model.id}>{model.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                onClick={() => handleSetConfig('preferred_model', preferredModel)}
                disabled={settingConfig || !preferredModel}
              >
                {settingConfig && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Set Model
              </Button>
            </div>

            {/* Generic Key-Value Configuration */}
            <div className="grid grid-cols-[120px_1fr_1fr_auto] items-center gap-4"> {/* Specific grid columns for two inputs */}
              <label htmlFor="custom-config" className="text-right text-sm">Custom Config:</label>
              <Input
                id="custom-config-key"
                placeholder="Configuration Key"
                value={newConfigKey}
                onChange={(e) => setNewConfigKey(e.target.value)}
                disabled={settingConfig}
              />
              <Input
                id="custom-config-value"
                placeholder="Configuration Value"
                value={newConfigValue}
                onChange={(e) => setNewConfigValue(e.target.value)}
                disabled={settingConfig}
              />
              <Button
                onClick={() => handleSetConfig(newConfigKey, newConfigValue)}
                disabled={settingConfig || !newConfigKey.trim() || !newConfigValue.trim()}
              >
                {settingConfig && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Set Custom
              </Button>
            </div>
          </div>

          {loadingConfigs ? (
            <div className="flex justify-center items-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : cliConfigs.length === 0 ? (
            <p className="text-center text-muted-foreground">No CLI configurations found.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Key</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cliConfigs.map((config) => (
                  <TableRow key={config.id}>
                    <TableCell className="font-medium">{config.key}</TableCell>
                    <TableCell>{config.value}</TableCell>
                    <TableCell>{format(new Date(config.updated_at), 'PPP p')}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteConfig(config.key)}
                        disabled={deletingConfig === config.key}
                      >
                        {deletingConfig === config.key ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Your API Keys</CardTitle>
          <CardDescription>
            Manage your existing Arcana CLI API keys.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : apiKeys.length === 0 ? (
            <p className="text-center text-muted-foreground">No API keys found. Generate one above!</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Key (Masked)</TableHead>
                  <TableHead>Created At</TableHead>
                  <TableHead>Expires At</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {apiKeys.map((key) => (
                  <TableRow key={key.id}>
                    <TableCell className="font-medium">{key.name}</TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-sm text-muted-foreground">
                          {key.is_active ? (revealedKeyId === key.id ? key.key : '****************') : 'Deactivated'}
                        </span>
                        {key.is_active && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => toggleRevealKey(key.id)}
                          >
                            {revealedKeyId === key.id ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{format(new Date(key.created_at), 'PPP')}</TableCell>
                    <TableCell>
                      {key.expires_at ? format(new Date(key.expires_at), 'PPP') : 'Never'}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          key.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {key.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      {key.is_active && (
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeactivateKey(key.id)}
                          disabled={deactivatingKey === key.id}
                        >
                          {deactivatingKey === key.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Trash2 className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {confirmDeactivateKeyId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Confirm Deactivation</CardTitle>
              <CardDescription>
                Are you sure you want to deactivate this API key? This action cannot be undone.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-end space-x-2">
              <Button variant="outline" onClick={cancelDeactivation}>
                Cancel
              </Button>
              <Button variant="destructive" onClick={confirmDeactivation} disabled={deactivatingKey !== null}>
                {deactivatingKey !== null && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Deactivate
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
