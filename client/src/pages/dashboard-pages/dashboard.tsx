import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge } from '@/components/ui';
import { StatusIndicator } from '@/components/dashboard/status-indicator';
import { ArrowRight, Activity, Bot, Search, Network, Terminal, TrendingUp } from 'lucide-react';
import { useLocation } from 'wouter';
import { useToast } from '@/hooks/dashboard/use-toast';

import { SystemStatus } from '@/types';

export default function Dashboard() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();

  const openNeosyntisLabMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/neosyntis/open-lab', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to open Neosyntis Lab');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Neosyntis Lab Opened',
        description: 'The Neosyntis Lab has been successfully opened.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: `Failed to open Neosyntis Lab: ${error.message}`,
        variant: 'destructive',
      });
    },
  });

  const startArcanaChatMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/arcana/start-chat', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to start Arcana Chat');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Arcana Chat Started',
        description: 'A new Arcana chat session has been initiated.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: `Failed to start Arcana Chat: ${error.message}`,
        variant: 'destructive',
      });
    },
  });

  const deployMyntrixModelMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/myntrix/deploy-model', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to deploy Myntrix Model');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Myntrix Model Deployed',
        description: 'The Myntrix model has been successfully deployed.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: `Failed to deploy Myntrix Model: ${error.message}`,
        variant: 'destructive',
      });
    },
  });

  const manageMyntrixAgentsMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch('/api/myntrix/manage-agents', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to manage Myntrix Agents');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: 'Myntrix Agents Managed',
        description: 'Myntrix agents management initiated.',
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: `Failed to manage Myntrix Agents: ${error.message}`,
        variant: 'destructive',
      });
    },
  });

  const queryClient = useQueryClient();



  const { data: systemStatus, isLoading, error } = useQuery<SystemStatus>({
    queryKey: ['/api/system/status'],
    queryFn: async () => {
      const response = await fetch('/api/system/status');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
  });









  const quickActions = [
    {
      label: 'Open Neosyntis Lab',
      icon: Search,
      action: () => openNeosyntisLabMutation.mutate(),
      loading: openNeosyntisLabMutation.isPending,
    },
    {
      label: 'Start Arcana Chat',
      icon: Terminal,
      action: () => startArcanaChatMutation.mutate(),
      loading: startArcanaChatMutation.isPending,
    },
    {
      label: 'Deploy Myntrix Model',
      icon: Bot,
      action: () => deployMyntrixModelMutation.mutate(),
      loading: deployMyntrixModelMutation.isPending,
    },
    {
      label: 'Manage Myntrix Agents',
      icon: Activity,
      action: () => manageMyntrixAgentsMutation.mutate(),
      loading: manageMyntrixAgentsMutation.isPending,
    },
  ];

  const overallLoading = isLoading ||
                         openNeosyntisLabMutation.isPending || startArcanaChatMutation.isPending ||
                         deployMyntrixModelMutation.isPending || manageMyntrixAgentsMutation.isPending;
  const overallError = error ||
                       openNeosyntisLabMutation.isError || startArcanaChatMutation.isError ||
                       deployMyntrixModelMutation.isError || manageMyntrixAgentsMutation.isError;

  if (overallLoading) {
    return <div className="p-6 text-center">Loading dashboard data...</div>;
  }

  if (overallError) {
    return <div className="p-6 text-center text-red-500">Error loading dashboard data: {overallError instanceof Error ? overallError.message : 'An unknown error occurred'}</div>;
  }

  // Ensure all data is available before proceeding
  if (!systemStatus) {
    return <div className="p-6 text-center text-red-500">Missing system status data.</div>;
  }

  const modules = [
    {
      id: 'arcana',
      name: 'ARCANA',
      icon: Terminal,
      description: 'Cognitive Chat & Shell System',
      status: systemStatus.arcana.status,
      metrics: [
        { label: 'Active Chats', value: systemStatus.arcana.activeChats },
        { label: 'Messages', value: systemStatus.arcana.messagesProcessed },
        { label: 'Avg Response', value: systemStatus.arcana.avgResponseTime },
      ],
      path: '/dashboard/arcana',
    },
    {
      id: 'myntrix',
      name: 'MYNTRIX',
      icon: Bot,
      description: 'AI Core & Device Control',
      status: systemStatus.myntrix.status,
      metrics: [
        { label: 'Active Agents', value: systemStatus.myntrix.activeAgents },
        { label: 'Jobs Completed', value: systemStatus.myntrix.jobsCompleted },
        { label: 'Devices', value: systemStatus.myntrix.devicesConnected },
      ],
      path: '/dashboard/myntrix',
    },
    {
      id: 'neosyntis',
      name: 'NEOSYNTIS',
      icon: Search,
      description: 'Research & Workflow Lab',
      status: systemStatus.neosyntis.status,
      metrics: [
        { label: 'Active Workflows', value: systemStatus.neosyntis.activeWorkflows },
        { label: 'Datasets', value: systemStatus.neosyntis.datasetsManaged },
        { label: 'Search Queries', value: systemStatus.neosyntis.searchQueriesProcessed },
      ],
      path: '/dashboard/neosyntis',
    },
    {
      id: 'cognisys',
      name: 'COGNISYS',
      icon: Network,
      description: 'Multimodel Orchestration',
      status: systemStatus.cognisys.status,
      metrics: [
        { label: 'Active Models', value: systemStatus.cognisys.modelsActive },
        { label: 'Routing Rules', value: systemStatus.cognisys.routingRules },
        { label: 'Requests Routed', value: systemStatus.cognisys.requestsRouted },
      ],
      path: '/dashboard/cognisys',
    },
  ];

  // The All Systems Operational badge status can still refer to systemStatus for overall health
  const overallSystemStatus = systemStatus.arcana.status === 'online' &&
                              systemStatus.myntrix.status === 'online' &&
                              systemStatus.neosyntis.status === 'online' &&
                              systemStatus.cognisys.status === 'online' ? 'online' : 'offline';

  const overallUptime = systemStatus.arcana.uptime; // Just pick one or calculate an aggregate if needed

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">VAREON Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Central hub for your cognitive AI ecosystem
          </p>
        </div>
        <Badge variant="outline" className="gap-2">
          <StatusIndicator status="online" size="sm" />
          All Systems Operational
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {modules.map((module) => (
          <Card
            key={module.id}
            className="hover-elevate cursor-pointer transition-all"
            onClick={() => setLocation(module.path)}
            data-testid={`card-module-${module.id}`}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <module.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{module.name}</CardTitle>
                    <StatusIndicator
                      status={module.status}
                      showLabel
                      size="sm"
                      label={module.status}
                    />
                  </div>
                </div>
              </div>
              <CardDescription className="text-xs mt-2">
                {module.description}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {module.metrics.map((metric, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{metric.label}</span>
                  <span className="font-medium font-mono">{metric.value}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Quick Actions
            </CardTitle>
            <CardDescription>
              Frequently used operations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {quickActions.map((action, idx) => (
              <Button
                key={idx}
                variant="ghost"
                className="w-full justify-between group"
                onClick={action.action}
                disabled={action.loading}
                data-testid={`button-quick-${action.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <span className="flex items-center gap-2">
                  {action.loading ? <Activity className="h-4 w-4 animate-spin" /> : <action.icon className="h-4 w-4" />}
                  {action.label}
                </span>
                <ArrowRight className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </Button>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-primary" />
              System Health
            </CardTitle>
            <CardDescription>
              Overall system performance
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {Object.entries(systemStatus).map(([key, value]: [string, { status: string; uptime: string }]) => (
              <div key={key} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StatusIndicator status={value.status as any} size="sm" />
                  <span className="text-sm font-medium capitalize">{key}</span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {value.uptime} uptime
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle>Welcome to VAREON Ecosystem</CardTitle>
          <CardDescription>
            An enterprise-grade cognitive AI platform integrating research, orchestration, and deployment
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>
            <strong className="text-foreground">NEOSYNTIS</strong> - Advanced research laboratory with workflow automation, dataset management, and intelligent search capabilities.
          </p>
          <p>
            <strong className="text-foreground">MYNTRIX</strong> - Core AI engine managing agents, hardware integration, and task orchestration with 3D visualization.
          </p>
          <p>
            <strong className="text-foreground">COGNISYS</strong> - Multimodel routing system with intelligent intent detection and reasoning capabilities.
          </p>
          <p>
            <strong className="text-foreground">ARCANA</strong> - Conversational AI interface with embedded terminal and context-aware memory management.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
