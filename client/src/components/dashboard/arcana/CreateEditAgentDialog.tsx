import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuth } from '@/hooks/use-auth';
import { ArcanaAgent } from '@/types/system';
import { useToast } from '@/hooks/use-toast';
import { Loader2 } from 'lucide-react';

interface CreateEditAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  agent?: ArcanaAgent | null; // If provided, it's for editing
}

interface LLMModel {
  id: string;
  model_name: string;
  provider_id: string;
}

const CreateEditAgentDialog: React.FC<CreateEditAgentDialogProps> = ({ isOpen, onClose, agent }) => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [name, setName] = useState(agent?.name || '');
  const [persona, setPersona] = useState(agent?.persona || 'default');
  const [mode, setMode] = useState(agent?.mode || 'tool_user');
  const [objective, setObjective] = useState(agent?.objective || '');
  const [targetRepoPath, setTargetRepoPath] = useState(agent?.configuration?.target_repo_path || '');
  const [targetBranch, setTargetBranch] = useState(agent?.configuration?.target_branch || '');
  const [defaultModelId, setDefaultModelId] = useState(agent?.configuration?.default_model_id || '');

  useEffect(() => {
    if (agent) {
      setName(agent.name);
      setPersona(agent.persona);
      setMode(agent.mode);
      setObjective(agent.objective || '');
      setTargetRepoPath(agent.configuration?.target_repo_path || '');
      setTargetBranch(agent.configuration?.target_branch || '');
      setDefaultModelId(agent.configuration?.default_model_id || '');
    } else {
      // Reset form for new agent creation
      setName('');
      setPersona('default');
      setMode('tool_user');
      setObjective('');
      setTargetRepoPath('');
      setTargetBranch('');
      setDefaultModelId('');
    }
  }, [agent, isOpen]);

  const { data: llmModels, isLoading: isLoadingLlmModels } = useQuery<LLMModel[]>({
    queryKey: ['cognisysLLMModels'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/models/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch LLM models');
      return response.json();
    },
    enabled: isOpen && !!token, // Only fetch when dialog is open and token is available
  });

  const createAgentMutation = useMutation({
    mutationFn: (newAgentData: any) => {
      return fetch('/api/arcana/agents/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newAgentData),
      }).then(res => {
        if (!res.ok) throw new Error('Failed to create agent');
        return res.json();
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['arcanaAgents'] });
      toast({ title: 'Agent Created', description: 'New Arcana agent has been successfully created.' });
      onClose();
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: `Failed to create agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const updateAgentMutation = useMutation({
    mutationFn: (updatedAgentData: any) => {
      if (!agent) throw new Error("Agent ID not available for update");
      return fetch(`/api/arcana/agents/${agent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(updatedAgentData),
      }).then(res => {
        if (!res.ok) throw new Error('Failed to update agent');
        return res.json();
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['arcanaAgents'] });
      toast({ title: 'Agent Updated', description: 'Arcana agent has been successfully updated.' });
      onClose();
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: `Failed to update agent: ${error.message}`, variant: 'destructive' });
    },
  });

  const handleSubmit = () => {
    const agentData = {
      name,
      persona,
      mode,
      objective,
      configuration: {
        target_repo_path: targetRepoPath,
        target_branch: targetBranch,
        default_model_id: defaultModelId,
      },
    };

    if (agent) {
      updateAgentMutation.mutate(agentData);
    } else {
      createAgentMutation.mutate(agentData);
    }
  };

  const isSubmitting = createAgentMutation.isPending || updateAgentMutation.isPending;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{agent ? 'Edit Arcana Agent' : 'Create New Arcana Agent'}</DialogTitle>
          <DialogDescription>
            {agent ? 'Modify the details of your agent.' : 'Configure a new autonomous AI agent.'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input id="name" value={name} onChange={(e) => setName(e.target.value)} className="col-span-3" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="persona" className="text-right">
              Persona
            </Label>
            <Input id="persona" value={persona} onChange={(e) => setPersona(e.target.value)} className="col-span-3" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="mode" className="text-right">
              Mode
            </Label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="Select agent mode" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="chat">Chat</SelectItem>
                <SelectItem value="tool_user">Tool User</SelectItem>
                <SelectItem value="autonomous">Autonomous</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="objective" className="text-right">
              Objective
            </Label>
            <Textarea id="objective" value={objective} onChange={(e) => setObjective(e.target.value)} className="col-span-3" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="targetRepoPath" className="text-right">
              Target Repo Path
            </Label>
            <Input id="targetRepoPath" value={targetRepoPath} onChange={(e) => setTargetRepoPath(e.target.value)} className="col-span-3" placeholder="e.g., /app/my-project" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="targetBranch" className="text-right">
              Target Branch
            </Label>
            <Input id="targetBranch" value={targetBranch} onChange={(e) => setTargetBranch(e.target.value)} className="col-span-3" placeholder="e.g., main" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="defaultModelId" className="text-right">
              Default LLM
            </Label>
            <Select value={defaultModelId} onValueChange={setDefaultModelId} disabled={isLoadingLlmModels}>
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="Select default LLM model" />
              </SelectTrigger>
              <SelectContent>
                {isLoadingLlmModels ? (
                  <SelectItem value="loading" disabled>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading models...
                  </SelectItem>
                ) : (
                  llmModels?.map((model) => (
                    <SelectItem key={model.id} value={model.id}>
                      {model.model_name} ({model.provider_id})
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            {agent ? 'Save Changes' : 'Create Agent'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateEditAgentDialog;
