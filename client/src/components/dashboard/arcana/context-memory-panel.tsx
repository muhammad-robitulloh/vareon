import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter, Button, Badge, ScrollArea, Tabs, TabsContent, TabsList, TabsTrigger, Label, Switch, Slider } from '@/components/ui';
import { Brain, Edit, Trash2, User, FolderGit, MessageSquare, PlusCircle, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

// --- INTERFACES ---

interface ContextItem {
  id: string;
  key: string;
  value: Record<string, any>; // Value is now a JSON object
}

interface UserPreference extends ContextItem {
  source: string; // Specific field for UserPreference
}

interface ProjectKnowledge extends ContextItem {
  repo: string;
  summary: string;
  techStack: string[];
}

interface ConversationSnippet extends ContextItem {
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

interface CreateContextItemPayload {
  type: 'preference' | 'project' | 'conversation';
  key: string;
  value: Record<string, any>;
}

const createContextItem = async (payload: CreateContextItemPayload): Promise<any> => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/context_memory/item', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Failed to create context item');
  }
  return response.json();
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

  const [isCreateItemDialogOpen, setIsCreateItemDialogOpen] = useState(false);
  const [newItemType, setNewItemType] = useState<'preference' | 'project' | 'conversation'>('preference');
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState(''); // Storing as string, will parse to JSON

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

  const createMutation = useMutation({
    mutationFn: createContextItem,
    onSuccess: () => {
      toast({ title: "Success", description: "Context item created." });
      queryClient.invalidateQueries({ queryKey: ['arcanaContextMemory'] });
      setIsCreateItemDialogOpen(false);
      setNewKey('');
      setNewValue('');
    },
    onError: (error: Error) => {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    },
  });

  const handleDelete = (itemId: string) => {
    deleteMutation.mutate(itemId);
  };

  const handleCreateItem = () => {
    try {
      const parsedValue = JSON.parse(newValue);
      createMutation.mutate({ type: newItemType, key: newKey, value: parsedValue });
    } catch (e) {
      toast({ title: "Error", description: "Invalid JSON for value.", variant: "destructive" });
    }
  };

  if (isLoading) return <div className="p-4">Loading context memory...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error.message}</div>;

  return (
    <div className="h-full flex flex-col">
        <div className="p-6 border-b flex justify-between items-center">
            <h1 className="text-2xl font-bold flex items-center gap-2"><Brain className="h-6 w-6" /> Arcana Context Memory</h1>
            <Button onClick={() => setIsCreateItemDialogOpen(true)}><PlusCircle className="mr-2 h-4 w-4" /> Add Context Item</Button>
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
                                        <p><strong>Value:</strong> {JSON.stringify(pref.value)}</p>
                                        <p className="text-xs text-muted-foreground">Source: {pref.source}</p>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                        <TabsContent value="projects">
                            <div className="grid grid-cols-1 gap-4">
                                {contextMemory?.projectKnowledge.map(proj => (
                                    <ContextCard key={proj.id} title={proj.key} onEdit={() => {}} onDelete={() => handleDelete(proj.id)}>
                                        <p><strong>Repo:</strong> {proj.value.repo}</p>
                                        <p><strong>Summary:</strong> {proj.value.summary}</p>
                                        <div className="flex flex-wrap gap-2 mt-2">
                                            {proj.value.techStack?.map((tech: string) => <Badge key={tech} variant="secondary">{tech}</Badge>)}
                                        </div>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                        <TabsContent value="conversations">
                            <div className="grid grid-cols-1 gap-4">
                                {contextMemory?.conversationSnippets.map(conv => (
                                    <ContextCard key={conv.id} title={conv.key} onEdit={() => {}} onDelete={() => handleDelete(conv.id)}>
                                        <p>"{conv.value.summary}"</p>
                                        <p className="text-xs text-muted-foreground mt-2">Topic: {conv.value.topic}</p>
                                        <p className="text-xs text-muted-foreground">Timestamp: {conv.value.timestamp}</p>
                                    </ContextCard>
                                ))}
                            </div>
                        </TabsContent>
                    </ScrollArea>
                </Tabs>
            </div>
        </div>

        {/* Create Context Item Dialog */}
        <Dialog open={isCreateItemDialogOpen} onOpenChange={setIsCreateItemDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Context Item</DialogTitle>
              <DialogDescription>
                Store a new piece of information for Arcana to remember.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="itemType" className="text-right">
                  Type
                </Label>
                <Select value={newItemType} onValueChange={(value: 'preference' | 'project' | 'conversation') => setNewItemType(value)}>
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder="Select item type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="preference">Preference</SelectItem>
                    <SelectItem value="project">Project Knowledge</SelectItem>
                    <SelectItem value="conversation">Conversation Snippet</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="key" className="text-right">
                  Key
                </Label>
                <Input
                  id="key"
                  value={newKey}
                  onChange={(e) => setNewKey(e.target.value)}
                  className="col-span-3"
                />
              </div>
              <div className="grid grid-cols-4 items-start gap-4">
                <Label htmlFor="value" className="text-right">
                  Value (JSON)
                </Label>
                <Textarea
                  id="value"
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  className="col-span-3"
                  rows={5}
                  placeholder='e.g., {"language": "Python", "level": "advanced"}'
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateItemDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreateItem} disabled={createMutation.isPending}>
                {createMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Add Item
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
    </div>
  );
}