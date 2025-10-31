import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Upload, Server, CheckCircle, Clock } from 'lucide-react';

const deployments = [
  { name: 'Llama-3-8B-Instruct', status: 'deployed', uptime: '15d 4h', requests: 12453 },
  { name: 'Mistral-7B-v0.3', status: 'deploying', progress: 67, eta: '5 min' },
  { name: 'CodeLlama-13B', status: 'pending', queuePosition: 3 },
];

export default function ModelDeploymentTab() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5 text-primary" />
            Model Deployment
          </CardTitle>
          <CardDescription>
            Deploy and manage self-hosted LLM models
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Model Name</Label>
              <Input placeholder="llama-3-8b-instruct" data-testid="input-model-name" />
            </div>
            <div className="space-y-2">
              <Label>Model Format</Label>
              <select className="w-full h-9 rounded-md border px-3 text-sm" data-testid="select-model-format">
                <option value="gguf">GGUF</option>
                <option value="safetensors">SafeTensors</option>
                <option value="pytorch">PyTorch</option>
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <Label>Upload Model File</Label>
            <div className="border-2 border-dashed rounded-lg p-8 text-center hover-elevate cursor-pointer">
              <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                Drag and drop your model file here, or click to browse
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Supports GGUF, SafeTensors, PyTorch formats (max 50GB)
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button className="flex-1" data-testid="button-deploy-model">
              <Server className="h-4 w-4 mr-2" />
              Deploy Model
            </Button>
            <Button variant="outline" data-testid="button-import-huggingface">
              Import from HuggingFace
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Active Deployments</CardTitle>
          <CardDescription>
            Monitor and manage deployed models
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {deployments.map((deployment) => (
            <Card key={deployment.name} className="bg-card/50">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-sm">{deployment.name}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      {deployment.status === 'deployed' && (
                        <>
                          <Badge variant="default" className="gap-1">
                            <CheckCircle className="h-3 w-3" />
                            Deployed
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {deployment.uptime} uptime
                          </span>
                        </>
                      )}
                      {deployment.status === 'deploying' && (
                        <>
                          <Badge variant="secondary" className="gap-1">
                            <Clock className="h-3 w-3" />
                            Deploying
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            ETA {deployment.eta}
                          </span>
                        </>
                      )}
                      {deployment.status === 'pending' && (
                        <Badge variant="outline">
                          Queue #{deployment.queuePosition}
                        </Badge>
                      )}
                    </div>
                  </div>
                  {deployment.status === 'deployed' && (
                    <div className="text-right">
                      <div className="text-sm font-mono font-medium">
                        {deployment.requests?.toLocaleString()}
                      </div>
                      <div className="text-xs text-muted-foreground">requests</div>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {deployment.status === 'deploying' && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{deployment.progress}%</span>
                    </div>
                    <Progress value={deployment.progress} />
                  </div>
                )}
                {deployment.status === 'deployed' && (
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">View Logs</Button>
                    <Button variant="outline" size="sm">Metrics</Button>
                    <Button variant="outline" size="sm" className="text-destructive">
                      Stop
                    </Button>
                  </div>
                )}
                {deployment.status === 'pending' && (
                  <p className="text-sm text-muted-foreground">
                    Waiting for available resources...
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Self-Hosted Deployment Benefits</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <ul className="list-disc list-inside space-y-1">
            <li>Complete data privacy and control</li>
            <li>No API rate limits or usage costs</li>
            <li>Custom fine-tuned models</li>
            <li>Lower latency for local inference</li>
            <li>Independence from cloud LLM providers</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
