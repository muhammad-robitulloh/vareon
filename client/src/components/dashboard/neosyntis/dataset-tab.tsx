import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Badge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui';
import { Database, Plus, Upload, ExternalLink, Download, Trash2, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/dashboard/use-toast';

import { Dataset } from './types';

export default function DatasetTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: datasets, isLoading, error } = useQuery<Dataset[]>({
    queryKey: ['/api/neosyntis/datasets'],
    queryFn: async () => {
      const response = await fetch('/api/neosyntis/datasets');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
  });

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [newDatasetName, setNewDatasetName] = useState('');
  const [newDatasetDescription, setNewDatasetDescription] = useState('');
  const [newDatasetType, setNewDatasetType] = useState('custom');

  const createDatasetMutation = useMutation({
    mutationFn: async (datasetData: { name: string; description: string; type: string }) => {
      const response = await fetch('/api/neosyntis/datasets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datasetData),
      });
      if (!response.ok) {
        throw new Error('Failed to create dataset');
      }
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/neosyntis/datasets'] });      setNewDatasetName('');
      setNewDatasetDescription('');
      setNewDatasetType('custom');
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to create dataset: ${err.message}`, variant: 'destructive' });
    },
  });

  const uploadDatasetMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/neosyntis/datasets/upload', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Failed to upload dataset');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Dataset Uploaded', description: 'Dataset file successfully uploaded.' });
      queryClient.invalidateQueries({ queryKey: ['/api/neosyntis/datasets'] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to upload dataset: ${err.message}`, variant: 'destructive' });
    },
  });

  const deleteDatasetMutation = useMutation({
    mutationFn: async (datasetId: string) => {
      const response = await fetch(`/api/neosyntis/datasets/${datasetId}`, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete dataset');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Dataset Deleted', description: 'Dataset has been successfully deleted.' });
      queryClient.invalidateQueries({ queryKey: ['/api/neosyntis/datasets'] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to delete dataset: ${err.message}`, variant: 'destructive' });
    },
  });

  const filteredDatasets = datasets?.filter((d: Dataset) =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return <div className="p-6 text-center">Loading datasets...</div>;
  }

  if (error) {
    console.error("Error loading datasets:", error);
    return <div className="p-6 text-center text-red-500">Error loading datasets: {error.message}</div>;
  }

  console.log("Datasets:", datasets);
  console.log("Filtered Datasets:", filteredDatasets);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5 text-primary" />
                Dataset Management
              </CardTitle>
              <CardDescription className="mt-1">
                Create, manage, and deploy custom datasets for model fine-tuning
              </CardDescription>
            </div>
            <Dialog>
              <DialogTrigger asChild>
                <Button data-testid="button-create-dataset">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Dataset
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create New Dataset</DialogTitle>
                  <DialogDescription>
                    Build a custom dataset from scratch or import existing data
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Dataset Name</label>
                    <Input
                      placeholder="My Custom Dataset"
                      data-testid="input-dataset-name"
                      value={newDatasetName}
                      onChange={(e) => setNewDatasetName(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Description</label>
                    <Input
                      placeholder="Dataset description..."
                      data-testid="input-dataset-description"
                      value={newDatasetDescription}
                      onChange={(e) => setNewDatasetDescription(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Type</label>
                    <select
                      className="w-full h-9 rounded-md border px-3 text-sm"
                      data-testid="select-dataset-type"
                      value={newDatasetType}
                      onChange={(e) => setNewDatasetType(e.target.value)}
                    >
                      <option value="custom">Custom</option>
                      <option value="qa">Question-Answer</option>
                      <option value="code">Code Examples</option>
                      <option value="text">Text</option>
                      <option value="structured">Structured Data</option>
                    </select>
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button
                      className="flex-1"
                      data-testid="button-create"
                      onClick={() => createDatasetMutation.mutate({ name: newDatasetName, description: newDatasetDescription, type: newDatasetType })}
                      disabled={createDatasetMutation.isPending || !newDatasetName}
                    >
                      {createDatasetMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : 'Create'}
                    </Button>
                    <Button variant="outline" className="flex-1">Cancel</Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Input
              placeholder="Search datasets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
              data-testid="input-search-datasets"
            />
            <input
              type="file"
              id="dataset-file-upload"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  uploadDatasetMutation.mutate(e.target.files[0]);
                }
              }}
            />
            <Button
              variant="outline"
              data-testid="button-import"
              onClick={() => {
                const fileInput = document.getElementById('dataset-file-upload') as HTMLInputElement;
                if (fileInput) {
                  fileInput.click();
                }
              }}
              disabled={uploadDatasetMutation.isPending}
            >
              {uploadDatasetMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
              Import
            </Button>
          </div>

          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Size</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDatasets?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      No datasets found. Create one or import from a file.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDatasets?.map((dataset: Dataset) => (
                    <TableRow key={dataset.id} data-testid={`row-dataset-${dataset.id}`}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{dataset.name}</div>
                          <div className="text-sm text-muted-foreground">
                            {dataset.description}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{dataset.type}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {dataset.size.toLocaleString()} rows
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(dataset.createdAt).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm" data-testid={`button-view-${dataset.id}`}>
                            View
                          </Button>
                          <Button variant="ghost" size="sm" data-testid={`button-export-${dataset.id}`}>
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" data-testid={`button-huggingface-${dataset.id}`}>
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            data-testid={`button-delete-${dataset.id}`}
                            onClick={() => deleteDatasetMutation.mutate(dataset.id)}
                            disabled={deleteDatasetMutation.isPending}
                          >
                            {deleteDatasetMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Showing {filteredDatasets?.length} of {datasets?.length} datasets</span>
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" />
              Push to HuggingFace
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Dataset Injection</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            VAREON uses dataset injection for prompt enhancement. Before LLM inference, selected datasets are checked
            and relevant context is automatically injected into the prompt.
          </p>
          <p>
            This approach allows fine-tuning-like results without training custom models, perfect for using
            cloud LLM providers like OpenRouter, Gemini API, or HuggingFace Inference.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
