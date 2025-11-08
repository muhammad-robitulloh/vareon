import { useState, useEffect } from 'react';
import { useSearch, useLocation } from 'wouter';
import { Tabs, TabsContent, TabsList, TabsTrigger, Badge } from '@/components/ui';
import { Search, Database, Workflow, BarChart3, Settings, Network, Box, Upload, Brain } from 'lucide-react';
import {
  SearchEngineTab,
  DatasetTab,
  WorkflowBuilderTab,
  TelemetryTab,
  DeviceSettingsTab,
  CognisysConfigTab,
  EcosystemBuilderTab,
  ModelDeploymentTab,
  MachineLearningTab,
} from '@/components/dashboard/neosyntis';

const tabs = [
  { value: 'search', label: 'Search Engine', icon: Search },
  { value: 'datasets', label: 'Datasets', icon: Database },
  { value: 'workflow', label: 'Workflow', icon: Workflow },
  { value: 'telemetry', label: 'Telemetry', icon: BarChart3 },
  { value: 'devices', label: 'Device Settings', icon: Settings },
  { value: 'cognisys', label: 'COGNISYS Config', icon: Network },
  { value: 'ecosystem', label: 'Ecosystem Builder', icon: Box },
  { value: 'deployment', label: 'Model Deployment', icon: Upload },
  { value: 'ml', label: 'Machine Learning', icon: Brain },
];

export default function Neosyntis() {
  const search = useSearch();
  const [, setLocation] = useLocation();
  const params = new URLSearchParams(search);
  const tabFromUrl = params.get('tab') || 'search';
  const [activeTab, setActiveTab] = useState(tabFromUrl);

  useEffect(() => {
    setActiveTab(tabFromUrl);
  }, [tabFromUrl]);

  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    setLocation(`/dashboard/neosyntis?tab=${newTab}`);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">NEOSYNTIS Lab</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Research & Workflow Automation Platform
            </p>
          </div>
          <Badge variant="outline">v2.1.0</Badge>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="h-full flex flex-col">
          <div className="border-b bg-card/50 px-6 overflow-x-auto">
            <TabsList className="bg-transparent h-12 w-full justify-start gap-1">
              {tabs.map((tab) => (
                <TabsTrigger
                  key={tab.value}
                  value={tab.value}
                  className="gap-2 data-[state=active]:bg-background"
                  data-testid={`tab-${tab.value}`}
                >
                  <tab.icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          <div className="flex-1 overflow-auto">
            <TabsContent value="search" className="h-full m-0 p-6">
              <SearchEngineTab />
            </TabsContent>
            <TabsContent value="datasets" className="h-full m-0 p-6">
              <DatasetTab />
            </TabsContent>
            <TabsContent value="workflow" className="h-full m-0 p-6">
              <WorkflowBuilderTab />
            </TabsContent>
            <TabsContent value="telemetry" className="h-full m-0 p-6">
              <TelemetryTab />
            </TabsContent>
            <TabsContent value="devices" className="h-full m-0 p-6">
              <DeviceSettingsTab />
            </TabsContent>
            <TabsContent value="cognisys" className="h-full m-0 p-6">
              <CognisysConfigTab />
            </TabsContent>
            <TabsContent value="ecosystem" className="h-full m-0 p-6">
              <EcosystemBuilderTab />
            </TabsContent>
            <TabsContent value="deployment" className="h-full m-0 p-6">
              <ModelDeploymentTab />
            </TabsContent>
            <TabsContent value="ml" className="h-full m-0 p-6">
              <MachineLearningTab />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}
