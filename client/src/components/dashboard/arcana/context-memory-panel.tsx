import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardFooter, Button, Badge, ScrollArea } from '@/components/ui';
import { Play, Save, Trash2, X } from 'lucide-react';

// Type definitions for better type safety
interface PinnedDataset {
  id: string;
  name: string;
  size: string;
}

interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

interface ContextMemory {
  pinnedDatasets: PinnedDataset[];
  conversationHistory: ConversationMessage[];
}

// Mock API function for fetching data
const fetchContextMemory = async (): Promise<ContextMemory> => {
  // In a real app, you'd fetch this from your API
  return Promise.resolve({
    pinnedDatasets: [
      { id: 'ds1', name: 'financial_report_q3.csv', size: '1.2MB' },
      { id: 'ds2', name: 'user_feedback_analysis.json', size: '800KB' },
    ],
    conversationHistory: [
      { id: 'msg1', role: 'user', content: 'Summarize the key findings from the Q3 financial report.' },
      { id: 'msg2', role: 'assistant', content: 'The Q3 report shows a 15% increase in revenue, primarily driven by the new product line.' },
      { id: 'msg3', role: 'user', content: 'Which regions performed best?' },
    ],
  });
};

export default function ContextMemoryPanel() {
  const queryClient = useQueryClient();

  const { data: contextMemory, isLoading, error } = useQuery<ContextMemory, Error>({
    queryKey: ['arcanaContextMemory'],
    queryFn: fetchContextMemory,
  });

  const clearConversationMutation = useMutation({
    mutationFn: async () => {
      // TODO: Implement backend API call to clear conversation
      console.log('Clearing conversation history...');
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.setQueryData(['arcanaContextMemory'], (oldData: ContextMemory | undefined) => 
        oldData ? { ...oldData, conversationHistory: [] } : oldData
      );
    },
  });

  const removeDatasetMutation = useMutation({
    mutationFn: async (datasetId: string) => {
      // TODO: Implement backend API call to remove dataset
      console.log(`Removing dataset ${datasetId}...`);
      return Promise.resolve();
    },
    onSuccess: (_, datasetId) => {
      queryClient.setQueryData(['arcanaContextMemory'], (oldData: ContextMemory | undefined) =>
        oldData ? { ...oldData, pinnedDatasets: oldData.pinnedDatasets.filter(d => d.id !== datasetId) } : oldData
      );
    },
  });


  if (isLoading) {
    return (
      <div className="w-80 border-l bg-card/30 p-4 flex items-center justify-center">
        Loading context and memory...
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-80 border-l bg-card/30 p-4 text-red-500 flex items-center justify-center">
        Error loading context and memory: {error.message}
      </div>
    );
  }

  return (
    <div className="w-80 border-l bg-card/30">
      <div className="p-4 border-b">
        <h3 className="font-medium text-sm">Context & Memory</h3>
      </div>
      <ScrollArea className="h-[calc(100%-60px)] p-4">
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3 flex-row items-center justify-between">
              <CardTitle className="text-sm">Current Conversation</CardTitle>
              <Button variant="ghost" size="sm" onClick={() => clearConversationMutation.mutate()} className="gap-1 text-xs">
                <Trash2 className="h-3 w-3" />
                Clear
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {contextMemory && contextMemory.conversationHistory && contextMemory.conversationHistory.length > 0 ? (
                  contextMemory.conversationHistory.map((msg) => (
                    <div key={msg.id} className="text-xs p-2 bg-muted/30 rounded">
                      <p className={`font-semibold ${msg.role === 'user' ? 'text-blue-400' : 'text-green-400'}`}>{msg.role}</p>
                      <p className="text-muted-foreground">{msg.content}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No conversation history.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Pinned Datasets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {contextMemory && contextMemory.pinnedDatasets && contextMemory.pinnedDatasets.length > 0 ? (
                  contextMemory.pinnedDatasets.map((dataset) => (
                    <div key={dataset.id} className="flex items-center justify-between text-sm p-2 bg-muted/30 rounded group">
                      <span className="truncate pr-2">{dataset.name}</span>
                      <div className="flex items-center shrink-0">
                        <Badge variant="outline" className="text-xs mr-2">{dataset.size}</Badge>
                        <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100" onClick={() => removeDatasetMutation.mutate(dataset.id)}>
                           <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No pinned datasets.</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start gap-2" data-testid="button-run-myntrix">
                <Play className="h-4 w-4" />
                Run in Myntrix
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start gap-2" data-testid="button-save-neosyntis">
                <Save className="h-4 w-4" />
                Save to Neosyntis
              </Button>
            </CardContent>
          </Card>
        </div>
      </ScrollArea>
    </div>
  );
}