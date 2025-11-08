export interface SystemStatus {
  [key: string]: {
    status: string;
    uptime: string;
  };
}
