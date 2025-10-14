import Navigation from "@/components/Navigation";
import ChatInterface from "@/components/ChatInterface";
import TerminalPanel from "@/components/TerminalPanel";
import TelemetryChart from "@/components/TelemetryChart";
import Footer from "@/components/Footer";
import { FlaskConical } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Neosyntis() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="bg-gradient-to-br from-chart-2/20 via-background to-background py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8 flex items-center space-x-3">
            <FlaskConical className="h-8 w-8 text-chart-2" />
            <h1 className="text-4xl font-bold text-foreground">NEOSYNTIS Lab</h1>
          </div>
          <p className="max-w-3xl text-lg text-muted-foreground">
            Interactive AI research dashboard powered by NeuroNet. Real-time chat, code generation, 
            shell terminal, and telemetry visualization in a unified development environment.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <Tabs defaultValue="chat" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 lg:w-auto">
            <TabsTrigger value="chat" data-testid="tab-chat">AI Chat</TabsTrigger>
            <TabsTrigger value="terminal" data-testid="tab-terminal">Terminal</TabsTrigger>
            <TabsTrigger value="telemetry" data-testid="tab-telemetry">Telemetry</TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-6">
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <ChatInterface />
              </div>
              <div className="space-y-6">
                <div className="rounded-xl border border-border bg-card p-6">
                  <h3 className="mb-4 font-semibold text-foreground">Active Models</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between rounded-lg bg-muted/50 p-3">
                      <span className="text-sm text-foreground">Intent Detection</span>
                      <div className="h-2 w-2 rounded-full bg-chart-3" />
                    </div>
                    <div className="flex items-center justify-between rounded-lg bg-muted/50 p-3">
                      <span className="text-sm text-foreground">Code Generation</span>
                      <div className="h-2 w-2 rounded-full bg-chart-3" />
                    </div>
                    <div className="flex items-center justify-between rounded-lg bg-muted/50 p-3">
                      <span className="text-sm text-foreground">Conversation</span>
                      <div className="h-2 w-2 rounded-full bg-chart-3" />
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-border bg-card p-6">
                  <h3 className="mb-4 font-semibold text-foreground">Token Usage</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Session</span>
                      <span className="font-medium text-foreground">2,450</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total</span>
                      <span className="font-medium text-foreground">15,230</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div className="h-full w-[45%] bg-primary" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="terminal">
            <div className="grid gap-6 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <TerminalPanel />
              </div>
              <div className="rounded-xl border border-border bg-card p-6">
                <h3 className="mb-4 font-semibold text-foreground">Command History</h3>
                <div className="space-y-2 font-mono text-sm">
                  <div className="text-muted-foreground">$ ls -la</div>
                  <div className="text-muted-foreground">$ pwd</div>
                  <div className="text-muted-foreground">$ cat ai_core.py</div>
                  <div className="text-muted-foreground">$ python main.py</div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="telemetry">
            <TelemetryChart />
          </TabsContent>
        </Tabs>
      </div>

      <Footer />
    </div>
  );
}
