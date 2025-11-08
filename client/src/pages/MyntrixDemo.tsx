import Navigation from "@/components/Navigation";
import JobSubmissionForm from "@/components/JobSubmissionForm";
import Footer from "@/components/Footer";
import { Cpu, Shield, Zap, Database } from "lucide-react";
import { Card } from '@/components/ui';

const features = [
  {
    icon: Shield,
    title: "Safety Validation",
    description: "Multi-layer safety checks including forbidden command detection, coordinate bounds validation, and feedrate limits.",
  },
  {
    icon: Zap,
    title: "Dry-run Simulation",
    description: "Execute jobs in simulation mode to validate behavior before committing to production hardware.",
  },
  {
    icon: Database,
    title: "Telemetry & Logging",
    description: "Real-time telemetry ingestion with journal entries and comprehensive execution history.",
  },
];

export default function Myntrix() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="bg-gradient-to-br from-chart-3/20 via-background to-background py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-8 flex items-center space-x-3">
            <Cpu className="h-8 w-8 text-chart-3" />
            <h1 className="text-4xl font-bold text-foreground">MYNTRIX Core</h1>
          </div>
          <p className="max-w-3xl text-lg text-muted-foreground">
            Manufacturing execution system adapted from NeuroNet architecture. Intelligent job planning,
            validation, and execution with human-in-loop safety protocols.
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <JobSubmissionForm />
          </div>

          <div className="space-y-6">
            <Card className="border border-card-border p-6">
              <h3 className="mb-4 font-semibold text-foreground">System Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Validator</span>
                  <div className="flex items-center space-x-2">
                    <div className="h-2 w-2 rounded-full bg-chart-3" />
                    <span className="text-sm text-foreground">Online</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Executor</span>
                  <div className="flex items-center space-x-2">
                    <div className="h-2 w-2 rounded-full bg-chart-3" />
                    <span className="text-sm text-foreground">Ready</span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">MQTT Bridge</span>
                  <div className="flex items-center space-x-2">
                    <div className="h-2 w-2 rounded-full bg-chart-5" />
                    <span className="text-sm text-foreground">Mock Mode</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="border border-card-border p-6">
              <h3 className="mb-4 font-semibold text-foreground">Recent Jobs</h3>
              <div className="space-y-3">
                <div className="rounded-lg bg-muted/50 p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-mono text-xs text-muted-foreground">job_x7k2m</span>
                    <span className="text-xs text-chart-3">Success</span>
                  </div>
                  <div className="text-sm text-foreground">CNC Node 1 - Dry Run</div>
                </div>
                <div className="rounded-lg bg-muted/50 p-3">
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-mono text-xs text-muted-foreground">job_p9n4q</span>
                    <span className="text-xs text-chart-3">Success</span>
                  </div>
                  <div className="text-sm text-foreground">CNC Node 2 - Validate</div>
                </div>
              </div>
            </Card>
          </div>
        </div>

        <div className="mt-16">
          <h2 className="mb-8 text-center text-3xl font-bold text-foreground">
            Core Modules
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            {features.map((feature) => (
              <Card key={feature.title} className="border border-card-border p-6 hover-elevate">
                <feature.icon className="mb-4 h-10 w-10 text-primary" />
                <h3 className="mb-3 text-xl font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>

        <div className="mt-16 rounded-2xl border border-primary/20 bg-primary/10 p-8">
          <h3 className="mb-4 text-2xl font-bold text-foreground">
            NeuroNet Integration
          </h3>
          <p className="text-muted-foreground">
            MYNTRIX Core is built on the foundation of the legacy NeuroNet system. The planner module uses
            the NeuroNet AI adapter to leverage reasoning capabilities, while the validator integrates
            legacy safety checks. This hybrid architecture combines proven AI intelligence with modern
            manufacturing execution standards.
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg bg-background p-4">
              <div className="mb-2 font-semibold text-foreground">Legacy Adapter Layer</div>
              <code className="text-sm text-muted-foreground">myntrix_core/adapters/legacy_adapter.py</code>
            </div>
            <div className="rounded-lg bg-background p-4">
              <div className="mb-2 font-semibold text-foreground">MQTT Bridge</div>
              <code className="text-sm text-muted-foreground">myntrix_core/adapters/mqtt_bridge.py</code>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
