import React, { useState, useEffect } from 'react';
import Editor from "@monaco-editor/react";
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@/hooks/use-auth';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button'; // Corrected import for Button
import { Save, Loader2, XCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface RepoEditorPanelProps {
  localPath: string;
  filePath: string | null;
  onFileSaved?: () => void;
}

const fetchFileContent = async (token: string | null, localPath: string, filePath: string) => {
  const response = await fetch(`/api/git/file_content?local_path=${encodeURIComponent(localPath)}&file_path=${encodeURIComponent(filePath)}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to fetch file content' }));
    throw new Error(errorData.detail);
  }
  return response.text(); // Assuming file content is plain text
};

const saveFileContent = async (token: string | null, localPath: string, filePath: string, content: string) => {
  const response = await fetch(`/api/git/file_content?local_path=${encodeURIComponent(localPath)}&file_path=${encodeURIComponent(filePath)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to save file content');
  }
  return response.text();
};

const RepoEditorPanel: React.FC<RepoEditorPanelProps> = ({ localPath, filePath, onFileSaved }) => {
  const { toast } = useToast();
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const [editorContent, setEditorContent] = useState<string | undefined>(undefined);
  const [originalContent, setOriginalContent] = useState<string | undefined>(undefined);

  // Fetch file content
  const { data, isLoading, error, isSuccess, isError, refetch } = useQuery<string, Error>({
    queryKey: ['repoFileContent', localPath, filePath],
    queryFn: () => fetchFileContent(token, localPath, filePath!),
    enabled: !!token && !!filePath && !!localPath,
  });

  useEffect(() => {
    if (isSuccess) {
      setEditorContent(data);
      setOriginalContent(data);
    }
  }, [isSuccess, data]);

  useEffect(() => {
    if (isError) {
      toast({ title: 'Error', description: `Failed to load file: ${error.message}`, variant: 'destructive' });
      setEditorContent(undefined);
      setOriginalContent(undefined);
    }
  }, [isError, error, toast]);

  // Save file content mutation
  const saveMutation = useMutation({
    mutationFn: async ({ content }: { content: string }) => {
      return saveFileContent(token, localPath, filePath!, content);
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'File saved successfully.' });
      queryClient.invalidateQueries({ queryKey: ['repoFileContent', localPath, filePath] });
      queryClient.invalidateQueries({ queryKey: ['gitStatus', localPath] }); // Invalidate Git status
      onFileSaved?.();
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to save file: ${err.message}`, variant: 'destructive' });
    },
  });

  const handleEditorChange = (value: string | undefined) => {
    setEditorContent(value);
  };

  const handleSave = () => {
    if (filePath && editorContent !== undefined) {
      saveMutation.mutate({ content: editorContent });
    }
  };

  const isContentModified = editorContent !== originalContent;

  if (!filePath) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle>Editor</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center text-muted-foreground">
          Select a file from the tree to view its content.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {filePath} {isContentModified && <span className="text-yellow-500 text-xs ml-2">(Modified)</span>}
        </CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleSave}
          disabled={!isContentModified || saveMutation.isPending || isLoading}
        >
          {saveMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        </Button>
      </CardHeader>
      <CardContent className="flex-1 p-0">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-500">
            <XCircle className="h-6 w-6 mr-2" />
            <span>Error loading file.</span>
          </div>
        ) : (
          <Editor
            height="100%"
            language={filePath.split('.').pop()} // Basic language detection
            theme="vs-dark"
            value={editorContent}
            onChange={handleEditorChange}
            options={{
              minimap: { enabled: false },
              readOnly: false,
            }}
          />
        )}
      </CardContent>
    </Card>
  );
};

export default RepoEditorPanel;
