import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Folder, ChevronDown, ChevronRight, GitBranch, Loader2, File as FileIcon } from 'lucide-react'; // Alias File to FileIcon
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';

// --- File Tree Interfaces ---
interface FileNode {
  name: string;
  path: string;
  is_dir: boolean;
  children?: FileNode[];
}

interface UserGitConfig {
  default_repo_url?: string;
  default_local_path?: string;
  default_branch?: string;
}

interface GitBranch {
  name: string;
  is_current: boolean;
  is_remote: boolean;
}

interface FileTreeProps {
  onFileSelect: (filePath: string) => void;
  selectedFile: string | null;
  selectedRepoPath: string;
  setSelectedRepoPath: (path: string) => void;
  selectedBranch: string; // Added
  setSelectedBranch: (branch: string) => void; // Added
}

const fetchFileTree = async (token: string | null, localPath: string) => {
  if (!localPath) return []; // Don't fetch if no localPath is selected
  const response = await fetch(`/api/arcana/file-tree/?local_path=${encodeURIComponent(localPath)}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch file tree' }));
    throw new Error(errorData.detail);
  }
  return response.json();
};

const fetchUserGitConfig = async (token: string | null) => {
  const response = await fetch('/api/git/config', {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!response.ok) {
    if (response.status === 404) return null; // Config not found is not an error
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch user Git config');
  }
  return response.json();
};

const fetchBranches = async (token: string | null, localPath: string) => {
  if (!localPath) return [];
  const response = await fetch(`/api/git/branches?local_path=${encodeURIComponent(localPath)}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to fetch branches');
  }
  return response.json();
};

const FileTreeNode: React.FC<{ node: FileNode; level?: number; onFileSelect: (filePath: string) => void; selectedFile: string | null }> = ({ node, level = 0, onFileSelect, selectedFile }) => {
  const [isOpen, setIsOpen] = useState(false);
  const hasChildren = node.children && node.children.length > 0;

  const handleToggle = () => {
    if (node.is_dir) {
      setIsOpen(!isOpen);
    } else {
      onFileSelect(node.path);
    }
  };

  const isSelected = selectedFile === node.path;

  return (
    <div>
      <div
        className={`flex items-center p-1 rounded-md hover:bg-accent/50 cursor-pointer ${isSelected ? 'bg-accent' : ''}`}
        style={{ paddingLeft: `${level * 1.5}rem` }}
        onClick={handleToggle}
      >
        {node.is_dir ? (
          <>
            {hasChildren ? (
              isOpen ? <ChevronDown className="h-4 w-4 mr-1" /> : <ChevronRight className="h-4 w-4 mr-1" />
            ) : (
              <span className="w-5" /> // Placeholder for alignment
            )}
            <Folder className="h-4 w-4 mr-2 text-blue-500" />
          </>
        ) : (
          <>
            <span className="w-5" />
            <FileIcon className="h-4 w-4 mr-2 text-gray-500" /> {/* Use FileIcon */}
          </>
        )}
        <span className="text-sm">{node.name}</span>
      </div>
      {isOpen && hasChildren && (
        <div>
          {node.children?.map((child: FileNode) => (
            <FileTreeNode key={child.path} node={child} level={level + 1} onFileSelect={onFileSelect} selectedFile={selectedFile} />
          ))}
        </div>
      )}
    </div>
  );
};


