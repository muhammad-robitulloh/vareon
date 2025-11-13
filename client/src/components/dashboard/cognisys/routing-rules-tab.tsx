import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Input, Label, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from '@/components/ui';
import { useAuth } from '@/hooks/use-auth';
import { GitBranch, Plus, Trash2, Activity } from 'lucide-react';
import { useToast } from '@/hooks/dashboard/use-toast';
import ConditionBuilder from './ConditionBuilder';
import AddModelForm from './AddModelForm'; // Import AddModelForm

export default function RoutingRulesTab() {
  const { token } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const [newRuleIntent, setNewRuleIntent] = useState('');
  const [newRuleCondition, setNewRuleCondition] = useState<any>({ id: 'root', combinator: 'and', rules: [] });
  const [newRuleTargetModel, setNewRuleTargetModel] = useState('');
  const [newRulePriority, setNewRulePriority] = useState(1);

  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);
  const [isAddModelDialogOpen, setIsAddModelDialogOpen] = useState(false);

  const handleAddModel = (modelData: any) => {
    addModelMutation.mutate({
      model_name: modelData.modelName,
      provider_id: modelData.providerId,
      type: modelData.modelType,
      is_active: true, // Default to active
      role: 'general', // Default role
      max_tokens: modelData.maxTokens,
      cost_per_token: modelData.costPerToken,
    });
    setIsAddModelDialogOpen(false);
  };

  const { data: routingRules, isLoading, error } = useQuery({
    queryKey: ['cognisysRoutingRules'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/routing-rules/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response:", errorBody);
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText} - ${errorBody}`);
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

  const { data: llmModels, isLoading: isLoadingModels, error: modelsError } = useQuery({
    queryKey: ['cognisysLLMModels'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/models/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LLM models');
      }
      return response.json();
    },
    enabled: !!token,
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

  const createRuleMutation = useMutation({
    mutationFn: async (ruleData: { intent: string; condition: any; targetModel: string; priority: number }) => {
      const response = await fetch('/api/cognisys/routing-rules/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: ruleData.intent, // Map intent to name
          condition: JSON.stringify(ruleData.condition),
          target_model: ruleData.targetModel, // Map targetModel to target_model
          priority: ruleData.priority,
        }),
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response (Create Rule):", errorBody);
        throw new Error(`Failed to create routing rule: ${response.status} ${response.statusText} - ${errorBody}`);
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Rule Created', description: 'New routing rule has been successfully created.' });
      setNewRuleIntent('');
      setNewRuleCondition({ id: 'root', combinator: 'and', rules: [] });
      setNewRuleTargetModel('');
      setNewRulePriority(1);
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to create rule: ${err.message}`, variant: 'destructive' });
    },
  });

  const updateRuleMutation = useMutation({
    mutationFn: async ({ ruleId, ruleData }: { ruleId: string, ruleData: { intent: string; condition: any; targetModel: string; priority: number } }) => {
      const response = await fetch(`/api/cognisys/routing-rules/${ruleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: ruleData.intent, // Map intent to name
          condition: JSON.stringify(ruleData.condition),
          target_model: ruleData.targetModel, // Map targetModel to target_model
          priority: ruleData.priority,
        }),
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response (Update Rule):", errorBody);
        throw new Error(`Failed to update routing rule: ${response.status} ${response.statusText} - ${errorBody}`);
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Rule Updated', description: 'Routing rule has been successfully updated.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysRoutingRules'] });
      setEditingRuleId(null);
      setNewRuleIntent('');
      setNewRuleCondition({ id: 'root', combinator: 'and', rules: [] });
      setNewRuleTargetModel('');
      setNewRulePriority(1);
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to update rule: ${err.message}`, variant: 'destructive' });
    },
  });

  const deleteRuleMutation = useMutation({
    mutationFn: async (ruleId: string) => {
      const response = await fetch(`/api/cognisys/routing-rules/${ruleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response (Delete Rule):", errorBody);
        throw new Error(`Failed to delete routing rule: ${response.status} ${response.statusText} - ${errorBody}`);
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Rule Deleted', description: 'Routing rule has been successfully deleted.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysRoutingRules'] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to delete rule: ${err.message}`, variant: 'destructive' });
    },
  });
  if (isLoading) {
    return <div className="p-6 text-center">Loading routing rules...</div>;
  }

  if (error) {
    console.error("Error loading routing rules:", error);
    return <div className="p-6 text-center text-red-500">Error loading routing rules: {error.message}</div>;
  }

  console.log("Routing Rules:", routingRules);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-primary" />
                Routing Rules
              </CardTitle>
              <CardDescription className="mt-1">
                Define intent-based routing to appropriate models
              </CardDescription>
            </div>
            <Button
              data-testid="button-add-rule"
              onClick={() => createRuleMutation.mutate({
                intent: newRuleIntent,
                condition: newRuleCondition,
                targetModel: newRuleTargetModel,
                priority: newRulePriority,
              })}
              disabled={createRuleMutation.isPending || !newRuleIntent || !newRuleCondition || !newRuleTargetModel}
            >
              {createRuleMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
              Add Rule
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Intent Type</Label>
              <Select value={newRuleIntent} onValueChange={setNewRuleIntent}>
                <SelectTrigger data-testid="select-intent-type">
                  <SelectValue placeholder="Select intent..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="code_generation">Code Generation</SelectItem>
                  <SelectItem value="reasoning">Reasoning</SelectItem>
                  <SelectItem value="conversation">Conversation</SelectItem>
                  <SelectItem value="summarization">Summarization</SelectItem>
                  <SelectItem value="shell_command">Shell Command</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Condition</Label>
              <ConditionBuilder root={newRuleCondition} setRoot={setNewRuleCondition} />
            </div>
            <div className="space-y-2">
              <Label>Target Model</Label>
              <div className="flex items-center gap-2">
                <Select value={newRuleTargetModel} onValueChange={setNewRuleTargetModel}>
                  <SelectTrigger data-testid="select-target-model">
                    <SelectValue placeholder="Select model..." />
                  </SelectTrigger>
                  <SelectContent>
                    {llmModels?.map((model: any) => (
                      <SelectItem key={model.id} value={model.model_name}>
                        {model.model_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Dialog open={isAddModelDialogOpen} onOpenChange={setIsAddModelDialogOpen}>
                  <DialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="icon"
                    >
                      <Plus className="h-4 w-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[425px]">
                    <DialogHeader>
                      <DialogTitle>Add New Model</DialogTitle>
                      <DialogDescription>
                        Add a new LLM model to your system.
                      </DialogDescription>
                    </DialogHeader>
                    <AddModelForm
                      onAddModel={handleAddModel}
                      providers={providers || []}
                    />
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Active Rules</CardTitle>
          <CardDescription>
            Rules are evaluated in order of priority
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <p className="text-muted-foreground">Loading rules...</p>
          ) : error ? (
            <p className="text-red-500">Error loading rules: {(error as Error).message}</p>
          ) : (
            <>
              {Array.isArray(routingRules) && routingRules.length > 0 ? (
                routingRules.map((rule: any) => {
                  try {
                    return (
                      <Card key={rule.id} className="bg-card/50">
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <Badge variant="default" className="text-xs">
                                  {rule.name.replace(/_/g, ' ')}
                                </Badge>
                                <Badge variant="outline" className="text-xs">
                                  Priority {rule.priority}
                                </Badge>
                              </div>
                              <div className="mt-2">
                                <div className="text-xs text-muted-foreground mb-1">Condition:</div>
                                <div className="text-sm font-mono bg-muted/30 px-2 py-1 rounded">
                                  {rule.condition}
                                </div>
                              </div>
                              <div className="mt-2">
                                <div className="text-xs text-muted-foreground mb-1">Target:</div>
                                <Badge variant="secondary" className="text-xs">
                                  {rule.targetModel}
                                </Badge>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="ghost" size="sm" onClick={() => {
                                setEditingRuleId(rule.id);
                                setNewRuleIntent(rule.intent);
                                try {
                                  setNewRuleCondition(JSON.parse(rule.condition));
                                } catch (e) {
                                  console.error("Failed to parse rule condition:", e);
                                  setNewRuleCondition({ id: 'root', combinator: 'and', rules: [] });
                                }
                                setNewRuleTargetModel(rule.targetModel);
                                setNewRulePriority(rule.priority);
                              }}>Edit</Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                data-testid={`button-delete-rule-${rule.id}`}
                                onClick={() => deleteRuleMutation.mutate(rule.id)}
                                disabled={deleteRuleMutation.isPending}
                              >
                                {deleteRuleMutation.isPending ? <Activity className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                              </Button>
                            </div>
                          </div>
                        </CardHeader>
                      </Card>
                    );
                  } catch (renderError: any) {
                    console.error(`Error rendering rule with ID ${rule.id || 'unknown'}:`, renderError);
                    return (
                      <Card key={`error-${rule.id || Math.random()}`} className="bg-red-100 border-red-400 text-red-700 p-4 mb-2">
                        <p>Error rendering rule. Please check console for details.</p>
                        {rule.id && <p>Rule ID: {rule.id}</p>}
                        <p>Error: {renderError.message}</p>
                      </Card>
                    );
                  }
                })
              ) : (
                <p className="text-muted-foreground">No routing rules found.</p>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {editingRuleId && (
        <Card>
          <CardHeader>
            <CardTitle>Edit Rule</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Intent Type</Label>
                <Select value={newRuleIntent} onValueChange={setNewRuleIntent}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select intent..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="code_generation">Code Generation</SelectItem>
                    <SelectItem value="reasoning">Reasoning</SelectItem>
                    <SelectItem value="conversation">Conversation</SelectItem>
                    <SelectItem value="summarization">Summarization</SelectItem>
                    <SelectItem value="shell_command">Shell Command</SelectItem>
                    <SelectItem value="custom">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Condition</Label>
                <ConditionBuilder root={newRuleCondition} setRoot={setNewRuleCondition} />
              </div>
              <div className="space-y-2">
                <Label>Target Model</Label>
                <div className="flex items-center gap-2">
                  <Select value={newRuleTargetModel} onValueChange={setNewRuleTargetModel}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select model..." />
                    </SelectTrigger>
                    <SelectContent>
                      {llmModels?.map((model: any) => (
                        <SelectItem key={model.id} value={model.model_name}>
                          {model.model_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    variant="outline"
                    size="icon"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="ghost" onClick={() => setEditingRuleId(null)}>Cancel</Button>
              <Button
                onClick={() => {
                  updateRuleMutation.mutate({
                    ruleId: editingRuleId,
                    ruleData: {
                      intent: newRuleIntent,
                      condition: newRuleCondition, // This will be stringified in the mutationFn
                      targetModel: newRuleTargetModel,
                      priority: newRulePriority,
                    },
                  });
                }}
                disabled={updateRuleMutation.isPending}
              >
                {updateRuleMutation.isPending ? <Activity className="h-4 w-4 mr-2 animate-spin" /> : null}
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Routing Logic</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            COGNISYS evaluates each request against routing rules in priority order:
          </p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Intent detection identifies the request type</li>
            <li>Matching rules are found based on conditions</li>
            <li>Highest priority matching rule determines the target model</li>
            <li>Request is routed to the selected model</li>
            <li>Optional reasoning step is applied if configured</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
