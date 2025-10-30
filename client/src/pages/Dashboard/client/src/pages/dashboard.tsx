import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StatusIndicator } from '@/pages/Dashboard/client/src/components/status-indicator';
import { ArrowRight, Activity, Bot, Search, Network, Terminal, TrendingUp } from 'lucide-react';
import { useLocation } from 'wouter';
import { mockSystemStatus } from '@/pages/Dashboard/client/src/lib/mockApi';

export default function Dashboard() {
  const [, setLocation] = useLocation();

  const { data: systemStatus } = useQuery({
    queryKey: ['/api/system/status'],
    initialData: mockSystemStatus,
  });

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
      path: '/arcana',
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
      path: '/myntrix',
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
      path: '/neosyntis',
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
      path: '/cognisys',
    },
  ];

  const quickActions = [
    { label: 'Open Neosyntis Lab', path: '/neosyntis', icon: Search },
    { label: 'Start Arcana Chat', path: '/arcana', icon: Terminal },
    { label: 'Deploy Model', path: '/neosyntis?tab=deployment', icon: Activity },
    { label: 'Manage Agents', path: '/myntrix?tab=agents', icon: Bot },
  ];

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
                onClick={() => setLocation(action.path)}
                data-testid={`button-quick-${action.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <span className="flex items-center gap-2">
                  <action.icon className="h-4 w-4" />
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
            {Object.entries(systemStatus).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <StatusIndicator status={value.status} size="sm" />
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
