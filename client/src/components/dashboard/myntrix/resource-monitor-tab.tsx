import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, Cpu, HardDrive, Activity } from 'lucide-react';
import { mockTelemetryData, mockJobs } from '@/lib/dashboard/mockApi';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function ResourceMonitorTab() {
  const { data: telemetry } = useQuery({
    queryKey: ['/api/telemetry'],
    initialData: mockTelemetryData,
  });

  const { data: jobs } = useQuery({
    queryKey: ['/api/jobs'],
    initialData: mockJobs,
  });

  const cpuData = telemetry.systemMetrics.cpu.map((value, idx) => ({ time: idx, value }));
  const memoryData = telemetry.systemMetrics.memory.map((value, idx) => ({ time: idx, value }));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-primary" />
            Resource Monitor
          </CardTitle>
          <CardDescription>
            System resources and job activity monitoring
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-muted-foreground">CPU Usage</CardTitle>
              <Cpu className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {cpuData[cpuData.length - 1].value}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Avg: {Math.round(cpuData.reduce((a, b) => a + b.value, 0) / cpuData.length)}%
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-muted-foreground">Memory Usage</CardTitle>
              <HardDrive className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {memoryData[memoryData.length - 1].value}%
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              12.8 GB / 16 GB
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm text-muted-foreground">Active Jobs</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {jobs?.filter(j => j.status === 'running').length}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {jobs?.filter(j => j.status === 'pending').length} pending
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">CPU Usage</CardTitle>
            <CardDescription>Real-time CPU utilization</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={cpuData}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--chart-1))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--chart-1))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="hsl(var(--chart-1))"
                  fillOpacity={1}
                  fill="url(#colorCpu)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Memory Usage</CardTitle>
            <CardDescription>RAM utilization over time</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={memoryData}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="time" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '6px',
                  }}
                />
                <Line type="monotone" dataKey="value" stroke="hsl(var(--chart-2))" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Job Activity</CardTitle>
          <CardDescription>
            Current running and pending jobs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {jobs?.map((job) => (
            <div key={job.id} className="flex items-center gap-4 p-4 border rounded-lg">
              <div className="flex-1">
                <div className="font-medium text-sm">{job.name}</div>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant={
                    job.status === 'running' ? 'default' :
                    job.status === 'completed' ? 'secondary' :
                    'outline'
                  } className="text-xs">
                    {job.status}
                  </Badge>
                  <span className="text-xs text-muted-foreground">{job.type}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-mono font-medium">{job.progress}%</div>
                <div className="text-xs text-muted-foreground">
                  {new Date(job.createdAt).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
