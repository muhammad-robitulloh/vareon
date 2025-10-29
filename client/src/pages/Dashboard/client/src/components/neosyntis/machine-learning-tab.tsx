import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Brain, Play, Pause, Settings } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const trainingData = [
  { epoch: 1, loss: 2.4, accuracy: 0.45, val_loss: 2.6, val_accuracy: 0.42 },
  { epoch: 2, loss: 1.8, accuracy: 0.58, val_loss: 2.1, val_accuracy: 0.51 },
  { epoch: 3, loss: 1.3, accuracy: 0.68, val_loss: 1.7, val_accuracy: 0.63 },
  { epoch: 4, loss: 0.9, accuracy: 0.76, val_loss: 1.4, val_accuracy: 0.71 },
  { epoch: 5, loss: 0.6, accuracy: 0.84, val_loss: 1.2, val_accuracy: 0.78 },
];

const experiments = [
  { name: 'GPT-2 Fine-tune', status: 'training', epoch: '3/10', accuracy: 0.76, eta: '2h 15m' },
  { name: 'BERT QA Model', status: 'completed', accuracy: 0.92, duration: '4h 32m' },
  { name: 'Code Generation', status: 'paused', epoch: '5/20', accuracy: 0.68 },
];

export default function MachineLearningTab() {
  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            Machine Learning Dashboard
          </CardTitle>
          <CardDescription>
            Train and monitor custom ML models for self-deployment
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Training Metrics</CardTitle>
            <CardDescription>Loss and accuracy over epochs</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trainingData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="epoch" label={{ value: 'Epoch', position: 'insideBottom', offset: -5 }} />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Legend />
                <Line type="monotone" dataKey="loss" stroke="hsl(var(--chart-1))" name="Training Loss" strokeWidth={2} />
                <Line type="monotone" dataKey="val_loss" stroke="hsl(var(--chart-1))" strokeDasharray="5 5" name="Val Loss" strokeWidth={2} />
                <Line type="monotone" dataKey="accuracy" stroke="hsl(var(--chart-2))" name="Training Acc" strokeWidth={2} />
                <Line type="monotone" dataKey="val_accuracy" stroke="hsl(var(--chart-2))" strokeDasharray="5 5" name="Val Acc" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Current Training</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Model</span>
                <span className="font-medium">GPT-2 Fine-tune</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Epoch</span>
                <span className="font-mono">3 / 10</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Accuracy</span>
                <span className="font-mono">76%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">ETA</span>
                <span className="font-mono">2h 15m</span>
              </div>
            </div>

            <Progress value={30} />

            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1" data-testid="button-pause-training">
                <Pause className="h-4 w-4 mr-2" />
                Pause
              </Button>
              <Button variant="outline" size="sm" data-testid="button-training-settings">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Training Experiments</CardTitle>
              <CardDescription>Manage and monitor ML training runs</CardDescription>
            </div>
            <Button data-testid="button-new-experiment">
              <Play className="h-4 w-4 mr-2" />
              New Experiment
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {experiments.map((exp) => (
            <Card key={exp.name} className="bg-card/50">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm">{exp.name}</CardTitle>
                  <Badge
                    variant={exp.status === 'training' ? 'default' : exp.status === 'completed' ? 'secondary' : 'outline'}
                  >
                    {exp.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  {exp.status === 'training' && (
                    <>
                      <div>
                        <div className="text-muted-foreground">Epoch</div>
                        <div className="font-mono font-medium">{exp.epoch}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Accuracy</div>
                        <div className="font-mono font-medium">{(exp.accuracy * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">ETA</div>
                        <div className="font-mono font-medium">{exp.eta}</div>
                      </div>
                    </>
                  )}
                  {exp.status === 'completed' && (
                    <>
                      <div>
                        <div className="text-muted-foreground">Accuracy</div>
                        <div className="font-mono font-medium text-green-600">{(exp.accuracy * 100).toFixed(1)}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Duration</div>
                        <div className="font-mono font-medium">{exp.duration}</div>
                      </div>
                      <div className="flex items-end justify-end">
                        <Button variant="outline" size="sm">Deploy</Button>
                      </div>
                    </>
                  )}
                  {exp.status === 'paused' && (
                    <>
                      <div>
                        <div className="text-muted-foreground">Progress</div>
                        <div className="font-mono font-medium">{exp.epoch}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Accuracy</div>
                        <div className="font-mono font-medium">{(exp.accuracy * 100).toFixed(1)}%</div>
                      </div>
                      <div className="flex items-end justify-end">
                        <Button variant="outline" size="sm">
                          <Play className="h-4 w-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">ML Training Features</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <ul className="list-disc list-inside space-y-1">
            <li>Fine-tune pre-trained models on custom datasets</li>
            <li>Real-time training metrics and visualization</li>
            <li>Automatic checkpointing and resume capability</li>
            <li>Hyperparameter optimization and tuning</li>
            <li>Model evaluation and comparison tools</li>
            <li>Export trained models for deployment</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
