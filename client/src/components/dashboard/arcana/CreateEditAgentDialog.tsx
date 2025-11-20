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
import { Loader2, ChevronLeft, ChevronRight, HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface CreateEditAgentDialogProps {
  isOpen: boolean;
  onClose: () => void;
  agent?: ArcanaAgent | null;
}

interface LLMModel {
  id: string;
  model_name: string;
  provider_id: string;
}

interface GitHubRepo {
  id: number;
  full_name: string;
  html_url: string;
}

const personaTemplates = {
  'software_engineer': 'Act as a senior software engineer. Your primary goal is to write clean, efficient, and well-documented code to solve the given problem. You should be able to understand complex requirements, break them down into smaller tasks, and implement them using the best practices for the given programming language and framework.',
  'data_analyst': 'Act as a data analyst. Your main objective is to analyze data, identify trends, and generate insights. You should be proficient in using data analysis libraries and tools to process, visualize, and interpret data.',
  'code_reviewer': 'Act as a code reviewer. Your task is to review code for quality, correctness, and adherence to coding standards. You should be able to identify potential bugs, suggest improvements, and provide constructive feedback to the author.',
  'default': 'You are a helpful AI assistant.',
};

const CreateEditAgentDialog: React.FC<CreateEditAgentDialogProps> = ({ isOpen, onClose, agent }) => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [persona, setPersona] = useState('default');
  const [customPersona, setCustomPersona] = useState('');
  const [mode, setMode] = useState('tool_user');
  const [objective, setObjective] = useState('');
  const [targetRepoPath, setTargetRepoPath] = useState('');
  const [targetBranch, setTargetBranch] = useState('');
  const [defaultModelId, setDefaultModelId] = useState('');
  const [selectedRepoFullName, setSelectedRepoFullName] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setStep(1);
      if (agent) {
        setName(agent.name);
        const isPresetPersona = Object.keys(personaTemplates).includes(agent.persona);
        setPersona(isPresetPersona ? agent.persona : 'custom');
        setCustomPersona(isPresetPersona ? '' : agent.persona);
        setMode(agent.mode);
        setObjective(agent.objective || '');
        setTargetRepoPath(agent.configuration?.target_repo_path || '');
        setTargetBranch(agent.configuration?.target_branch || '');
        setDefaultModelId(agent.configuration?.default_model_id || '');
        // Extract repo full name from URL for editing
        if (agent.configuration?.target_repo_path) {
          try {
            const url = new URL(agent.configuration.target_repo_path);
            const pathParts = url.pathname.split('/').filter(p => p);
            if (pathParts.length >= 2) {
              setSelectedRepoFullName(`${pathParts[0]}/${pathParts[1]}`);
            }
          } catch (e) {
            // Not a valid URL, might be a path; handle as needed
            setSelectedRepoFullName(null);
          }
        } else {
          setSelectedRepoFullName(null);
        }
      } else {
        setName('');
        setPersona('default');
        setCustomPersona('');
        setMode('tool_user');
        setObjective(personaTemplates.default);
        setTargetRepoPath('');
        setTargetBranch('');
        setDefaultModelId('');
        setSelectedRepoFullName(null);
      }
    }
  }, [agent, isOpen]);

  const handlePersonaChange = (selectedPersona: string) => {
    setPersona(selectedPersona);
    if (selectedPersona !== 'custom') {
      setObjective(personaTemplates[selectedPersona as keyof typeof personaTemplates] || '');
    } else {
      setObjective('');
    }
  };

  const { data: llmModels, isLoading: isLoadingLlmModels } = useQuery<LLMModel[]>({
    queryKey: ['cognisysLLMModels'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/models/', { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error('Failed to fetch LLM models');
      return response.json();
    },
    enabled: isOpen && !!token,
  });

  const { data: githubRepos, isLoading: isLoadingGithubRepos } = useQuery<GitHubRepo[]>({
    queryKey: ['githubRepositories'],
    queryFn: async () => {
      const response = await fetch('/api/git/github/repositories', { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error('Failed to fetch GitHub repositories. Is the GitHub App connected?');
      return response.json();
    },
    enabled: isOpen && step === 3 && !!token,
  });

  const { data: repoBranches, isLoading: isLoadingRepoBranches } = useQuery<string[]>({
    queryKey: ['githubRepoBranches', selectedRepoFullName],
    queryFn: async () => {
      if (!selectedRepoFullName) return [];
      const [owner, repo] = selectedRepoFullName.split('/');
      const response = await fetch(`/api/git/github/repositories/${owner}/${repo}/branches`, { headers: { Authorization: `Bearer ${token}` } });
      if (!response.ok) throw new Error('Failed to fetch repository branches.');
      return response.json();
    },
    enabled: isOpen && step === 3 && !!selectedRepoFullName && !!token,
  });

  const handleRepoChange = (repoFullName: string) => {
    const selectedRepo = githubRepos?.find(r => r.full_name === repoFullName);
    if (selectedRepo) {
      setSelectedRepoFullName(repoFullName);
      setTargetRepoPath(selectedRepo.html_url);
      setTargetBranch(''); // Reset branch when repo changes
    }
  };

  const mutationOptions = {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['arcanaAgents'] });
      toast({ title: agent ? 'Agent Updated' : 'Agent Created', description: `Arcana agent has been successfully ${agent ? 'updated' : 'created'}.` });
      onClose();
    },
    onError: (error: any) => {
      toast({ title: 'Error', description: `Failed to ${agent ? 'update' : 'create'} agent: ${error.message}`, variant: 'destructive' });
    },
  };

  const createAgentMutation = useMutation({
    mutationFn: (newAgentData: any) => fetch('/api/arcana/agents/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(newAgentData),
    }).then(res => res.ok ? res.json() : Promise.reject(new Error('Failed to create agent'))),
    ...mutationOptions,
  });

  const updateAgentMutation = useMutation({
    mutationFn: (updatedAgentData: any) => {
      if (!agent) return Promise.reject(new Error("Agent ID not available"));
      return fetch(`/api/arcana/agents/${agent.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(updatedAgentData),
      }).then(res => res.ok ? res.json() : Promise.reject(new Error('Failed to update agent')));
    },
    ...mutationOptions,
  });

  const handleSubmit = () => {
    const finalPersona = persona === 'custom' ? customPersona : persona;
    const agentData = {
      name, persona: finalPersona, mode, objective,
      configuration: { target_repo_path: targetRepoPath, target_branch: targetBranch, default_model_id: defaultModelId },
    };
    if (agent) updateAgentMutation.mutate(agentData);
    else createAgentMutation.mutate(agentData);
  };

  const handleNext = () => setStep(prev => Math.min(prev + 1, 3));
  const handleBack = () => setStep(prev => Math.max(prev - 1, 1));

  const isSubmitting = createAgentMutation.isPending || updateAgentMutation.isPending;

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="grid gap-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Agent Name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., My Code Assistant" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="persona">Persona</Label>
              <Select value={persona} onValueChange={handlePersonaChange}>
                <SelectTrigger><SelectValue placeholder="Select a persona" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="software_engineer">Software Engineer</SelectItem>
                  <SelectItem value="data_analyst">Data Analyst</SelectItem>
                  <SelectItem value="code_reviewer">Code Reviewer</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
              {persona === 'custom' && (
                <Textarea value={customPersona} onChange={(e) => setCustomPersona(e.target.value)} placeholder="Describe the custom persona..." className="mt-2" />
              )}
            </div>
          </div>
        );
      case 2:
        return (
          <div className="grid gap-6 py-4">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                Mode
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild><HelpCircle className="h-4 w-4 text-muted-foreground" /></TooltipTrigger>
                    <TooltipContent>
                      <p className="max-w-xs">
                        <b>Chat:</b> For conversational interactions.<br/>
                        <b>Tool User:</b> Can use tools to achieve goals.<br/>
                        <b>Autonomous:</b> Can operate independently without human intervention.
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </Label>
              <Select value={mode} onValueChange={setMode}>
                <SelectTrigger><SelectValue placeholder="Select agent mode" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="chat">Chat</SelectItem>
                  <SelectItem value="tool_user">Tool User</SelectItem>
                  <SelectItem value="autonomous">Autonomous</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="objective">Objective</Label>
              <Textarea id="objective" value={objective} onChange={(e) => setObjective(e.target.value)} className="col-span-3 min-h-[150px]" />
            </div>
          </div>
        );
      case 3:
        return (
          <div className="grid gap-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="targetRepo">Target Repository</Label>
              <Select value={selectedRepoFullName || ''} onValueChange={handleRepoChange} disabled={isLoadingGithubRepos}>
                <SelectTrigger><SelectValue placeholder="Select a repository" /></SelectTrigger>
                <SelectContent>
                  {isLoadingGithubRepos ? (
                    <SelectItem value="loading" disabled><Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading repositories...</SelectItem>
                  ) : (
                    githubRepos?.map((repo) => (
                      <SelectItem key={repo.id} value={repo.full_name}>{repo.full_name}</SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="targetBranch">Target Branch</Label>
              <Select value={targetBranch} onValueChange={setTargetBranch} disabled={isLoadingRepoBranches || !selectedRepoFullName}>
                <SelectTrigger><SelectValue placeholder="Select a branch" /></SelectTrigger>
                <SelectContent>
                  {isLoadingRepoBranches ? (
                    <SelectItem value="loading" disabled><Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading branches...</SelectItem>
                  ) : (
                    repoBranches?.map((branch) => (
                      <SelectItem key={branch} value={branch}>{branch}</SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="defaultModelId">Default LLM</Label>
              <Select value={defaultModelId} onValueChange={setDefaultModelId} disabled={isLoadingLlmModels}>
                <SelectTrigger><SelectValue placeholder="Select default LLM model" /></SelectTrigger>
                <SelectContent>
                  {isLoadingLlmModels ? (
                    <SelectItem value="loading" disabled><Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading models...</SelectItem>
                  ) : (
                    llmModels?.map((model) => (
                      <SelectItem key={model.id} value={model.id}>{model.model_name} ({model.provider_id})</SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{agent ? 'Edit Arcana Agent' : 'Create New Arcana Agent'}</DialogTitle>
          <DialogDescription>
            Step {step} of 3: {step === 1 ? 'Basic Information' : step === 2 ? 'Behavior & Objective' : 'Configuration'}
          </DialogDescription>
        </DialogHeader>
        
        {renderStep()}

        <DialogFooter className="flex justify-between w-full pt-4">
          <div>
            {step > 1 && (
              <Button variant="outline" onClick={handleBack}>
                <ChevronLeft className="h-4 w-4 mr-2" /> Back
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancel</Button>
            {step < 3 ? (
              <Button onClick={handleNext}>
                Next <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                {agent ? 'Save Changes' : 'Create Agent'}
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateEditAgentDialog;
