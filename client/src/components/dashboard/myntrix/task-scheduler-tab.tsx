import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Calendar, Plus, Clock } from 'lucide-react';

const scheduledTasks = [
  { name: 'Data Sync Job', schedule: '0 */6 * * *', nextRun: new Date(Date.now() + 3600000), enabled: true },
  { name: 'Model Training', schedule: '0 2 * * *', nextRun: new Date(Date.now() + 7200000), enabled: true },
  { name: 'Report Generation', schedule: '0 9 * * 1', nextRun: new Date(Date.now() + 86400000), enabled: false },
];

export default function TaskSchedulerTab() {
  const [cronExpression, setCronExpression] = useState('');

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            Task Scheduler
          </CardTitle>
          <CardDescription>
            Schedule automated tasks with cron expressions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Task Name</Label>
              <Input placeholder="My Scheduled Task" data-testid="input-task-name" />
            </div>
            <div className="space-y-2">
              <Label>Cron Expression</Label>
              <Input
                placeholder="0 */6 * * *"
                value={cronExpression}
                onChange={(e) => setCronExpression(e.target.value)}
                data-testid="input-cron-expression"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Task Action</Label>
            <select className="w-full h-9 rounded-md border px-3 text-sm" data-testid="select-task-action">
              <option value="workflow">Run Workflow</option>
              <option value="agent">Execute Agent</option>
              <option value="script">Run Script</option>
              <option value="api">Call API</option>
            </select>
          </div>

          <div className="flex gap-2">
            <Button data-testid="button-create-schedule">
              <Plus className="h-4 w-4 mr-2" />
              Create Schedule
            </Button>
            <Button variant="outline">Test Run</Button>
          </div>

          {cronExpression && (
            <div className="p-3 bg-primary/5 border border-primary/10 rounded-lg">
              <div className="text-sm font-medium mb-1">Schedule Preview</div>
              <div className="text-sm text-muted-foreground">
                This task will run: <span className="font-mono">{cronExpression}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Scheduled Tasks</CardTitle>
          <CardDescription>
            Manage existing scheduled tasks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {scheduledTasks.map((task, idx) => (
            <Card key={idx} className="bg-card/50">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-sm">{task.name}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant={task.enabled ? 'default' : 'outline'} className="text-xs">
                        {task.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                      <span className="text-xs text-muted-foreground font-mono">
                        {task.schedule}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      Next run
                    </div>
                    <div className="text-xs font-mono mt-1">
                      {task.nextRun.toLocaleString()}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Edit</Button>
                  <Button variant="outline" size="sm">Run Now</Button>
                  <Button variant="outline" size="sm">
                    {task.enabled ? 'Disable' : 'Enable'}
                  </Button>
                  <Button variant="outline" size="sm" className="text-destructive">
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Cron Expression Guide</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <div className="font-mono text-xs space-y-1">
            <div>* * * * * → Minute Hour Day Month Weekday</div>
            <div>0 */6 * * * → Every 6 hours</div>
            <div>0 9 * * 1 → Every Monday at 9 AM</div>
            <div>0 0 1 * * → First day of every month</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
