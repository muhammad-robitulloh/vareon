import { useState, useEffect } from 'react';
import { useSearch, useLocation } from 'wouter';
import { Tabs, TabsContent, TabsList, TabsTrigger, Badge } from '@/components/ui';
import { MessageSquare, Terminal, Brain, Bot } from 'lucide-react'; // Added Brain and Bot icons
import {
  ChatInterfaceTab,
  TerminalTab,
  ContextMemoryPanel, // Keep using ContextMemoryPanel
  ArcanaAgentTab, // Import the new ArcanaAgentTab
} from '@/components/dashboard/arcana';

export default function Arcana() {
  const search = useSearch();
  const [, setLocation] = useLocation();
  const params = new URLSearchParams(search);
  const tabFromUrl = params.get('tab') || 'chat';
  const [activeTab, setActiveTab] = useState(tabFromUrl);

  useEffect(() => {
    setActiveTab(tabFromUrl);
  }, [tabFromUrl]);

  const handleTabChange = (newTab: string) => {
    setActiveTab(newTab);
    setLocation(`/dashboard/arcana?tab=${newTab}`);
  };

  return (
    <div className="h-full">
      <div className="border-b border-border bg-card/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground text-glow">ARCANA Cognitive System</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Conversational AI & Shell Interface
            </p>
          </div>
          <Badge variant="outline" className="border-primary text-primary">GPT-4 Active</Badge>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <Tabs value={activeTab} onValueChange={handleTabChange} className="h-full flex flex-col">
          <div className="border-b border-border bg-card px-6">
            <TabsList className="bg-transparent h-12">
              <TabsTrigger
                value="chat"
                className="gap-2"
                data-testid="tab-chat"
              >
                <MessageSquare className="h-4 w-4" />
                Chat Interface
              </TabsTrigger>
              <TabsTrigger
                value="terminal"
                className="gap-2"
                data-testid="tab-terminal"
              >
                <Terminal className="h-4 w-4" />
                Terminal
              </TabsTrigger>
              <TabsTrigger
                value="memory"
                className="gap-2"
                data-testid="tab-memory"
              >
                <Brain className="h-4 w-4" /> {/* Using Brain icon for Context Memory */}
                Context Memory
              </TabsTrigger>
              <TabsTrigger
                value="agent"
                className="gap-2"
                data-testid="tab-agent"
              >
                <Bot className="h-4 w-4" /> {/* Using Bot icon for Arcana Mode Agent */}
                Arcana Mode Agent
              </TabsTrigger>
            </TabsList>
          </div>

          <div className="flex-1 overflow-hidden">
            <TabsContent value="chat" className="h-full m-0">
              <ChatInterfaceTab />
            </TabsContent>
            <TabsContent value="terminal" className="h-full m-0">
              <TerminalTab />
            </TabsContent>
            <TabsContent value="memory" className="h-full m-0">
              <ContextMemoryPanel /> {/* Use ContextMemoryPanel */}
            </TabsContent>
            <TabsContent value="agent" className="h-full m-0">
              <ArcanaAgentTab /> {/* New ArcanaAgentTab */}
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}