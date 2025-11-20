import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { TerminalSquare, PlusCircle, BotMessageSquare, Play, ScrollText, Loader2, Edit } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PanelGroup, Panel, PanelResizeHandle } from 'react-resizable-panels';
import { useAuth } from '@/hooks/use-auth';
import { ArcanaAgent } from '@/types/system';
import FileTree from './FileTree';
import GitOperationsPanel from './GitOperationsPanel';
import CreateEditAgentDialog from './CreateEditAgentDialog'; // Import the new dialog component
import FileEditor from './FileEditor'; // Import the new FileEditor component
import ChatInterfaceTab from './chat-interface-tab'; // Import the chat tab
import AgentChatInterfaceTab from './AgentChatInterfaceTab';

// Define types for job logs and job status received via WebSocket
interface AgentLog {
  job_id: string;
  log_id: string;
  timestamp: string;
  log_type: string;
  content: string;
}

interface AgentStatusUpdate {
  job_id: string;
  status: string;
  updated_at: string;
  final_output: string | null;
}

const ArcanaAgentTab: React.FC = () => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [selectedAgent, setSelectedAgent] = useState<ArcanaAgent | null>(null);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [newTaskGoal, setNewTaskGoal] = useState("");
  const [selectedFile, setSelectedFile] = useState<string | null>(null); // New state for selected file
  const [selectedRepoPath, setSelectedRepoPath] = useState<string>(''); // New state for selected repo path
  const [selectedBranch, setSelectedBranch] = useState<string>('');

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [agentToEdit, setAgentToEdit] = useState<ArcanaAgent | null>(null);
  const [humanInput, setHumanInput] = useState(''); // New state for human input

  // State for live logs and status from WebSocket
  const [liveJobLogs, setLiveJobLogs] = useState<AgentLog[]>([]);
  const [liveJobStatus, setLiveJobStatus] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const { data: agents, isLoading: isLoadingAgents } = useQuery<ArcanaAgent[]>({
    queryKey: ['arcanaAgents'],
    queryFn: async () => {
      const response = await fetch('/api/arcana/agents/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch agents');
      return response.json();
    },
    enabled: !!token,
  });

  const { data: jobs, isLoading: isLoadingJobs } = useQuery<any[]>({
    queryKey: ['arcanaJobs', selectedAgent?.id],
    queryFn: async () => {
      if (!selectedAgent) return [];
      const response = await fetch(`/api/arcana/agents/${selectedAgent.id}/jobs/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch jobs');
      return response.json();
    },
    enabled: !!selectedAgent && !!token,
  });

  // Initial fetch for job logs (will be updated by WebSocket)
  const { data: initialJobLogs, isLoading: isLoadingInitialLogs } = useQuery<AgentLog[]>({
    queryKey: ['arcanaJobLogs', selectedJobId],
    queryFn: async () => {
      if (!selectedJobId) return [];
      const response = await fetch(`/api/arcana/jobs/${selectedJobId}/logs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch logs');
      return response.json();
    },
    enabled: !!selectedJobId && !!token,
  });

  // Initial fetch for selected job details (will be updated by WebSocket)
  const { data: initialSelectedJob, isLoading: isLoadingInitialSelectedJob } = useQuery<any>({
    queryKey: ['arcanaJob', selectedJobId],
    queryFn: async () => {
      if (!selectedJobId) return null;
      const response = await fetch(`/api/arcana/jobs/${selectedJobId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch job details');
      return response.json();
    },
    enabled: !!selectedJobId && !!token,
    // refetchInterval removed, relying on WebSocket for updates
  });

  // Effect to manage WebSocket connection
  useEffect(() => {
    if (selectedJobId && token) {
      // Close existing WebSocket connection if any
      if (wsRef.current) {
        wsRef.current.close();
      }

      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = window.location.host;
      const wsUrl = `${wsProtocol}//${wsHost}/ws-api/ws/arcana/${selectedJobId}?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log(`WebSocket connected for job ${selectedJobId}`);
        // Reset live logs and status when a new job is selected
        setLiveJobLogs(initialJobLogs || []);
        setLiveJobStatus(initialSelectedJob?.status || null);
      };

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'agent_log') {
          setLiveJobLogs((prevLogs) => [...prevLogs, message.payload]);
        } else if (message.type === 'agent_status_update') {
          setLiveJobStatus(message.payload.status);
          // Invalidate the job query to update other job details if necessary
          queryClient.invalidateQueries({ queryKey: ['arcanaJob', selectedJobId] });
          queryClient.invalidateQueries({ queryKey: ['arcanaJobs', selectedAgent?.id] });
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log(`WebSocket disconnected for job ${selectedJobId}`);
      };

      wsRef.current = ws;

      return () => {
        ws.close();
      };
    } else {
      // Clear logs and status if no job is selected
      setLiveJobLogs([]);
      setLiveJobStatus(null);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    }
  }, [selectedJobId, token, initialJobLogs, initialSelectedJob, queryClient, selectedAgent]);

  // Auto-scroll logs to bottom
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [liveJobLogs]);

  const executeMutation = useMutation({
    mutationFn: (taskGoal: string) => {
      if (!selectedAgent) throw new Error("No agent selected");
      return fetch(`/api/arcana/agents/${selectedAgent.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ task_prompt: taskGoal }),
      }).then(res => res.json());
    },
    onSuccess: (data: any) => {
      queryClient.invalidateQueries({ queryKey: ['arcanaJobs', selectedAgent?.id] });
      setSelectedJobId(data.id);
      setNewTaskGoal("");
    },
  });

  const submitHumanInputMutation = useMutation({
    mutationFn: async (input: string) => {
      if (!selectedJobId) throw new Error("No job selected");
      // The backend now includes context in the message_to_user, so we just send human_input
      const response = await fetch(`/api/arcana/jobs/${selectedJobId}/submit_human_input`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ human_input: input }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit human input');
      }
      return response.json();
    },
    onSuccess: () => {
      setHumanInput('');
      // WebSocket will update job status and logs, no need to invalidate here
    },
    onError: (err: Error) => {
      // Display error to user
    },
  });

  const handleRunAgent = () => {
    if (newTaskGoal) {
      executeMutation.mutate(newTaskGoal);
    }
  };

  const handleEditAgent = () => {
    if (selectedAgent) {
      setAgentToEdit(selectedAgent);
      setIsEditDialogOpen(true);
    }
  };

  const handleHumanInputSubmit = () => {
    if (humanInput.trim() && selectedJobId) {
      submitHumanInputMutation.mutate(humanInput);
    }
  };

  // Determine current job status for display
  const currentJobStatus = liveJobStatus || initialSelectedJob?.status || 'unknown';
  const displayedJobLogs = liveJobLogs.length > 0 ? liveJobLogs : (initialJobLogs || []);


  return (
    <>
      <PanelGroup direction="horizontal" className="h-full w-full">
        {/* Agents List Panel */}
        <Panel defaultSize={25}>
          <Card className="h-full flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TerminalSquare className="h-5 w-5" /> Autonomous Agents</CardTitle>
              <CardDescription>Define, manage, and monitor your AI agents.</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col overflow-hidden">
              <Button className="w-full mb-4" onClick={() => setIsCreateDialogOpen(true)}><PlusCircle className="mr-2 h-4 w-4" /> Create Agent</Button>
              <Separator className="my-4" />
              <h3 className="text-lg font-semibold mb-2">Available Agents</h3>
              <ScrollArea className="flex-1 pr-4">
                {isLoadingAgents ? <p>Loading agents...</p> : (
                  <Table>
                    <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
                    <TableBody>
                      {agents?.map((agent: ArcanaAgent) => (
                        <TableRow key={agent.id} onClick={() => setSelectedAgent(agent)} className={selectedAgent?.id === agent.id ? 'bg-accent/50 cursor-pointer' : 'cursor-pointer'}>
                          <TableCell className="font-medium">{agent.name}</TableCell>
                          <TableCell><Badge>{agent.status}</Badge></TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </Panel>
        <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300" />

        {/* Agent Details & Tasks Panel */}
        <Panel defaultSize={75}>
          {selectedAgent ? (
            selectedAgent.mode === 'chat' ? (
              <AgentChatInterfaceTab agent={selectedAgent} />
            ) : (
              <PanelGroup direction="horizontal">
                <Panel defaultSize={50}>
                  <div className="h-full p-4">
                    <div className="flex flex-col h-full gap-4">
                      <Card className="flex-1">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2"><BotMessageSquare className="h-5 w-5" /> Agent Details & Tasks</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <p><strong>ID:</strong> <span className="font-mono text-xs">{selectedAgent.id}</span></p>
                          <p><strong>Name:</strong> {selectedAgent.name}</p>
                          <p><strong>Persona:</strong> {selectedAgent.persona}</p>
                          <Separator className="my-4" />
                          <div className="space-y-2">
                            <p><strong>Status:</strong> <Badge>{selectedAgent.status}</Badge></p>
                            <p><strong>Mode:</strong> <Badge>{selectedAgent.mode}</Badge></p>
                            <p><strong>Objective:</strong> {selectedAgent.objective}</p>
                          </div>
                          <Separator className="my-4" />
                          <Label htmlFor="newTaskGoal">Submit New Task</Label>
                          <Textarea id="newTaskGoal" placeholder="e.g., Refactor the Button component to use Tailwind CSS." className="my-2" value={newTaskGoal} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewTaskGoal(e.target.value)} />
                          <div className="flex gap-2">
                            <Button className="flex-1" onClick={handleRunAgent} disabled={executeMutation.isPending}>
                              {executeMutation.isPending ? "Starting..." : <><Play className="mr-2 h-4 w-4" /> Run Agent</>}
                            </Button>
                            <Button variant="outline" onClick={handleEditAgent}>
                              <Edit className="mr-2 h-4 w-4" /> Edit Agent
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader><CardTitle>Jobs</CardTitle></CardHeader>
                        <CardContent>
                          <ScrollArea className="h-48">
                            {isLoadingJobs ? <p>Loading jobs...</p> : (
                              <Table>
                                <TableHeader><TableRow><TableHead>Job ID</TableHead><TableHead>Goal</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
                                <TableBody>
                                  {jobs?.map(job => (
                                    <TableRow key={job.id} onClick={() => setSelectedJobId(job.id)} className={selectedJobId === job.id ? 'bg-accent/50 cursor-pointer' : 'cursor-pointer'}>
                                      <TableCell className="font-mono text-xs">{job.id.substring(0, 8)}...</TableCell>
                                      <TableCell>{job.goal.substring(0, 30)}...</TableCell>
                                      <TableCell><Badge>{job.status}</Badge></TableCell>
                                    </TableRow>
                                  ))}
                                </TableBody>
                              </Table>
                            )}
                          </ScrollArea>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </Panel>
                <PanelResizeHandle className="w-2 bg-gray-200 hover:bg-gray-300" />
                <Panel defaultSize={50}>
                  {selectedFile && selectedRepoPath ? (
                    <FileEditor filePath={selectedFile} localPath={selectedRepoPath} onClose={() => setSelectedFile(null)} />
                  ) : selectedJobId ? (
                    <div className="flex flex-col h-full p-4 gap-4">
                      <Card className="flex-1 flex flex-col">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2"><ScrollText className="h-5 w-5" /> Agent Log & Thoughts</CardTitle>
                          {currentJobStatus && <CardDescription>Status: <Badge>{currentJobStatus}</Badge></CardDescription>}
                        </CardHeader>
                        <CardContent className="flex-1 overflow-hidden">
                          <ScrollArea className="h-full p-2 border rounded-md bg-black font-mono text-sm" ref={scrollAreaRef}>
                            {(isLoadingInitialLogs && displayedJobLogs.length === 0) ? <p className="text-white">Loading logs...</p> : displayedJobLogs.map((log, index) => (
                              <div key={log.log_id || index} className="whitespace-pre-wrap text-white">
                                <span className="text-green-400">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                                <span className={`ml-2 font-bold ${
                                  log.log_type === 'thought' ? 'text-purple-400' :
                                  log.log_type === 'action' ? 'text-blue-400' :
                                  log.log_type === 'error' ? 'text-red-500' :
                                  'text-gray-300'
                                }`}>
                                  [{log.log_type.toUpperCase()}]
                                </span>
                                <span className="ml-2">{log.content}</span>
                              </div>
                            ))}
                          </ScrollArea>
                        </CardContent>
                      </Card>
                      {currentJobStatus === 'awaiting_human_input' && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-lg">Agent Awaiting Input</CardTitle>
                            <CardDescription>The agent needs your clarification or approval to proceed.</CardDescription>
                          </CardHeader>
                          <CardContent className="space-y-2">
                            {displayedJobLogs.length > 0 && displayedJobLogs[displayedJobLogs.length - 1].log_type === 'human_input_needed' && (
                              <p className="text-sm text-muted-foreground whitespace-pre-wrap">{displayedJobLogs[displayedJobLogs.length - 1].content}</p>
                            )}
                            <Textarea
                              placeholder="Type your input or clarification here..."
                              value={humanInput}
                              onChange={(e) => setHumanInput(e.target.value)}
                              rows={3}
                              disabled={submitHumanInputMutation.isPending}
                            />
                            <Button
                              className="w-full"
                              onClick={handleHumanInputSubmit}
                              disabled={submitHumanInputMutation.isPending || !humanInput.trim()}
                            >
                              {submitHumanInputMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                              Submit Input & Resume
                            </Button>
                          </CardContent>
                        </Card>
                      )}
                      <PanelGroup direction="vertical">
                        <Panel>
                          <div className="h-full">
                            <FileTree onFileSelect={setSelectedFile} selectedFile={selectedFile} selectedRepoPath={selectedRepoPath} setSelectedRepoPath={setSelectedRepoPath} selectedBranch={selectedBranch} setSelectedBranch={setSelectedBranch} />
                            <GitOperationsPanel localPath={selectedRepoPath} currentBranch={selectedBranch} onBranchChange={setSelectedBranch} />
                          </div>
                        </Panel>
                      </PanelGroup>
                    </div>
                  ) : (
                    <div className="flex flex-col h-full p-4 gap-4">
                      <Card className="flex-1 flex flex-col">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2"><ScrollText className="h-5 w-5" /> Agent Log & Thoughts</CardTitle>
                        </CardHeader>
                        <CardContent className="flex-1 flex items-center justify-center"><p className="text-muted-foreground">Select a job to view logs.</p></CardContent>
                    </Card>
                    <PanelGroup direction="vertical">
                      <Panel>
                        <div className="h-full">
                          <FileTree onFileSelect={setSelectedFile} selectedFile={selectedFile} selectedRepoPath={selectedRepoPath} setSelectedRepoPath={setSelectedRepoPath} selectedBranch={selectedBranch} setSelectedBranch={setSelectedBranch} />
                          <GitOperationsPanel localPath={selectedRepoPath} currentBranch={selectedBranch} onBranchChange={setSelectedBranch} />
                        </div>
                      </Panel>
                    </PanelGroup>
                  </div>
                  )}
                </Panel>
              </PanelGroup>
            )
          ) : (
            <Card className="h-full flex items-center justify-center"><p className="text-muted-foreground">Select an agent to begin.</p></Card>
          )}
        </Panel>
      </PanelGroup>
      <CreateEditAgentDialog
        isOpen={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        agent={null}
      />
      <CreateEditAgentDialog
        isOpen={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        agent={agentToEdit}
      />
    </>
  );
};

export default ArcanaAgentTab;