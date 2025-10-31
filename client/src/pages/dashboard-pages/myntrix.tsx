import { useState, useEffect } from 'react';
import { useSearch, useLocation } from 'wouter';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Bot, Calendar, Cpu, BarChart3 } from 'lucide-react';
import AgentManagerTab from '@/components/dashboard/myntrix/agent-manager-tab';
import TaskSchedulerTab from '@/components/dashboard/myntrix/task-scheduler-tab';
import DeviceControlTab from '@/components/dashboard/myntrix/device-control-tab';
import ResourceMonitorTab from '@/components/dashboard/myntrix/resource-monitor-tab';

const tabs = [
  { value: 'agents', label: 'Agent Manager', icon: Bot },
  { value: 'scheduler', label: 'Task Scheduler', icon: Calendar },
  { value: 'devices', label: 'Device Control', icon: Cpu },
  { value: 'monitor', label: 'Resource Monitor', icon: BarChart3 },
];

export default function Myntrix() {
  const search = useSearch();
  const [, setLocation] = useLocation();
  const params = new URLSearchParams(search);
  const tabFromUrl = params.get('tab') || 'agents';
  const [activeTab, setActiveTab] = useState(tabFromUrl);

  useEffect(() => {
    setActiveTab(tabFromUrl);
  }, [tabFromUrl]);

  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    setLocation(`/dashboard/myntrix?tab=${newTab}`);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">MYNTRIX Core</h1>
            <p className="text-sm text-muted-foreground mt-1">
              AI Core & Hardware Integration Platform
            </p>
          </div>
          <Badge variant="outline">v1.8.2</Badge>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="h-full flex flex-col">
          <div className="border-b bg-card/50 px-6">
            <TabsList className="bg-transparent h-12 w-full justify-start gap-1">
              {tabs.map((tab) => (
                <TabsTrigger
                  key={tab.value}
                  value={tab.value}
                  className="gap-2 data-[state=active]:bg-background"
                  data-testid={`tab-${tab.value}`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          <div className="flex-1 overflow-auto">
            <TabsContent value="agents" className="h-full m-0 p-6">
              <AgentManagerTab />
            </TabsContent>
            <TabsContent value="scheduler" className="h-full m-0 p-6">
              <TaskSchedulerTab />
            </TabsContent>
            <TabsContent value="devices" className="h-full m-0 p-6">
              <DeviceControlTab />
            </TabsContent>
            <TabsContent value="monitor" className="h-full m-0 p-6">
              <ResourceMonitorTab />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}
