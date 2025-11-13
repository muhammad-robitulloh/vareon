export interface SystemStatusModule {
  status: 'online' | 'offline' | 'degraded' | 'idle' | 'running' | 'stopped' | 'connected' | 'disconnected' | 'pending' | 'completed' | 'error'; // Updated type
  uptime: string;
  activeChats?: number;
  messagesProcessed?: number;
  avgResponseTime?: string;
  activeAgents?: number;
  jobsCompleted?: number;
  devicesConnected?: number;
  activeWorkflows?: number;
  datasetsManaged?: number;
  searchQueriesProcessed?: number;
  modelsActive?: number;
  routingRules?: number;
  requestsRouted?: number;
  cpu_percent?: number;
  memory_percent?: number;
  memory_total?: number;
  memory_available?: number;
  system_metrics_mocked?: boolean;
  system_metrics_reason?: string;
}

export interface SystemStatus {
  arcana: SystemStatusModule;
  myntrix: SystemStatusModule;
  neosyntis: SystemStatusModule;
  cognisys: SystemStatusModule;
  mocked?: boolean;
  reason?: string;
}

export interface ArcanaAgent {
  id: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
  name: string;
  persona: string;
  mode: string;
  objective: string | null;
  status: string;
  configuration: Record<string, any> | null;
  target_repo_path: string | null;
  target_branch: string | null;
}
