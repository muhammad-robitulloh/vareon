import { useCallback } from 'react';
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Workflow, Play, Save, Plus } from 'lucide-react';
import { mockWorkflowNodes, mockWorkflowEdges } from '@/pages/Dashboard/client/src/lib/mockApi';

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
  const [nodes, onNodesChange] = useNodesState(mockWorkflowNodes as Node[]);
  const [edges, setEdges, onEdgesChange] = useEdgesState(mockWorkflowEdges as Edge[]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

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
              <Button variant="outline" data-testid="button-add-node">
                <Plus className="h-4 w-4 mr-2" />
                Add Node
              </Button>
              <Button variant="outline" data-testid="button-save-workflow">
                <Save className="h-4 w-4 mr-2" />
                Save
              </Button>
              <Button data-testid="button-run-workflow">
                <Play className="h-4 w-4 mr-2" />
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
            className="bg-background"
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
