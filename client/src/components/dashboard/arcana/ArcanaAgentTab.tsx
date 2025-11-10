import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { PlusCircle, Play, StopCircle, Trash2, TerminalSquare, BotMessageSquare, Code, ScrollText, GitBranch, Github, ThumbsUp, ThumbsDown } from 'lucide-react';
import { Separator } from '@/components/ui/separator';
import Editor from "@monaco-editor/react";
import FileTree, { TreeNode } from './FileTree';

// --- MOCK DATA AND INTERFACES ---

interface LogEntry {
  type: 'thought' | 'command' | 'output' | 'human_input_needed' | 'error';
  content: string;
  timestamp: string;
}

interface Agent {
  id: string;
  name: string;
  description: string;
  goal: string;
  status: 'idle' | 'planning' | 'coding' | 'testing' | 'deploying' | 'paused' | 'completed' | 'failed' | 'awaiting_human_input';
  lastActivity: string;
  currentStep: string;
  logs: LogEntry[];
  generatedCode: string;
  repo: string;
  branch: string;
}

const mockFileTree: TreeNode = {
  name: 'root',
  type: 'folder',
  children: [
    { name: 'package.json', type: 'file' },
    { name: 'README.md', type: 'file' },
    {
      name: 'src',
      type: 'folder',
      children: [
        { name: 'index.js', type: 'file' },
        { name: 'App.js', type: 'file' },
        { 
          name: 'components', 
          type: 'folder',
          children: [
            { name: 'Button.js', type: 'file' },
            { name: 'Card.js', type: 'file' },
          ]
        },
      ],
    },
  ],
};

const mockAgents: Agent[] = [
  {
    id: 'agent-1',
    name: 'Fullstack App Builder',
    description: 'Builds fullstack applications from high-level descriptions.',
    goal: 'Create a simple e-commerce platform',
    status: 'idle',
    lastActivity: '2025-11-08 10:00 AM',
    currentStep: 'Awaiting task...',
    logs: [],
    generatedCode: `// Select an agent and a task to see generated code`,
    repo: 'vareon/vareon-frontend',
    branch: 'main',
  },
  {
    id: 'agent-2',
    name: 'Bug Fixer Agent',
    description: 'Identifies and fixes bugs in existing codebases.',
    goal: 'Fix authentication bug in user service',
    status: 'awaiting_human_input',
    lastActivity: '2025-11-09 09:35 AM',
    currentStep: 'Waiting for approval to apply patch.',
    logs: [
        { type: 'thought', content: 'Starting analysis...', timestamp: '09:30:01' },
        { type: 'command', content: 'grep -r "authenticate" src/', timestamp: '09:30:05' },
        { type: 'output', content: 'src/auth/auth.py: def authenticate(user, pass): ...', timestamp: '09:30:06' },
        { type: 'thought', content: 'Identified potential issue in auth.py. The password check is too simple.', timestamp: '09:31:10' },
        { type: 'thought', content: 'Generating a patch to add hashing and salting.', timestamp: '09:32:00' },
        { type: 'human_input_needed', content: 'Generated a patch to fix the authentication vulnerability. Should I apply it to `src/auth/auth.py`?', timestamp: '09:35:00' },
    ],
    generatedCode: `import hashlib
import os

def authenticate(user, password):
-   # Insecure password check
-   if user.password == password:
-       return True
-   return False
+   # Secure password check with hashing and salting
+   salt = user.password_salt
+   hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
+   return user.password_hash == hashed_password
`,
    repo: 'vareon/vareon-backend',
    branch: 'bugfix/auth-vulnerability',
  },
];

const mockRepos = ['vareon/vareon-frontend', 'vareon/vareon-backend', 'vareon/infra-config'];
const mockBranches = ['main', 'develop', 'staging', 'bugfix/auth-vulnerability'];


