import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, Button, Textarea } from '@/components/ui';
import { Save, Loader2, FileText, XCircle } from 'lucide-react';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';

interface FileEditorProps {
  filePath: string | null;
  localPath: string; // The local repository path
  onClose: () => void; // Callback to close the editor
}

interface FileOperationRequest {
  action: 'read' | 'write';
  path: string;
  content?: string;
}

const FileEditor: React.FC<FileEditorProps> = ({ filePath, localPath, onClose }) => {
  const { token } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [fileContent, setFileContent] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // --- Fetch File Content ---
  const { data, isLoading, error, refetch } = useQuery<string>({
    queryKey: ['fileContent', filePath, localPath],
    queryFn: async () => {
      if (!filePath || !localPath) return '';
      const response = await fetch(`/api/arcana/file-operations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ action: 'read', path: `${localPath}/${filePath}` }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to read file content');
      }
      const result = await response.json();
      return result.content;
    },
    enabled: !!filePath && !!localPath && !!token,
  });

  useEffect(() => {
    if (data !== undefined) {
      setFileContent(data);
    }
  }, [data]);

  // --- Save File Content Mutation ---
  const saveFileMutation = useMutation({
    mutationFn: async (content: string) => {
      if (!filePath || !localPath) throw new Error("File path or local path not provided.");
      const response = await fetch(`/api/arcana/file-operations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ action: 'write', path: `${localPath}/${filePath}`, content }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save file content');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'File saved successfully.' });
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['fileContent', filePath, localPath] }); // Refetch to ensure UI is updated
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to save file: ${err.message}`, variant: 'destructive' });
    },
  });

  const handleSave = () => {
    if (fileContent !== null) {
      saveFileMutation.mutate(fileContent);
    }
  };

  if (!filePath) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" /> File Editor
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center text-muted-foreground">
          Select a file from the tree to view and edit its content.
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" /> {filePath.split('/').pop()}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin" />
          <p className="ml-2">Loading file content...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" /> {filePath.split('/').pop()}
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} className="absolute top-3 right-3">
            <XCircle className="h-5 w-5" />
          </Button>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center text-red-500">
          <p>Error loading file: {error.message}</p>
          <Button onClick={() => refetch()} className="mt-4">Retry</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <FileText className="h-5 w-5" /> {filePath.split('/').pop()}
        </CardTitle>
        <div className="flex gap-2">
          <Button variant="ghost" size="icon" onClick={onClose}>
            <XCircle className="h-5 w-5" />
          </Button>
          <Button onClick={handleSave} disabled={saveFileMutation.isPending || !isEditing}>
            {saveFileMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Save className="h-4 w-4 mr-2" />}
            Save
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0">
        <Textarea
          value={fileContent || ''}
          onChange={(e) => { setFileContent(e.target.value); setIsEditing(true); }}
          className="flex-1 font-mono text-sm resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 rounded-none"
          placeholder="File content..."
        />
      </CardContent>
    </Card>
  );
};

export default FileEditor;
