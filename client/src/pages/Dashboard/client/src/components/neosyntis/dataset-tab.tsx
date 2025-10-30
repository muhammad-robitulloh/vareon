import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import { Database, Plus, Upload, ExternalLink, Download, Trash2 } from 'lucide-react';
import { mockDatasets } from '@/pages/Dashboard/client/src/lib/mockApi';

export default function DatasetTab() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: datasets } = useQuery({
    queryKey: ['/api/datasets'],
    initialData: mockDatasets,
  });

  const filteredDatasets = datasets?.filter(d =>
    d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
                    <Input placeholder="My Custom Dataset" data-testid="input-dataset-name" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Description</label>
                    <Input placeholder="Dataset description..." data-testid="input-dataset-description" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Type</label>
                    <select className="w-full h-9 rounded-md border px-3 text-sm" data-testid="select-dataset-type">
                      <option value="custom">Custom</option>
                      <option value="qa">Question-Answer</option>
                      <option value="code">Code Examples</option>
                      <option value="text">Text</option>
                      <option value="structured">Structured Data</option>
                    </select>
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button className="flex-1" data-testid="button-create">Create</Button>
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
            <Button variant="outline" data-testid="button-import">
              <Upload className="h-4 w-4 mr-2" />
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
                {filteredDatasets?.map((dataset) => (
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
                        <Button variant="ghost" size="sm" data-testid={`button-delete-${dataset.id}`}>
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
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
