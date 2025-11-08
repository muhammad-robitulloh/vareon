import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Label, Badge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, Calendar, Popover, PopoverContent, PopoverTrigger } from '@/components/ui';
import { useToast } from '@/hooks/use-toast';
import { Activity, Plus, Clock, History, Calendar as CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';

// TYPE DEFINITIONS
interface ScheduledTask {
  id: string;
  name: string;
  schedule: string;
  action: string;
  enabled: boolean;
  nextRun: string | null;
  lastRun?: TaskRun;
}

interface TaskRun {
  id: string;
  taskId: string;
  taskName: string;
  startTime: string;
  endTime: string;
  status: 'Success' | 'Failed' | 'Running';
  logs: string;
}

// MOCK DATA
const MOCK_SCHEDULED_TASKS: ScheduledTask[] = [
  { id: 'task-1', name: 'Daily Data Sync', schedule: '0 1 * * *', action: 'workflow', enabled: true, nextRun: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() },
  { id: 'task-2', name: 'Hourly Health Check', schedule: '0 * * * *', action: 'script', enabled: true, nextRun: new Date(Date.now() + 60 * 60 * 1000).toISOString() },
  { id: 'task-3', name: 'Agent Deployment', schedule: '0 9 * * 1', action: 'agent', enabled: false, nextRun: null },
];

const MOCK_TASK_HISTORY: TaskRun[] = [
  { id: 'run-1', taskId: 'task-1', taskName: 'Daily Data Sync', startTime: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), endTime: new Date(Date.now() - 23 * 60 * 60 * 1000).toISOString(), status: 'Success', logs: 'INFO: Sync complete. 10,234 records updated.' },
  { id: 'run-2', taskId: 'task-2', taskName: 'Hourly Health Check', startTime: new Date(Date.now() - 60 * 60 * 1000).toISOString(), endTime: new Date(Date.now() - 59 * 60 * 1000).toISOString(), status: 'Success', logs: 'INFO: All systems nominal.' },
  { id: 'run-3', taskId: 'task-2', taskName: 'Hourly Health Check', startTime: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), endTime: new Date(Date.now() - 2 * 60 * 60 * 1000 + 5000).toISOString(), status: 'Failed', logs: 'ERROR: Timeout connecting to node-B. Check network connectivity.' },
];


