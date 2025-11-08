import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';
import { Terminal, Send, Trash2, Network, GitBranch, Brain } from 'lucide-react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

const getReasoningFlow = (query: string) => {
  const nodes: Node[] = [
    { id: '1', type: 'input', data: { label: `Query: "${query}"` }, position: { x: 250, y: 5 } },
    { id: '2', data: { label: 'Intent Analysis' }, position: { x: 250, y: 100 } },
    { id: '3', data: { label: 'ARCANA (Conversational)' }, position: { x: 50, y: 200 } },
    { id: '4', data: { label: 'MYNTRIX (Operational)' }, position: { x: 250, y: 200 } },
    { id: '5', data: { label: 'NEOSYNTIS (Analytical)' }, position: { x: 450, y: 200 } },
    { id: '6', type: 'output', data: { label: 'Decision: Route to ARCANA' }, position: { x: 250, y: 300 } },
  ];

  const edges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2', animated: true },
    { id: 'e2-3', source: '2', target: '3', label: '85% confidence' },
    { id: 'e2-4', source: '2', target: '4', label: '10% confidence' },
    { id: 'e2-5', source: '2', target: '5', label: '5% confidence' },
    { id: 'e3-6', source: '3', target: '6', animated: true, style: { stroke: '#10b981' } },
  ];

  return { nodes, edges };
};

export default function TestConsoleTab() {
  const [prompt, setPrompt] = useState('Hello, can you summarize a document for me?');
  const [selectedModel, setSelectedModel] = useState('auto');
  const [messages, setMessages] = useState<Array<{
    role: 'user' | 'assistant';
    content: string;
    model?: string;
    tokens?: number;
  }>>([]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const handleSend = () => {
    if (!prompt.trim()) return;

    const newMessages = [
      ...messages,
      { role: 'user' as const, content: prompt },
      {
        role: 'assistant' as const,
        content: 'This is a mock response. The visualization on the right shows the routing logic.',
        model: selectedModel === 'auto' ? 'GPT-4 (auto-routed)' : selectedModel,
        tokens: Math.floor(Math.random() * 500) + 100,
      },
    ];
    setMessages(newMessages);

    if (selectedModel === 'auto') {
      const { nodes: newNodes, edges: newEdges } = getReasoningFlow(prompt);
      setNodes(newNodes);
      setEdges(newEdges);
    }

    setPrompt('');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-primary" />
              Test Console
            </CardTitle>
            <CardDescription>
              Test prompts and verify routing behavior. The visualization will appear on the right when using auto-routing.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-3">
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="auto">Auto-route</SelectItem>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                </SelectContent>
              </Select>
              <Input
                placeholder="Enter test prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="flex-1"
              />
              <Button onClick={handleSend}><Send className="h-4 w-4" /></Button>
              {messages.length > 0 && (
                <Button variant="outline" onClick={() => setMessages([])}><Trash2 className="h-4 w-4" /></Button>
              )}
            </div>
          </CardContent>
        </Card>

        {messages.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Conversation</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {messages.map((message, idx) => (
                <div key={idx} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg p-4 ${message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card border'}`}>
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    {message.model && (
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant="secondary" className="text-xs">{message.model}</Badge>
                        {message.tokens && <span className="text-xs text-muted-foreground">{message.tokens} tokens</span>}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      <Card className="h-[600px]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            Reasoning & Routing Visualization
          </CardTitle>
        </CardHeader>
        <CardContent className="h-[calc(100%-4rem)]">
          {nodes.length > 0 ? (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              fitView
            >
              <Controls />
              <MiniMap />
              <Background gap={12} size={1} />
            </ReactFlow>
          ) : (
            <div className="flex items-center justify-center h-full text-center text-muted-foreground">
              <p>Run a query with auto-routing to see the visualization.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