export default function ArcanaAgentTab() {
  const [agents, setAgents] = useState<Agent[]>(mockAgents);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(mockAgents[1]);
  const [isGithubConnected, setIsGithubConnected] = useState(true); // Mocked as true

  const handleSelectAgent = (agent: Agent) => { setSelectedAgent(agent); };

  const handleHumanApproval = (approved: boolean) => {
    if (!selectedAgent) return;

    const newLogEntry: LogEntry = {
        type: approved ? 'thought' : 'error',
        content: approved ? 'User approved the change. Applying patch...' : 'User rejected the change. Halting execution.',
        timestamp: new Date().toLocaleTimeString(),
    };

    setAgents(prev => prev.map(agent => 
        agent.id === selectedAgent.id 
        ? { ...agent, status: approved ? 'coding' : 'idle', logs: [...agent.logs, newLogEntry] } 
        : agent
    ));
    setSelectedAgent(prev => prev ? { ...prev, status: approved ? 'coding' : 'idle', logs: [...prev.logs, newLogEntry] } : null);
  };

  return (
    <ResizablePanelGroup direction="horizontal" className="h-full w-full">
      {/* Left Panel: Agent Management */}
      <ResizablePanel defaultSize={25}>
        <Card className="h-full flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><TerminalSquare className="h-5 w-5" /> Autonomous Agents</CardTitle>
            <CardDescription>Define, manage, and monitor your AI agents.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col overflow-hidden">
            <Button className="w-full mb-4"><PlusCircle className="mr-2 h-4 w-4" /> Create Agent</Button>
            <Separator className="my-4" />
            <h3 className="text-lg font-semibold mb-4">Your Agents</h3>
            <ScrollArea className="flex-1 pr-4">
              <Table>
                <TableHeader><TableRow><TableHead>Name</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
                <TableBody>
                  {agents.map((agent) => (
                    <TableRow key={agent.id} onClick={() => handleSelectAgent(agent)} className={selectedAgent?.id === agent.id ? 'bg-accent/50 cursor-pointer' : 'cursor-pointer'}>
                      <TableCell className="font-medium">{agent.name}</TableCell>
                      <TableCell><Badge>{agent.status}</Badge></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          </CardContent>
        </Card>
      </ResizablePanel>
      <ResizableHandle withHandle />

      {/* Middle Panel: Context & Details */}
      <ResizablePanel defaultSize={35}>
        <div className="h-full flex flex-col gap-4 p-4">
          {selectedAgent ? (
            <>
              {isGithubConnected ? (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2"><Github className="h-5 w-5" /> Project Context</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <Label>Repository</Label>
                        <Select defaultValue={selectedAgent.repo}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>{mockRepos.map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Branch</Label>
                        <Select defaultValue={selectedAgent.branch}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>{mockBranches.map(b => <SelectItem key={b} value={b}><GitBranch className="inline-block h-4 w-4 mr-2" />{b}</SelectItem>)}</SelectContent>
                        </Select>
                      </div>
                    </div>
                    <Label>File Explorer</Label>
                    <ScrollArea className="h-48 border rounded-md p-2">
                      <FileTree root={mockFileTree} onSelect={(path) => console.log(path)} />
                    </ScrollArea>
                  </CardContent>
                </Card>
              ) : (
                <Card className="flex items-center justify-center p-6">
                  <Button><Github className="mr-2 h-4 w-4" /> Connect to GitHub</Button>
                </Card>
              )}
              <Card className="flex-1">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><BotMessageSquare className="h-5 w-5" /> Agent Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <h3 className="font-semibold">{selectedAgent.name}</h3>
                  <p className="text-sm text-muted-foreground">{selectedAgent.description}</p>
                  <Separator className="my-4" />
                  <div className="space-y-2 text-sm">
                    <p><strong>Goal:</strong> {selectedAgent.goal}</p>
                    <p><strong>Status:</strong> <Badge>{selectedAgent.status}</Badge></p>
                    <p><strong>Current Step:</strong> {selectedAgent.currentStep}</p>
                  </div>
                  <Separator className="my-4" />
                  <Label htmlFor="newTaskGoal">Submit New Task</Label>
                  <Textarea id="newTaskGoal" placeholder="e.g., Refactor the Button component to use Tailwind CSS." className="my-2" />
                  <Button className="w-full"><Play className="mr-2 h-4 w-4" /> Run Agent</Button>
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="h-full flex items-center justify-center"><p className="text-muted-foreground">Select an agent to begin.</p></Card>
          )}
        </div>
      </ResizablePanel>
      <ResizableHandle withHandle />

      {/* Right Panel: Logs & Code */}
      <ResizablePanel defaultSize={40}>
        <div className="h-full flex flex-col gap-4 p-4">
          <Card className="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ScrollText className="h-5 w-5" /> Agent Log & Thoughts</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full p-2 border rounded-md bg-black font-mono text-sm">
                {selectedAgent?.logs.map((log, index) => (
                  <div key={index} className="mb-2">
                    <span className="text-gray-500 mr-2">[{log.timestamp}]</span>
                    <span className={
                      log.type === 'thought' ? 'text-blue-400' :
                      log.type === 'command' ? 'text-yellow-400' :
                      log.type === 'output' ? 'text-green-400' :
                      log.type === 'error' ? 'text-red-500' : 'text-white'
                    }>
                      {log.type === 'command' && '$ '}
                      {log.content}
                    </span>
                    {log.type === 'human_input_needed' && (
                      <div className="flex gap-2 mt-2">
                        <Button size="sm" variant="outline" className="bg-green-500 hover:bg-green-600" onClick={() => handleHumanApproval(true)}><ThumbsUp className="h-4 w-4 mr-2" /> Approve</Button>
                        <Button size="sm" variant="outline" className="bg-red-500 hover:bg-red-600" onClick={() => handleHumanApproval(false)}><ThumbsDown className="h-4 w-4 mr-2" /> Deny</Button>
                      </div>
                    )}
                  </div>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>
          <Card className="flex-1 flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Code className="h-5 w-5" /> Generated Code</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden p-0">
              <Editor
                height="100%"
                language="python"
                theme="vs-dark"
                value={selectedAgent?.generatedCode}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  scrollBeyondLastLine: false,
                }}
              />
            </CardContent>
          </Card>
        </div>
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}