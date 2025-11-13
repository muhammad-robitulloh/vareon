import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardHeader, CardTitle, Button, Textarea, Input, Label, Badge, ScrollArea } from '@/components/ui';
import { GitBranch, GitCommit, GitPullRequest, Plus, Loader2, AlertCircle, ArrowUpFromLine } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

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

const GitStatusPanel: React.FC = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { token } = useAuth();
  const repoLocalPath = '.'; // Assuming the project root is the Git repository

  const [commitMessage, setCommitMessage] = useState('');
  const [authorName, setAuthorName] = useState('');
  const [authorEmail, setAuthorEmail] = useState('');

  // --- Fetch Git Status ---
  const { data: gitStatus, isLoading: isLoadingGitStatus, error: gitStatusError } = useQuery<GitStatus>({
    queryKey: ['gitStatus', repoLocalPath],
    queryFn: async () => {
      const response = await fetch(`/api/git/status?local_path=${encodeURIComponent(repoLocalPath)}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch Git status');
      }
      return response.json();
    },
    enabled: !!token,
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  // --- Git Add Mutation ---
  const addMutation = useMutation({
    mutationFn: async (files: string[]) => {
      const response = await fetch(`/api/git/add?local_path=${encodeURIComponent(repoLocalPath)}`, {
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
      queryClient.invalidateQueries({ queryKey: ['gitStatus'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to add files: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Commit Mutation ---
  const commitMutation = useMutation({
    mutationFn: async (commitData: GitCommitRequest) => {
      const response = await fetch(`/api/git/commit?local_path=${encodeURIComponent(repoLocalPath)}`, {
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
      queryClient.invalidateQueries({ queryKey: ['gitStatus'] });
      setCommitMessage('');
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to commit changes: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Push Mutation ---
  const pushMutation = useMutation({
    mutationFn: async (pushData: GitPushRequest) => {
      const response = await fetch(`/api/git/push?local_path=${encodeURIComponent(repoLocalPath)}`, {
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
      queryClient.invalidateQueries({ queryKey: ['gitStatus'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to push changes: ${err.message}`, variant: 'destructive' });
    },
  });

  // --- Git Pull Mutation ---
  const pullMutation = useMutation({
    mutationFn: async (pullData: GitPullRequest) => {
      const response = await fetch(`/api/git/pull?local_path=${encodeURIComponent(repoLocalPath)}`, {
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
      queryClient.invalidateQueries({ queryKey: ['gitStatus'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to pull changes: ${err.message}`, variant: 'destructive' });
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

  if (isLoadingGitStatus) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading Git status...</div>;
  if (gitStatusError) return <div className="p-4 text-center text-red-500">Error loading Git status: {gitStatusError.message}</div>;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-5 w-5" /> Git Operations
          {gitStatus && (
            <Badge variant="secondary" className="ml-2">
              <GitBranch className="h-3 w-3 mr-1" /> {gitStatus.current_branch}
              {gitStatus.ahead_by > 0 && <span className="ml-1 text-green-500">↑{gitStatus.ahead_by}</span>}
              {gitStatus.behind_by > 0 && <span className="ml-1 text-red-500">↓{gitStatus.behind_by}</span>}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto space-y-4">
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
                <ScrollArea className="h-24 border rounded-md p-2 text-xs">
                  {gitStatus.staged_files.map((file, index) => (
                    <p key={index} className="text-green-400">{file.status} {file.path}</p>
                  ))}
                </ScrollArea>
              </div>
            )}

            {/* Unstaged Files */}
            {gitStatus.unstaged_files.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">Unstaged Changes ({gitStatus.unstaged_files.length})</h4>
                <ScrollArea className="h-24 border rounded-md p-2 text-xs">
                  {gitStatus.unstaged_files.map((file, index) => (
                    <p key={index} className="text-yellow-400">{file.status} {file.path}</p>
                  ))}
                </ScrollArea>
              </div>
            )}

            {/* Untracked Files */}
            {gitStatus.untracked_files.length > 0 && (
              <div>
                <h4 className="font-semibold text-sm mb-2">Untracked Files ({gitStatus.untracked_files.length})</h4>
                <ScrollArea className="h-24 border rounded-md p-2 text-xs">
                  {gitStatus.untracked_files.map((file, index) => (
                    <p key={index} className="text-gray-400">?? {file}</p>
                  ))}
                </ScrollArea>
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
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default GitStatusPanel;
