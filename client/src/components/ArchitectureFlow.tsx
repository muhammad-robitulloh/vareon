import { ArrowRight } from "lucide-react";

export default function ArchitectureFlow() {
  const nodes = [
    { id: "arcana", label: "Arcana AI", subtitle: "Intelligence Core" },
    { id: "neosyntis", label: "NEOSYNTIS", subtitle: "Development Lab" },
    { id: "myntrix", label: "MYNTRIX", subtitle: "Execution Core" },
    { id: "edge", label: "Edge Devices", subtitle: "Production" },
  ];

  return (
    <div className="bg-card py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-foreground">
            How It Works
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Seamless integration from AI reasoning to production execution
          </p>
        </div>

        <div className="flex flex-col items-center space-y-8 md:flex-row md:space-x-4 md:space-y-0">
          {nodes.map((node, index) => (
            <div key={node.id} className="flex items-center">
              <div className="group relative transition-all duration-300 hover:scale-105 hover:shadow-xl">
                <div className="absolute -inset-1 rounded-xl bg-gradient-to-r from-primary to-chart-2 opacity-25 blur transition group-hover:opacity-50" />
                <div className="relative flex h-32 w-40 flex-col items-center justify-center rounded-xl border border-border bg-background p-4">
                  <div className="mb-2 text-lg font-bold text-foreground">
                    {node.label}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {node.subtitle}
                  </div>
                </div>
              </div>
              
              {index < nodes.length - 1 && (
                <ArrowRight className="mx-4 hidden h-8 w-8 text-primary md:block animate-pulse-horizontal" />
              )}
            </div>
          ))}
        </div>

        <div className="mt-16 grid gap-6 md:grid-cols-3">
          <div className="rounded-xl border border-border bg-background p-6">
            <div className="mb-3 text-lg font-semibold text-foreground">1. AI Processing</div>
            <p className="text-sm text-muted-foreground">
              Arcana AI analyzes tasks using multi-model orchestration, intent detection, and reasoning capabilities
            </p>
          </div>
          <div className="rounded-xl border border-border bg-background p-6">
            <div className="mb-3 text-lg font-semibold text-foreground">2. Validation</div>
            <p className="text-sm text-muted-foreground">
              MYNTRIX validates execution plans, performs safety checks, and requires human approval for critical operations
            </p>
          </div>
          <div className="rounded-xl border border-border bg-background p-6">
            <div className="mb-3 text-lg font-semibold text-foreground">3. Execution</div>
            <p className="text-sm text-muted-foreground">
              Commands are executed on edge devices with real-time telemetry monitoring and status updates
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
