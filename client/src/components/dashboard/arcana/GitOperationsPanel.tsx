import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardHeader, CardTitle, Button, Textarea, Input, Label, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';
import { GitBranch, GitCommit, GitPullRequest, Plus, Loader2, AlertCircle, Code, CheckCircle, XCircle, ArrowUpFromLine, Github } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useLocation } from 'wouter'; // Import useLocation from wouter

// --- Git Status Interfaces (matching backend schemas) ---
interface GitStatusFile {
  path: string;
  status: string; // e.g., 'M' (modified), 'A' (added), 'D' (deleted), '??' (untracked)
}

interface GitStatus {
  current_branch: string;
  is_dirty: boolean;
  staged_files: GitStatusFile[];
  unstaged_files: GitStatusFile[];
  untracked_files: string[];
  ahead_by: number;
  behind_by: number;
}

interface GitBranch {
  name: string;
  is_current: boolean;
  is_remote: boolean;
}

interface GitCommitRequest {
  message: string;
  author_name?: string;
  author_email?: string;
}

interface GitAddRequest {
  files: string[];
}

interface GitPushRequest {
  remote_name?: string;
  branch_name?: string;
}

interface GitPullRequest {
  remote_name?: string;
  branch_name?: string;
}

interface GitCheckoutRequest {
  branch_name: string;
}

interface GitCreateBranchRequest {
  branch_name: string;
}

interface GitOperationsPanelProps {
  localPath: string;
  currentBranch: string;
  onBranchChange: (newBranch: string) => void;
}