const FileTree: React.FC<FileTreeProps> = ({ onFileSelect, selectedFile, selectedRepoPath, setSelectedRepoPath, selectedBranch, setSelectedBranch }) => {
  const { token } = useAuth();
  const { toast } = useToast();

  // Fetch User Git Config to get default repo/path
  const { data: userGitConfig, isLoading: isLoadingUserGitConfig, error: userGitConfigError } = useQuery<UserGitConfig | null>({
    queryKey: ['userGitConfig'],
    queryFn: () => fetchUserGitConfig(token),
    enabled: !!token,
  });

  // Set initial selectedRepoPath and selectedBranch from user config
  useEffect(() => {
    if (userGitConfig && userGitConfig.default_local_path && !selectedRepoPath) {
      setSelectedRepoPath(userGitConfig.default_local_path);
      if (userGitConfig.default_branch && !selectedBranch) {
        setSelectedBranch(userGitConfig.default_branch);
      }
    }
  }, [userGitConfig, selectedRepoPath, selectedBranch, setSelectedRepoPath, setSelectedBranch]);

  // Fetch branches for the selected repository
  const { data: branches, isLoading: isLoadingBranches, error: branchesError } = useQuery<GitBranch[]>({
    queryKey: ['gitBranches', selectedRepoPath],
    queryFn: () => fetchBranches(token, selectedRepoPath),
    enabled: !!token && !!selectedRepoPath,
  });

  // Fetch file tree for the selected repository and branch
  const { data: fileTree, isLoading: isLoadingFileTree, error: fileTreeError } = useQuery<FileNode[]>({
    queryKey: ['fileTree', selectedRepoPath, selectedBranch],
    queryFn: () => fetchFileTree(token, selectedRepoPath), // Branch is handled by Git checkout, not directly in file-tree endpoint
    enabled: !!token && !!selectedRepoPath,
  });

  if (isLoadingUserGitConfig || isLoadingFileTree || isLoadingBranches) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Folder className="h-5 w-5" /> Project Context
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin" />
          <p className="ml-2 text-white">Loading project context...</p>
        </CardContent>
      </Card>
    );
  }

  if (userGitConfigError) {
    toast({
      title: 'Error',
      description: `Failed to load Git config: ${userGitConfigError.message}. Please configure in User Profile.`,
      variant: 'destructive',
    });
  }
  if (fileTreeError) {
    toast({
      title: 'Error',
      description: `Failed to load file tree: ${fileTreeError.message}`,
      variant: 'destructive',
    });
  }
  if (branchesError) {
    toast({
      title: 'Error',
      description: `Failed to load branches: ${branchesError.message}`,
      variant: 'destructive',
    });
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Folder className="h-5 w-5" /> Project Context
        </CardTitle>
        <div className="flex flex-col gap-2 mt-2">
          {/* Repository Selector (for now, assume one default repo from config) */}
          <Label htmlFor="repo-select" className="sr-only">Select Repository</Label>
          <Select value={selectedRepoPath} onValueChange={setSelectedRepoPath}>
            <SelectTrigger id="repo-select" className="w-full">
              <SelectValue placeholder="Select Repository" />
            </SelectTrigger>
            <SelectContent>
              {userGitConfig?.default_local_path && (
                <SelectItem value={userGitConfig.default_local_path}>
                  {userGitConfig.default_local_path} ({userGitConfig.default_repo_url})
                </SelectItem>
              )}
              {/* In future, list all cloned repos */}
            </SelectContent>
          </Select>

          {/* Branch Selector */}
          <Label htmlFor="branch-select" className="sr-only">Select Branch</Label>
          <Select value={selectedBranch} onValueChange={setSelectedBranch} disabled={!selectedRepoPath || isLoadingBranches}>
            <SelectTrigger id="branch-select" className="w-full">
              <SelectValue placeholder="Select Branch" />
            </SelectTrigger>
            <SelectContent>
              {branches?.map((branch: GitBranch) => (
                <SelectItem key={branch.name} value={branch.name}>
                  <div className="flex items-center gap-2">
                    <GitBranch className="h-4 w-4" /> {branch.name} {branch.is_current && '(current)'} {branch.is_remote && '(remote)'}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden">
        <ScrollArea className="h-full p-2 border rounded-md bg-black font-mono text-sm">
          {fileTreeError && <p className="text-red-500">Error loading file tree: {fileTreeError.message}</p>}
          {fileTree?.map((node: FileNode) => (
            <FileTreeNode key={node.path} node={node} onFileSelect={onFileSelect} selectedFile={selectedFile} />
          ))}
          {!fileTree?.length && !isLoadingFileTree && <p className="text-muted-foreground">No files found or repository not selected/cloned.</p>}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default FileTree;
