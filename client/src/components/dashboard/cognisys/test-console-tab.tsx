import { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Label } from '@/components/ui';
import { Terminal, Send, Trash2, Network, GitBranch, Brain, Loader2, Plus } from 'lucide-react';
import { ReactFlow, MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/use-toast';

// --- Interfaces ---
interface LLMModel {
  id: string;
  provider_id: string;
  model_name: string;
  type: string;
  is_active: boolean;
  reasoning: boolean;
  role?: string;
  max_tokens: number;
  cost_per_token: number;
  created_at: string;
  updated_at: string;
}

interface ChatRequest {
  prompt: string;
  model_name?: string; // Optional, for direct model selection
  conversation_id?: string; // Optional, for continuing a conversation
}

interface ChatResponse {
  response: string;
  model_used: string;
  conversation_id?: string; // New: ID of the conversation
  message_id?: string; // New: ID of the LLM's response message
  visualization_data?: {
    nodes: Node[];
    edges: Edge[];
  };
}

interface IntentDetectionResponse {
  intent: string;
  confidence: number;
  reasoning: string;
}

interface ChatMessage {
  id: string;
  conversation_id: string;
  user_id: string;
  sender: 'user' | 'llm';
  message_content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

// Placeholder for initial nodes/edges, will be replaced by actual data
const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

export default function TestConsoleTab() {
  const { toast } = useToast();
  const { token } = useAuth();
  const queryClient = useQueryClient();

  const [prompt, setPrompt] = useState('');
  const [selectedModel, setSelectedModel] = useState('auto'); // 'auto' or a model_name
  const [messages, setMessages] = useState<ChatMessage[]>([]); // Use ChatMessage interface
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: any) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  // --- Fetch Conversations ---
  const { data: fetchedConversations, isLoading: isLoadingConversations, error: conversationsError } = useQuery<Conversation[]> ({
    queryKey: ['cognisysConversations'],
    queryFn: async () => {
      const response = await fetch('/api/chat/conversations', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch conversations');
      }
      return response.json();
    },
    enabled: !!token,
  });

  useEffect(() => {
    if (fetchedConversations) {
      setConversations(fetchedConversations);
      if (!selectedConversationId && fetchedConversations.length > 0) {
        setSelectedConversationId(fetchedConversations[0].id); // Auto-select the most recent conversation
      }
    }
  }, [fetchedConversations, selectedConversationId]);

  // --- Fetch Chat History for selected conversation ---
  const { data: fetchedMessages, isLoading: isLoadingMessages, error: messagesError } = useQuery<ChatMessage[]> ({
    queryKey: ['cognisysChatHistory', selectedConversationId],
    queryFn: async () => {
      if (!selectedConversationId) return [];
      const response = await fetch(`/api/chat/history/${selectedConversationId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }
      return response.json();
    },
    enabled: !!selectedConversationId && !!token,
  });

  useEffect(() => {
    if (fetchedMessages) {
      setMessages(fetchedMessages);
    }
  }, [fetchedMessages]);

  // --- Fetch LLM Models ---
  const { data: llmModels, isLoading: isLoadingModels, error: modelsError } = useQuery<LLMModel[]>({
    queryKey: ['cognisysLLMModels'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/models/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LLM models');
      }
      return response.json();
    },
    enabled: !!token,
  });

  const { data: providers, isLoading: isLoadingProviders, error: providersError } = useQuery({
    queryKey: ['cognisysProviders'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/providers/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch providers');
      }
      return response.json();
    },
    enabled: !!token,
  });

  // --- Chat Mutation ---
  const chatMutation = useMutation({
    mutationFn: async (chatRequest: ChatRequest) => {
      const response = await fetch('/api/cognisys/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(chatRequest),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get chat response');
      }
      return response.json();
    },
    onSuccess: (data: ChatResponse) => {
      // Update selectedConversationId if a new conversation was created
      if (data.conversation_id && data.conversation_id !== selectedConversationId) {
        setSelectedConversationId(data.conversation_id);
        queryClient.invalidateQueries({ queryKey: ['cognisysConversations'] }); // Refresh conversations list
      }
      queryClient.invalidateQueries({ queryKey: ['cognisysChatHistory', selectedConversationId] }); // Refresh chat history
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Chat failed: ${err.message}`, variant: 'destructive' });
    },
  });

  const addModelMutation = useMutation({
    mutationFn: async (modelData: any) => {
      const response = await fetch('/api/cognisys/models/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(modelData),
      });
      if (!response.ok) {
        throw new Error('Failed to create model');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Model Created', description: 'New model has been successfully created.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMModels'] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to create model: ${err.message}`, variant: 'destructive' });
    },
  });

  const handleAddModel = (modelData: any) => {
    addModelMutation.mutate(modelData);
    // This is a bit of a hack to close the toast. A better way would be to use a modal.
    const closeButton = document.querySelector('[data-radix-toast-close-button]');
    if (closeButton) {
      (closeButton as HTMLElement).click();
    }
  };

  const openAddModelToast = () => {
    toast({
      title: "Add New Model",
      description: (
        <AddModelForm
          onAddModel={handleAddModel}
          providers={providers || []}
        />
      ),
    });
  };

  // --- Intent Detection Mutation (if needed separately, but chat endpoint handles it) ---
  // The /cognisys/chat endpoint is designed to handle intent detection and routing internally.
  // So, a separate intent detection mutation might not be directly needed here for the main flow.

  const handleSend = () => {
    if (!prompt.trim()) return;

    setMessages(prev => [...prev, {
      id: Date.now().toString(), // Temporary ID for frontend display
      conversation_id: selectedConversationId || 'temp', // Placeholder
      user_id: 'current_user', // Placeholder
      sender: 'user',
      message_content: prompt,
      timestamp: new Date().toISOString(), // Current timestamp
    }]);
    setPrompt(''); // Clear input immediately

    const chatRequest: ChatRequest = { prompt };
    if (selectedModel !== 'auto') {
      chatRequest.model_name = selectedModel;
    }
    if (selectedConversationId) {
      chatRequest.conversation_id = selectedConversationId;
    }

    chatMutation.mutate(chatRequest);
  };

  if (isLoadingModels) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading models...</div>;
  if (modelsError) return <div className="p-4 text-center text-red-500">Error loading models: {modelsError.message}</div>;

  const deleteConversationMutation = useMutation({
    mutationFn: async (conversationId: string) => {
      const response = await fetch(`/api/chat/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to delete conversation');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Success', description: 'Conversation deleted.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysConversations'] });
      setSelectedConversationId(null); // Clear selected conversation
      setMessages([]); // Clear messages
      setNodes([]);
      setEdges([]);
    },
    onError: (err: Error) => {
      toast({ title: 'Error', description: `Failed to delete conversation: ${err.message}`, variant: 'destructive' });
    },
  });

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
            <div className="flex items-center gap-2">
              <Label htmlFor="conversation-select" className="sr-only">Select Conversation</Label>
              <Select
                value={selectedConversationId || ''}
                onValueChange={(value) => setSelectedConversationId(value)}
                disabled={isLoadingConversations}
              >
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Select conversation..." />
                </SelectTrigger>
                <SelectContent>
                  {conversations.map((conv) => (
                    <SelectItem key={conv.id} value={conv.id}>{conv.title}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSelectedConversationId(null); // Start a new conversation
                }}
              >
                <Plus className="h-4 w-4 mr-2" /> New Chat
              </Button>
              {selectedConversationId && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => deleteConversationMutation.mutate(selectedConversationId)}
                  disabled={deleteConversationMutation.isPending}
                >
                  {deleteConversationMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Trash2 className="h-4 w-4 mr-2" />}
                  Clear Chat
                </Button>
              )}
            </div>
            <div className="flex gap-3">
              <div className="flex items-center gap-2 flex-1">
                <Select value={selectedModel} onValueChange={setSelectedModel} disabled={chatMutation.isPending}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select model..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Auto-route</SelectItem>
                    {llmModels?.filter(m => m.is_active).map(model => (
                      <SelectItem key={model.id} value={model.model_name}>{model.model_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={openAddModelToast}
                  disabled={isLoadingProviders}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <Input
                placeholder="Enter test prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                className="flex-1"
                disabled={chatMutation.isPending}
              />
              <Button onClick={handleSend} disabled={chatMutation.isPending || !prompt.trim()}>
                {chatMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              </Button>
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
                <div key={idx} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-lg p-4 ${message.sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-card border'}`}>
                    <div className="text-sm whitespace-pre-wrap">{message.message_content}</div>
                    {/* message.model and message.tokens are not part of ChatMessage interface directly */}
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

function AddModelForm({ onAddModel, providers }: { onAddModel: (data: any) => void, providers: any[] }) {
  const [modelName, setModelName] = useState('');
  const [providerId, setProviderId] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onAddModel({
      model_name: modelName,
      provider_id: providerId,
      type: 'chat', // default type
      is_active: true,
      role: 'general' // default role
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label>Model Name</Label>
        <Input value={modelName} onChange={(e) => setModelName(e.target.value)} placeholder="e.g., gpt-4-turbo" />
      </div>
      <div>
        <Label>Provider</Label>
        <Select value={providerId} onValueChange={setProviderId}>
          <SelectTrigger>
            <SelectValue placeholder="Select provider..." />
          </SelectTrigger>
          <SelectContent>
            {providers.map((provider) => (
              <SelectItem key={provider.id} value={provider.id}>
                {provider.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <Button type="submit">Add Model</Button>
    </form>
  );
}
