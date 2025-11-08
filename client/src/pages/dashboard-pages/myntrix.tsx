import { useState, useEffect } from 'react';
import { useSearch, useLocation } from 'wouter';
import { Tabs, TabsContent, TabsList, TabsTrigger, Badge } from '@/components/ui';
import { Bot, Calendar, Cpu, BarChart3 } from 'lucide-react';
import {
  AgentManagerTab,
  TaskSchedulerTab,
  DeviceControlTab,
  ResourceMonitorTab,
  ThreeDVisualizationTab,
} from '@/components/dashboard/myntrix';

const tabs = [
  { value: 'agents', label: 'Agent Manager', icon: Bot },
  { value: 'scheduler', label: 'Task Scheduler', icon: Calendar },
  { value: 'devices', label: 'Device Control', icon: Cpu },
  { value: 'monitor', label: 'Resource Monitor', icon: BarChart3 },
  { value: '3d-viz', label: '3D Visualization', icon: BarChart3 }, // Reusing BarChart3 for now
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
            <TabsContent value="3d-viz" className="h-full m-0 p-6">
              <ThreeDVisualizationTab />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}
