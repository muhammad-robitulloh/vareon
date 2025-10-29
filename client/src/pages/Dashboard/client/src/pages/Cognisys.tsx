import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Network, Settings, GitBranch, Terminal } from 'lucide-react';
import ModelMapTab from '@/pages/Dashboard/client/src/components/cognisys/model-map-tab';
import RoutingRulesTab from '@/pages/Dashboard/client/src/components/cognisys/routing-rules-tab';
import ProviderSettingsTab from '@/pages/Dashboard/client/src/components/cognisys/provider-settings-tab';
import TestConsoleTab from '@/pages/Dashboard/client/src/components/cognisys/test-console-tab';

export default function Cognisys() {
  const [activeTab, setActiveTab] = useState('map');

  return (
    <div className="flex flex-col h-full">
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">COGNISYS</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Multimodel Orchestration & Routing System
            </p>
          </div>
          <Badge variant="outline" className="gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500" />
            12 Models Active
          </Badge>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 mb-6">
            <TabsTrigger value="map" className="gap-2" data-testid="tab-model-map">
              <Network className="h-4 w-4" />
              Model Map
            </TabsTrigger>
            <TabsTrigger value="routing" className="gap-2" data-testid="tab-routing">
              <GitBranch className="h-4 w-4" />
              Routing Rules
            </TabsTrigger>
            <TabsTrigger value="settings" className="gap-2" data-testid="tab-provider-settings">
              <Settings className="h-4 w-4" />
              Providers
            </TabsTrigger>
            <TabsTrigger value="test" className="gap-2" data-testid="tab-test-console">
              <Terminal className="h-4 w-4" />
              Test Console
            </TabsTrigger>
          </TabsList>

          <TabsContent value="map">
            <ModelMapTab />
          </TabsContent>

          <TabsContent value="routing">
            <RoutingRulesTab />
          </TabsContent>

          <TabsContent value="settings">
            <ProviderSettingsTab />
          </TabsContent>

          <TabsContent value="test">
            <TestConsoleTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
