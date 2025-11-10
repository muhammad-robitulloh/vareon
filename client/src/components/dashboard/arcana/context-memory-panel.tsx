import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter, Button, Badge, ScrollArea, Tabs, TabsContent, TabsList, TabsTrigger, Label, Switch, Slider } from '@/components/ui';
import { Brain, Edit, Trash2, User, FolderGit, MessageSquare } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// --- INTERFACES ---

interface UserPreference {
  id: string;
  key: string;
  value: string;
  source: string;
}

interface ProjectKnowledge {
  id: string;
  repo: string;
  summary: string;
  techStack: string[];
}

interface ConversationSnippet {
  id: string;
  topic: string;
  summary: string;
  timestamp: string;
}

interface ContextMemory {
  userPreferences: UserPreference[];
  projectKnowledge: ProjectKnowledge[];
  conversationSnippets: ConversationSnippet[];
}

// --- API FUNCTIONS ---

const fetchContextMemory = async (): Promise<ContextMemory> => {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/context_memory/', {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
};

const deleteContextItem = async (itemId: string): Promise<void> => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`/api/context_memory/item/${itemId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete item');
    }
};


// --- COMPONENTS ---

const ContextCard = ({ title, children, onEdit, onDelete }: { title: string, children: React.ReactNode, onEdit: () => void, onDelete: () => void }) => (
    <Card>
        <CardHeader className="pb-4">
            <CardTitle className="text-base">{title}</CardTitle>
        </CardHeader>
        <CardContent className="text-sm">
            {children}
        </CardContent>
        <CardFooter className="gap-2">
            <Button variant="ghost" size="sm" onClick={onEdit}><Edit className="h-4 w-4 mr-2" /> Edit</Button>
            <Button variant="ghost" size="sm" className="text-red-500" onClick={onDelete}><Trash2 className="h-4 w-4 mr-2" /> Forget</Button>
        </CardFooter>
    </Card>
);


export default function ContextMemoryPanel() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: contextMemory, isLoading, error } = useQuery<ContextMemory, Error>({
    queryKey: ['arcanaContextMemory'],
    queryFn: fetchContextMemory,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteContextItem,
    onSuccess: () => {
      toast({ title: "Success", description: "Context item forgotten." });
      queryClient.invalidateQueries({ queryKey: ['arcanaContextMemory'] });
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const handleDelete = (itemId: string) => {
    deleteMutation.mutate(itemId);
  };

  if (isLoading) return <div className="p-4">Loading context memory...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error.message}</div>;

  return (
    <div className="h-full flex flex-col">
        <div className="p-6 border-b">
            <h1 className="text-2xl font-bold flex items-center gap-2"><Brain className="h-6 w-6" /> Arcana Context Memory</h1>
            <p className="text-muted-foreground">Configure Arcana's learning and view the contextual data it has recognized.</p>
        </div>
        <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
            {/* Left Column: Configuration */}
            <div className="md:col-span-1">
                <Card>
                    <CardHeader>
                        <CardTitle>Configuration</CardTitle>
                        <CardDescription>Adjust how Arcana learns from and uses your context.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="space-y-2">
                            <Label htmlFor="awareness-level">Context Awareness Level</Label>
                            <Slider id="awareness-level" defaultValue={[60]} max={100} step={10} />
                            <p className="text-xs text-muted-foreground">Higher levels use more context, improving relevance but may increase latency.</p>
                        </div>
                        <div className="space-y-4">
                            <Label>Context Sources</Label>
                            <div className="flex items-center justify-between">
                                <Label htmlFor="learn-conversations" className="font-normal">Learn from conversations</Label>
                                <Switch id="learn-conversations" defaultChecked />
                            </div>
                            <div className="flex items-center justify-between">
                                <Label htmlFor="learn-code" className="font-normal">Learn from code & repositories</Label>
                                <Switch id="learn-code" defaultChecked />
                            </div>
                            <div className="flex items-center justify-between">
                                <Label htmlFor="learn-shell" className="font-normal">Learn from shell commands</Label>
                                <Switch id="learn-shell" />
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button className="w-full">Save Configuration</Button>
                    </CardFooter>
                </Card>
            </div>

            {/* Right Column: Data Transparency */}
            <div className="md:col-span-2">
                <Tabs defaultValue="preferences">
                    <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="preferences"><User className="h-4 w-4 mr-2" />Preferences</TabsTrigger>
                        <TabsTrigger value="projects"><FolderGit className="h-4 w-4 mr-2" />Projects</TabsTrigger>
                        <TabsTrigger value="conversations"><MessageSquare className="h-4 w-4 mr-2" />Conversations</TabsTrigger>
                    </TabsList>
                    <ScrollArea className="h-[calc(100vh-200px)] mt-4">
                        <TabsContent value="preferences">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                                {contextMemory?.userPreferences.map(pref => (
                                    <ContextCard key={pref.id} title={pref.key} onEdit={() => {}} onDelete={() => handleDelete(pref.id)}>
                                        <p><strong>Value:</strong> {pref.value}</p>
                                        <p className="text-xs text-muted-foreground">Source: {pref.source}</p>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                        <TabsContent value="projects">
                            <div className="grid grid-cols-1 gap-4">
                                {contextMemory?.projectKnowledge.map(proj => (
                                    <ContextCard key={proj.id} title={proj.repo} onEdit={() => {}} onDelete={() => handleDelete(proj.id)}>
                                        <p>{proj.summary}</p>
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {proj.techStack.map(tech => <Badge key={tech} variant="secondary">{tech}</Badge>)}
                                        </div>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                        <TabsContent value="conversations">
                            <div className="grid grid-cols-1 gap-4">
                                {contextMemory?.conversationSnippets.map(conv => (
                                    <ContextCard key={conv.id} title={conv.topic} onEdit={() => {}} onDelete={() => handleDelete(conv.id)}>
                                        <p>"{conv.summary}"</p>
                                        <p className="text-xs text-muted-foreground mt-2">Recognized {conv.timestamp}</p>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                    </ScrollArea>
                </Tabs>
            </div>
        </div>
    </div>
  );
}