const GitOperationsPanel: React.FC<GitOperationsPanelProps> = ({ localPath, currentBranch, onBranchChange }) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const [location, setLocation] = useLocation(); // Get location and setLocation from wouter

  const [commitMessage, setCommitMessage] = useState('');
  const [authorName, setAuthorName] = useState('');
  const [authorEmail, setAuthorEmail] = useState('');
  const [newBranchName, setNewBranchName] = useState('');

  // --- Handle GitHub OAuth Callback ---
  useEffect(() => {
    const params = new URLSearchParams(location.split('?')[1]);
    if (params.get('github_auth_success') === 'true') {
      toast({ title: 'GitHub Connected', description: 'Your GitHub account has been successfully connected.' });
      // Clean up URL
      setLocation(location.split('?')[0], { replace: true });
    } else if (params.get('github_auth_success') === 'false') {
      const error = params.get('error_description') || 'Unknown error';
      toast({ title: 'GitHub Connection Failed', description: `Error: ${error}`, variant: 'destructive' });
      // Clean up URL
      setLocation(location.split('?')[0], { replace: true });
    }
  }, [location, setLocation, toast]);

  // --- Fetch Git Status ---
  const { data: gitStatus, isLoading: isLoadingGitStatus, error: gitStatusError } = useQuery<GitStatus>({
    queryKey: ['gitStatus', localPath],
    queryFn: async () => {
      const response = await fetch(`/api/git/status?local_path=${encodeURIComponent(localPath)}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch Git status');
      }
      return response.json();
    },
    enabled: !!token && !!localPath,
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  // --- Fetch Branches ---
  const { data: branches, isLoading: isLoadingBranches, error: branchesError } = useQuery<GitBranch[]>({
    queryKey: ['gitBranches', localPath],
    queryFn: async () => {
      const response = await fetch(`/api/git/branches?local_path=${encodeURIComponent(localPath)}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch branches');
      }
      return response.json();
    },
    enabled: !!token && !!localPath,
  });

  // --- Git Add Mutation ---
  const addMutation = useMutation({
    mutationFn: async (files: string[]) => {
      const response = await fetch(`/api/git/add?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ files }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to add files');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Files added to staging.' });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to add files: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Commit Mutation ---
  const commitMutation = useMutation({
    mutationFn: async (commitData: GitCommitRequest) => {
      const response = await fetch(`/api/git/commit?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(commitData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to commit changes');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Changes committed.' });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] });
      setCommitMessage('');
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to commit changes: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Push Mutation ---
  const pushMutation = useMutation({
    mutationFn: async (pushData: GitPushRequest) => {
      const response = await fetch(`/api/git/push?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(pushData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to push changes');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Changes pushed to remote.' });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to push changes: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Pull Mutation ---
  const pullMutation = useMutation({
    mutationFn: async (pullData: GitPullRequest) => {
      const response = await fetch(`/api/git/pull?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(pullData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to pull changes');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Changes pulled from remote.' });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to pull changes: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Checkout Mutation ---
  const checkoutMutation = useMutation({
    mutationFn: async (checkoutData: GitCheckoutRequest) => {
      const response = await fetch(`/api/git/checkout?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(checkoutData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to checkout branch');
      }
      return response.json();
    },
    onSuccess: (data, variables) => {
      toast({ title: 'Success', description: data });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] });
      queryClient.invalidateQueries({ queryKey: ['gitBranches', localPath] });
      onBranchChange(variables.branch_name); // Notify parent about branch change
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to checkout branch: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Create Branch Mutation ---
  const createBranchMutation = useMutation({
    mutationFn: async (createBranchData: GitCreateBranchRequest) => {
      const response = await fetch(`/api/git/branch?local_path=${encodeURIComponent(localPath)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(createBranchData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create branch');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast({ title: 'Success', description: data });
      queryClient.invalidateQueries({ queryKey: ['gitBranches', localPath] });
      setNewBranchName('');
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to create branch: ${err.message}`, variant: 'destructive' });
    },
  });


  const handleAddAll = () => {
    addMutation.mutate(['.']);
  };

  const handleCommit = () => {
    if (!commitMessage.trim()) {
      toast({ title: 'Warning', description: 'Commit message cannot be empty.', variant: 'warning' });
      return;
    }
    commitMutation.mutate({ message: commitMessage, author_name: authorName || undefined, author_email: authorEmail || undefined });
  };

  const handlePush = () => {
    pushMutation.mutate({});
  };

  const handlePull = () => {
    pullMutation.mutate({});
  };

  const handleCheckoutBranch = (branchName: string) => {
    checkoutMutation.mutate({ branch_name: branchName });
  };

  const handleCreateBranch = () => {
    if (!newBranchName.trim()) {
      toast({ title: 'Warning', description: 'Branch name cannot be empty.', variant: 'warning' });
      return;
    }
    createBranchMutation.mutate({ branch_name: newBranchName });
  };

  const handleConnectGitHub = () => {
    window.location.href = '/api/git/github/authorize';
  };

  if (!localPath) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5" /> Git Operations
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center text-muted-foreground">
          Select a repository to view Git operations.
        </CardContent>
      </Card>
    );
  }

  if (isLoadingGitStatus || isLoadingBranches) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading Git data...</div>;
  if (gitStatusError) return <div className="p-4 text-center text-red-500">Error loading Git status: {gitStatusError.message}</div>;
  if (branchesError) return <div className="p-4 text-center text-red-500">Error loading branches: {branchesError.message}</div>;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-5 w-5" /> Git Operations
          {gitStatus && (
            <Badge variant="secondary" className="ml-2">
              {gitStatus.current_branch}
              {gitStatus.ahead_by > 0 && <span className="ml-1 text-green-500">↑{gitStatus.ahead_by}</span>}
              {gitStatus.behind_by > 0 && <span className="ml-1 text-red-500">↓{gitStatus.behind_by}</span>}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4">
        <div className="flex justify-end mb-4">
          <Button onClick={handleConnectGitHub} className="gap-2">
            <Github className="h-4 w-4" /> Connect to GitHub
          </Button>
        </div>

        {gitStatus && (
          <>
            {gitStatus.is_dirty && (
              <div className="flex items-center gap-2 text-yellow-500">
                <AlertCircle className="h-4 w-4" />
                <span>Uncommitted changes detected.</span>
              </div>
            )}

            {/* Staged Files */}
            {gitStatus.staged_files.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">Staged Changes ({gitStatus.staged_files.length})</h4>
                <div className="border rounded-md p-2 text-xs bg-black font-mono">
                  {gitStatus.staged_files.map((file, index) => (
                    <p key={index} className="text-green-400"><CheckCircle className="inline-block h-3 w-3 mr-1" /> {file.path}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Unstaged Files */}
            {gitStatus.unstaged_files.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">Unstaged Changes ({gitStatus.unstaged_files.length})</h4>
                <div className="border rounded-md p-2 text-xs bg-black font-mono">
                  {gitStatus.unstaged_files.map((file, index) => (
                    <p key={index} className="text-yellow-400"><AlertCircle className="inline-block h-3 w-3 mr-1" /> {file.path}</p>
                  ))}
                </div>
              </div>
            )}

            {/* Untracked Files */}
            {gitStatus.untracked_files.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">Untracked Files ({gitStatus.untracked_files.length})</h4>
                <div className="border rounded-md p-2 text-xs bg-black font-mono">
                  {gitStatus.untracked_files.map((file, index) => (
                    <p key={index} className="text-gray-400"><XCircle className="inline-block h-3 w-3 mr-1" /> {file}</p>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={handleAddAll}
                disabled={addMutation.isPending || (!gitStatus.unstaged_files.length && !gitStatus.untracked_files.length)}
                className="flex-1"
              >
                {addMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                Add All Changes
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="commit-message">Commit Message</Label>
              <Textarea
                id="commit-message"
                placeholder="Enter commit message"
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
                rows={3}
                disabled={commitMutation.isPending}
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-2">
                <Label htmlFor="author-name">Author Name (optional)</Label>
                <Input
                  id="author-name"
                  placeholder="Your Name"
                  value={authorName}
                  onChange={(e) => setAuthorName(e.target.value)}
                  disabled={commitMutation.isPending}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="author-email">Author Email (optional)</Label>
                <Input
                  id="author-email"
                  placeholder="your@email.com"
                  value={authorEmail}
                  onChange={(e) => setAuthorEmail(e.target.value)}
                  disabled={commitMutation.isPending}
                />
              </div>
            </div>
            <Button
              onClick={handleCommit}
              disabled={commitMutation.isPending || !commitMessage.trim() || !gitStatus.staged_files.length}
              className="w-full"
            >
              {commitMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <GitCommit className="h-4 w-4 mr-2" />}
              Commit Staged
            </Button>

            <div className="flex gap-2">
              <Button
                onClick={handlePull}
                disabled={pullMutation.isPending}
                className="flex-1"
              >
                {pullMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <GitPullRequest className="h-4 w-4 mr-2" />}
                Pull
              </Button>
              <Button
                onClick={handlePush}
                disabled={pushMutation.isPending || (!gitStatus.ahead_by && !gitStatus.is_dirty)}
                className="flex-1"
              >
                {pushMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowUpFromLine className="h-4 w-4 mr-2" />}
                Push
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="new-branch-name">Create New Branch</Label>
              <div className="flex gap-2">
                <Input
                  id="new-branch-name"
                  placeholder="feature/my-new-feature"
                  value={newBranchName}
                  onChange={(e) => setNewBranchName(e.target.value)}
                  disabled={createBranchMutation.isPending}
                />
                <Button
                  onClick={handleCreateBranch}
                  disabled={createBranchMutation.isPending || !newBranchName.trim()}
                >
                  {createBranchMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="checkout-branch">Checkout Branch</Label>
              <Select value={currentBranch} onValueChange={handleCheckoutBranch} disabled={checkoutMutation.isPending || isLoadingBranches}>
                <SelectTrigger id="checkout-branch" className="w-full">
                  <SelectValue placeholder="Select branch to checkout" />
                </SelectTrigger>
                <SelectContent>
                  {branches?.map(branch => (
                    <SelectItem key={branch.name} value={branch.name}>
                      <div className="flex items-center gap-2">
                        <GitBranch className="h-4 w-4" /> {branch.name} {branch.is_current && '(current)'} {branch.is_remote && '(remote)'}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default GitOperationsPanel;
