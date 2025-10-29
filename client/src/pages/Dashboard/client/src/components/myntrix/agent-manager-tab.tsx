import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import { Bot, Play, Pause, RotateCcw, Trash2, Plus } from 'lucide-react';
import { StatusIndicator } from '../status-indicator';
import { mockAgents } from '@/pages/Dashboard/client/src/lib/mockApi';
import { useToast } from '@/pages/Dashboard/client/src/hooks/use-toast';
import { queryClient } from '@/pages/Dashboard/client/src/lib/queryClient';

export default function AgentManagerTab() {
  const { toast } = useToast();

  const { data: agents } = useQuery({
    queryKey: ['/api/agents'],
    initialData: mockAgents,
  });

  const startAgent = useMutation({
    mutationFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return { success: true };
    },
    onSuccess: () => {
      toast({ title: 'Agent started', description: 'Agent is now running' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
  });

  const stopAgent = useMutation({
    mutationFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return { success: true };
    },
    onSuccess: () => {
      toast({ title: 'Agent stopped' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary" />
                Agent Manager
              </CardTitle>
              <CardDescription className="mt-1">
                Manage and monitor AI agents for task execution
              </CardDescription>
            </div>
            <Button data-testid="button-create-agent">
              <Plus className="h-4 w-4 mr-2" />
              Create Agent
            </Button>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Last Run</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {agents?.map((agent) => (
                <TableRow key={agent.id} data-testid={`row-agent-${agent.id}`}>
                  <TableCell className="font-medium">{agent.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{agent.type}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <StatusIndicator status={agent.status as any} size="sm" />
                      <span className="text-sm capitalize">{agent.status}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 max-w-[100px]">
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              agent.health >= 90 ? 'bg-green-500' :
                              agent.health >= 70 ? 'bg-yellow-500' :
                              agent.health > 0 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${agent.health}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-mono">{agent.health}%</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {agent.lastRun ? new Date(agent.lastRun).toLocaleString() : 'Never'}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      {agent.status === 'running' ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => stopAgent.mutate(agent.id)}
                          data-testid={`button-stop-${agent.id}`}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => startAgent.mutate(agent.id)}
                          data-testid={`button-start-${agent.id}`}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <Button variant="ghost" size="sm" data-testid={`button-restart-${agent.id}`}>
                        <RotateCcw className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm" data-testid={`button-delete-${agent.id}`}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Total Agents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{agents?.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Running</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {agents?.filter(a => a.status === 'running').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Avg Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {Math.round(agents?.reduce((acc, a) => acc + a.health, 0)! / agents?.length!)}%
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
