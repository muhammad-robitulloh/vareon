import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Label, Switch } from '@/components/ui';
import { Github, Eye, EyeOff, Save, Loader2, Link, Unlink } from 'lucide-react'; // Added Link and Unlink icons
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/use-auth';
import { useLocation } from 'wouter'; // Import useLocation

// --- Interfaces ---
interface UserGitConfig {
  id: string;
  user_id: string;
  github_pat: string; // Masked or omitted in response
  default_author_name?: string;
  default_author_email?: string;
  default_repo_url?: string;
  default_local_path?: string;
  default_branch?: string;
  created_at: string;
  updated_at: string;
}

interface UserGitConfigCreateUpdate {
  github_pat?: string; // Still needed for initial PAT creation if OAuth not used
  default_author_name?: string;
  default_author_email?: string;
  default_repo_url?: string;
  default_local_path?: string;
  default_branch?: string;
}

const GithubSettingsTab: React.FC = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [location, setLocation] = useLocation(); // For handling OAuth callback

  const [formData, setFormData] = useState<UserGitConfigCreateUpdate>({});

  // --- Fetch User Git Config ---
  const { data: userGitConfig, isLoading, error } = useQuery<UserGitConfig>({
    queryKey: ['userGitConfig'],
    queryFn: async () => {
      const response = await fetch('/api/git/config', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        if (response.status === 404) return null; // Config not found is not an error here
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch user Git config');
      }
      return response.json();
    },
    enabled: !!token,
    retry: false, // Don't retry on 404
  });

  useEffect(() => {
    if (userGitConfig) {
      setFormData({
        default_author_name: userGitConfig.default_author_name,
        default_author_email: userGitConfig.default_author_email,
        default_repo_url: userGitConfig.default_repo_url,
        default_local_path: userGitConfig.default_local_path,
        default_branch: userGitConfig.default_branch,
      });
    } else {
      // Reset form if no config exists
      setFormData({});
    }
  }, [userGitConfig]);

  // --- Handle GitHub OAuth Callback ---
  useEffect(() => {
    const params = new URLSearchParams(location.split('?')[1]);
    if (params.get('github_auth_success') === 'true') {
      toast({ title: 'GitHub Connected', description: 'Your GitHub account has been successfully connected.' });
      queryClient.invalidateQueries({ queryKey: ['userGitConfig'] }); // Refresh config
      setLocation(location.split('?')[0], { replace: true }); // Clean up URL
    } else if (params.get('github_auth_success') === 'false') {
      const error = params.get('error_description') || 'Unknown error';
      toast({ title: 'GitHub Connection Failed', description: `Error: ${error}`, variant: 'destructive' });
      setLocation(location.split('?')[0], { replace: true }); // Clean up URL
    }
  }, [location, setLocation, toast, queryClient]);

  // --- Save/Update User Git Config Mutation (for non-PAT fields) ---
  const saveConfigMutation = useMutation({
    mutationFn: async (config: UserGitConfigCreateUpdate) => {
      const method = userGitConfig ? 'PUT' : 'POST';
      const response = await fetch('/api/git/config', {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save Git configuration');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Git configuration saved.' });
      queryClient.invalidateQueries({ queryKey: ['userGitConfig'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to save config: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Disconnect GitHub Mutation ---
  const disconnectMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/git/config/disconnect-github', { // New endpoint
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to disconnect GitHub');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'GitHub Disconnected', description: 'Your GitHub account has been disconnected.' });
      queryClient.invalidateQueries({ queryKey: ['userGitConfig'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to disconnect GitHub: ${err.message}`, variant: 'destructive' });
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleSubmit = () => {
    // Only send non-PAT fields
    const configToSave = {
      default_author_name: formData.default_author_name,
      default_author_email: formData.default_author_email,
      default_repo_url: formData.default_repo_url,
      default_local_path: formData.default_local_path,
      default_branch: formData.default_branch,
    };
    saveConfigMutation.mutate(configToSave);
  };

  const handleConnectGitHub = () => {
    window.location.href = '/api/git/github/authorize';
  };

  const handleDisconnectGitHub = () => {
    disconnectMutation.mutate();
  };

  const isConnectedToGitHub = userGitConfig && userGitConfig.github_pat && userGitConfig.github_pat !== '********';

  if (isLoading) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading Git settings...</div>;
  if (error && error.message !== 'Failed to fetch user Git config') return <div className="p-4 text-center text-red-500">Error: {error.message}</div>;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Github className="h-5 w-5" /> GitHub Integration
        </CardTitle>
        <CardDescription>
          Connect your GitHub account for seamless repository operations.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center justify-between p-3 border rounded-md">
          <div className="flex items-center gap-3">
            {isConnectedToGitHub ? (
              <Link className="h-5 w-5 text-green-500" />
            ) : (
              <Unlink className="h-5 w-5 text-red-500" />
            )}
            <span className="font-medium">
              {isConnectedToGitHub ? 'Connected to GitHub' : 'Not Connected to GitHub'}
            </span>
          </div>
          {isConnectedToGitHub ? (
            <Button variant="destructive" onClick={handleDisconnectGitHub} disabled={disconnectMutation.isPending}>
              {disconnectMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Unlink className="h-4 w-4 mr-2" />}
              Disconnect
            </Button>
          ) : (
            <Button onClick={handleConnectGitHub} disabled={saveConfigMutation.isPending}>
              <Github className="h-4 w-4 mr-2" /> Connect to GitHub
            </Button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="default_author_name">Default Author Name</Label>
            <Input
              id="default_author_name"
              placeholder="Your Name"
              value={formData.default_author_name || ''}
              onChange={handleChange}
              disabled={saveConfigMutation.isPending}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="default_author_email">Default Author Email</Label>
            <Input
              id="default_author_email"
              placeholder="your@email.com"
              value={formData.default_author_email || ''}
              onChange={handleChange}
              disabled={saveConfigMutation.isPending}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="default_repo_url">Default Repository URL</Label>
          <Input
            id="default_repo_url"
            placeholder="https://github.com/user/repo.git"
            value={formData.default_repo_url || ''}
            onChange={handleChange}
            disabled={saveConfigMutation.isPending}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="default_local_path">Default Local Path</Label>
            <Input
              id="default_local_path"
              placeholder="my-project"
              value={formData.default_local_path || ''}
              onChange={handleChange}
              disabled={saveConfigMutation.isPending}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="default_branch">Default Branch</Label>
            <Input
              id="default_branch"
              placeholder="main"
              value={formData.default_branch || ''}
              onChange={handleChange}
              disabled={saveConfigMutation.isPending}
            />
          </div>
        </div>

        <Button
          className="w-full"
          onClick={handleSubmit}
          disabled={saveConfigMutation.isPending}
        >
          {saveConfigMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
          Save Git Settings
        </Button>
      </CardContent>
    </Card>
  );
};

export default GithubSettingsTab;
