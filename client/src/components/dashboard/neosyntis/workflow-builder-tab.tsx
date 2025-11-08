import { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  type Connection,
  type Node,
  type Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge } from '@/components/ui';
import { Workflow, Play, Save, Plus, Activity } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/dashboard/use-toast';

const nodeTypes = {
  input: ({ data }: { data: any }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-green-500">
      <div className="text-xs font-bold text-green-600">INPUT</div>
      <div className="text-sm">{data.label}</div>
    </div>
  ),
  llm: ({ data }: { data: any }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-primary">
      <div className="text-xs font-bold text-primary">LLM</div>
      <div className="text-sm">{data.label}</div>
      {data.model && <div className="text-xs text-muted-foreground">{data.model}</div>}
    </div>
  ),
  action: ({ data }: { data: any }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-accent">
      <div className="text-xs font-bold text-accent">ACTION</div>
      <div className="text-sm">{data.label}</div>
    </div>
  ),
  output: ({ data }: { data: any }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-orange-500">
      <div className="text-xs font-bold text-orange-600">OUTPUT</div>
      <div className="text-sm">{data.label}</div>
    </div>
  ),
  delay: ({ data }: { data: any }) => (
    <div className="px-4 py-2 shadow-md rounded-md bg-card border-2 border-yellow-500">
      <div className="text-xs font-bold text-yellow-600">DELAY</div>
      <div className="text-sm">{data.label}</div>
    </div>
  ),
};

export default function WorkflowBuilderTab() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [workflowId, setWorkflowId] = useState<string | null>(null); // State to hold the current workflow ID

  const { data: workflowData, isLoading, error } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: async () => {
      if (!workflowId) return { nodes: [], edges: [] }; // Return empty if no workflowId
      const response = await fetch(`/api/workflows/${workflowId}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
    enabled: !!workflowId, // Only run query if workflowId is available
    initialData: { nodes: [], edges: [] },
  });

  const [nodes, setNodes, onNodesChange] = useNodesState(workflowData.nodes as Node[]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(workflowData.edges as Edge[]);

  useEffect(() => {
    setNodes(workflowData.nodes as Node[]);
    setEdges(workflowData.edges as Edge[]);
  }, [workflowData, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const saveWorkflowMutation = useMutation({
    mutationFn: async (workflow: { nodes: Node[]; edges: Edge[] }) => {
      const method = workflowId ? 'PUT' : 'POST';
      const url = workflowId ? `/api/workflows/${workflowId}` : '/api/workflows';
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflow),
      });
      if (!response.ok) {
        throw new Error('Failed to save workflow');
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast({ title: 'Workflow Saved', description: 'Workflow has been successfully saved.' });
      if (!workflowId && data.id) {
        setWorkflowId(data.id); // Set workflowId if it's a new workflow
      }
      queryClient.invalidateQueries({ queryKey: ['workflow', workflowId] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to save workflow: ${err.message}`, variant: 'destructive' });
    },
  });

  const runWorkflowMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`/api/workflows/${id}/run`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to run workflow');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Workflow Started', description: 'Workflow execution initiated.' });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to run workflow: ${err.message}`, variant: 'destructive' });
    },
  });

  const addNodeMutation = useMutation({
    mutationFn: async (nodeData: any) => {
      if (!workflowId) {
        throw new Error('Cannot add node without a workflow. Please save the workflow first.');
      }
      const response = await fetch(`/api/workflows/${workflowId}/nodes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nodeData),
      });
      if (!response.ok) {
        throw new Error('Failed to add node');
      }
      return response.json();
    },
    onSuccess: (newNode) => {
      setNodes((nds) => nds.concat(newNode));
      toast({ title: 'Node Added', description: 'New node added to workflow.' });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to add node: ${err.message}`, variant: 'destructive' });
    },
  });

  if (isLoading) {
    return <div className="p-6 text-center">Loading workflow...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">Error loading workflow: {error.message}</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Workflow className="h-5 w-5 text-primary" />
                Workflow Builder
              </CardTitle>
              <CardDescription className="mt-1">
                Create agentic workflows with drag-and-drop node editor
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                data-testid="button-add-node"
                onClick={() => addNodeMutation.mutate({
                  id: `node-${Date.now()}`,
                  type: 'llm',
                  position: { x: Math.random() * 250, y: Math.random() * 250 },
                  data: { label: 'New LLM Node', model: 'GPT-3.5' },
                })}
                disabled={addNodeMutation.isPending || !workflowId}
              >
                {addNodeMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                Add Node
              </Button>
              <Button
                variant="outline"
                data-testid="button-save-workflow"
                onClick={() => saveWorkflowMutation.mutate({ nodes, edges })}
                disabled={saveWorkflowMutation.isPending}
              >
                {saveWorkflowMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save
              </Button>
              <Button
                data-testid="button-run-workflow"
                onClick={() => workflowId && runWorkflowMutation.mutate(workflowId)}
                disabled={runWorkflowMutation.isPending || !workflowId}
              >
                {runWorkflowMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                Run
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card className="h-[600px]">
        <CardContent className="h-full p-0">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            className="bg-background h-[500px]"
          >
            <Controls />
            <MiniMap className="bg-card border" />
            <Background gap={12} size={1} />
          </ReactFlow>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Available Node Types</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="border-green-500 text-green-600">
              Input - Entry point
            </Badge>
            <Badge variant="outline" className="border-primary text-primary">
              LLM - AI Processing
            </Badge>
            <Badge variant="outline" className="border-accent text-accent">
              Action - Execute Task
            </Badge>
            <Badge variant="outline" className="border-orange-500 text-orange-600">
              Output - Result
            </Badge>
            <Badge variant="outline" className="border-yellow-500 text-yellow-600">
              Delay - Wait Timer
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
