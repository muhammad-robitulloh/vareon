import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui';
import { Bot, Play, Pause, RotateCcw, Trash2, Plus, Loader2 } from 'lucide-react';
import { StatusIndicator } from '../status-indicator';
import { mockAgents } from '@/lib/dashboard/mockApi';
import { useToast } from '@/hooks/dashboard/use-toast';
import { queryClient } from '@/lib/dashboard/queryClient';

import { Agent } from './types';

export default function AgentManagerTab() {
  const { toast } = useToast();

  const { data: agents } = useQuery<Agent[]>({
    queryKey: ['/api/agents'],
    queryFn: async () => {
      const response = await fetch('/api/agents');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
  });

  const startAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`/api/agents/${agentId}/start`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to start agent');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Agent started', description: 'Agent is now running' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to start agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const stopAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`/api/agents/${agentId}/stop`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to stop agent');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Agent stopped' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to stop agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const createAgent = useMutation({
    mutationFn: async (newAgentData: { name: string; type: string }) => {
      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newAgentData),
      });
      if (!response.ok) {
        throw new Error('Failed to create agent');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Agent created', description: 'New agent has been successfully created.' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to create agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const restartAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`/api/agents/${agentId}/restart`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to restart agent');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Agent restarted', description: 'Agent has been successfully restarted.' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to restart agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const deleteAgent = useMutation({
    mutationFn: async (agentId: string) => {
      const response = await fetch(`/api/agents/${agentId}`, { method: 'DELETE' });
      if (!response.ok) {
        throw new Error('Failed to delete agent');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Agent deleted', description: 'Agent has been successfully deleted.' });
      queryClient.invalidateQueries({ queryKey: ['/api/agents'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to delete agent: ${error.message}`, variant: 'destructive' });
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
            <Button onClick={() => createAgent.mutate({ name: 'New Agent', type: 'Generic' })} data-testid="button-create-agent" disabled={createAgent.isPending}>
              {createAgent.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
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
              {agents?.map((agent: Agent) => (
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
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => restartAgent.mutate(agent.id)}
                        data-testid={`button-restart-${agent.id}`}
                        disabled={restartAgent.isPending}
                      >
                        {restartAgent.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCcw className="h-4 w-4" />}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteAgent.mutate(agent.id)}
                        data-testid={`button-delete-${agent.id}`}
                        disabled={deleteAgent.isPending}
                      >
                        {deleteAgent.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
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
              {agents?.filter((a: Agent) => a.status === 'running').length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm text-muted-foreground">Avg Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {Math.round(agents?.reduce((acc: number, a: Agent) => acc + a.health, 0)! / agents?.length!)}%
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
