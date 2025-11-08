export interface Agent {
  id: string;
  name: string;
  type: string;
  status: string;
  health: number;
  lastRun: string;
}

export interface Device {
  id: string;
  name: string;
  type: string;
  status: string;
  port: string;
  lastSeen: string;
}