export default function TaskSchedulerTab() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [newTaskName, setNewTaskName] = useState('');
  const [newTaskCronExpression, setNewTaskCronExpression] = useState('');
  const [newTaskAction, setNewTaskAction] = useState('workflow');
  const [date, setDate] = useState<Date>();

  const { data: scheduledTasks, isLoading, error } = useQuery({
    queryKey: ['/api/tasks'],
    queryFn: async (): Promise<ScheduledTask[]> => {
      // Mocking API call
      return Promise.resolve(MOCK_SCHEDULED_TASKS);
    },
  });

  const { data: taskHistory } = useQuery({
    queryKey: ['/api/tasks/history'],
    queryFn: async (): Promise<TaskRun[]> => {
      // Mocking API call
      return Promise.resolve(MOCK_TASK_HISTORY);
    }
  });

  const createTaskMutation = useMutation({
    mutationFn: async (taskData: { name: string; schedule: string; action: string }) => {
      console.log("Creating task:", taskData);
      // Mocking API call
      return Promise.resolve({ ...taskData, id: `task-${Math.random()}` });
    },
    onSuccess: () => {
      toast({ title: 'Task Created', description: 'New task has been scheduled.' });
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
      setNewTaskName('');
      setNewTaskCronExpression('');
      setNewTaskAction('workflow');
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to create task: ${err.message}`, variant: 'destructive' });
    },
  });

  const runTaskMutation = useMutation({
    mutationFn: async (taskId: string) => {
      console.log("Running task:", taskId);
      // Mocking API call
      return Promise.resolve({ status: 'ok' });
    },
    onSuccess: () => {
      toast({ title: 'Task Started', description: 'Task initiated successfully.' });
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to run task: ${err.message}`, variant: 'destructive' });
    },
  });

  const toggleTaskEnabledMutation = useMutation({
    mutationFn: async ({ taskId, enabled }: { taskId: string; enabled: boolean }) => {
      console.log(`${enabled ? 'Enabling' : 'Disabling'} task:`, taskId);
      // Mocking API call
      return Promise.resolve({ status: 'ok' });
    },
    onSuccess: () => {
      toast({ title: 'Task Updated', description: 'Task status changed successfully.' });
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to change task status: ${err.message}`, variant: 'destructive' });
    },
  });

  const deleteTaskMutation = useMutation({
    mutationFn: async (taskId: string) => {
      console.log("Deleting task:", taskId);
      // Mocking API call
      return Promise.resolve({ status: 'ok' });
    },
    onSuccess: () => {
      toast({ title: 'Task Deleted', description: 'Task removed successfully.' });
      queryClient.invalidateQueries({ queryKey: ['/api/tasks'] });
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to delete task: ${err.message}`, variant: 'destructive' });
    },
  });

  if (isLoading) {
    return <div className="p-6 text-center">Loading scheduled tasks...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">Error loading tasks: {error.message}</div>;
  }

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
              <Input
                placeholder="My Scheduled Task"
                data-testid="input-task-name"
                value={newTaskName}
                onChange={(e) => setNewTaskName(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Cron Expression</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant={"outline"}
                    className="w-full justify-start text-left font-normal"
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : <span>Pick a date</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0 z-50">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={(selectedDate) => {
                      setDate(selectedDate);
                      if (selectedDate) {
                        // Example: Set cron to run at midnight on the selected date
                        // This is a simplified example, actual cron generation might be more complex
                        setNewTaskCronExpression(`0 0 ${selectedDate.getDate()} ${selectedDate.getMonth() + 1} *`);
                      } else {
                        setNewTaskCronExpression('');
                      }
                    }}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              <Input
                placeholder="0 */6 * * *"
                value={newTaskCronExpression}
                onChange={(e) => setNewTaskCronExpression(e.target.value)}
                data-testid="input-cron-expression"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Task Action</Label>
            <select
              className="w-full h-9 rounded-md border px-3 text-sm"
              data-testid="select-task-action"
              value={newTaskAction}
              onChange={(e) => setNewTaskAction(e.target.value)}
            >
              <option value="workflow">Run Workflow</option>
              <option value="agent">Execute Agent</option>
              <option value="script">Run Script</option>
              <option value="api">Call API</option>
            </select>
          </div>

          <div className="flex gap-2">
            <Button
              data-testid="button-create-schedule"
              onClick={() => createTaskMutation.mutate({ name: newTaskName, schedule: newTaskCronExpression, action: newTaskAction })}
              disabled={createTaskMutation.isPending || !newTaskName || !newTaskCronExpression}
            >
              {createTaskMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
              Create Schedule
            </Button>
            <Button variant="outline">Test Run</Button>
          </div>

          {newTaskCronExpression && (
            <div className="p-3 bg-primary/5 border border-primary/10 rounded-lg">
              <div className="text-sm font-medium mb-1">Schedule Preview</div>
              <div className="text-sm text-muted-foreground">
                This task will run: <span className="font-mono">{newTaskCronExpression}</span>
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
          {scheduledTasks && scheduledTasks.length > 0 ? (
            scheduledTasks.map((task) => (
              <Card key={task.id} className="bg-card/50">
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
                        {task.nextRun ? new Date(task.nextRun).toLocaleString() : 'N/A'}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => runTaskMutation.mutate(task.id)} disabled={runTaskMutation.isPending}>
                      {runTaskMutation.isPending ? <Activity className="h-4 w-4 animate-spin" /> : 'Run Now'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleTaskEnabledMutation.mutate({ taskId: task.id, enabled: !task.enabled })}
                      disabled={toggleTaskEnabledMutation.isPending}
                    >
                      {toggleTaskEnabledMutation.isPending ? <Activity className="h-4 w-4 animate-spin" /> : (task.enabled ? 'Disable' : 'Enable')}
                    </Button>
                    <Button variant="outline" size="sm" className="text-destructive" onClick={() => deleteTaskMutation.mutate(task.id)} disabled={deleteTaskMutation.isPending}>
                      {deleteTaskMutation.isPending ? <Activity className="h-4 w-4 animate-spin" /> : 'Delete'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="text-muted-foreground">No scheduled tasks found.</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-primary" />
            Task Execution History
          </CardTitle>
          <CardDescription>
            Review the status and logs of past task runs.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Task</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="hidden md:table-cell">Start Time</TableHead>
                <TableHead className="hidden md:table-cell">Duration</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {taskHistory?.map((run) => (
                <TableRow key={run.id}>
                  <TableCell className="font-medium">{run.taskName}</TableCell>
                  <TableCell>
                    <Badge variant={run.status === 'Success' ? 'default' : run.status === 'Failed' ? 'destructive' : 'outline'}>
                      {run.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                    {new Date(run.startTime).toLocaleString()}
                  </TableCell>
                  <TableCell className="hidden md:table-cell text-sm text-muted-foreground">
                    {`${(new Date(run.endTime).getTime() - new Date(run.startTime).getTime()) / 1000}s`}
                  </TableCell>
                  <TableCell className="text-right">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">View Logs</Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Logs for {run.taskName}</DialogTitle>
                          <DialogDescription>
                            Execution started at {new Date(run.startTime).toLocaleString()}
                          </DialogDescription>
                        </DialogHeader>
                        <div className="mt-4 bg-muted/50 p-4 rounded-md max-h-96 overflow-y-auto">
                          <pre className="text-sm whitespace-pre-wrap">{run.logs}</pre>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
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
