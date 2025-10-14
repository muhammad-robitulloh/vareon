import Navigation from "@/components/Navigation";
import NeuroNetCapabilities from "@/components/NeuroNetCapabilities";
import Footer from "@/components/Footer";
import { Brain, Sparkles } from "lucide-react";

export default function NeuroNet() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="relative overflow-hidden bg-gradient-to-br from-primary/20 via-background to-background py-24">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 2px 2px, hsl(var(--primary) / 0.15) 1px, transparent 0)`,
          backgroundSize: '32px 32px'
        }} />
        
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="mb-6 inline-flex items-center space-x-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2">
              <Brain className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">
                AI Core Engine
              </span>
            </div>

            <h1 className="mb-6 text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
              NeuroNet AI
            </h1>

            <p className="mx-auto mb-12 max-w-3xl text-xl text-muted-foreground">
              Multi-model LLM orchestration platform powering intelligent code generation, 
              shell command conversion, and contextual reasoning across the VAREON ecosystem.
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              <div className="rounded-xl border border-border bg-card px-6 py-4">
                <div className="text-2xl font-bold text-primary">6</div>
                <div className="text-sm text-muted-foreground">Core Capabilities</div>
              </div>
              <div className="rounded-xl border border-border bg-card px-6 py-4">
                <div className="text-2xl font-bold text-chart-2">5+</div>
                <div className="text-sm text-muted-foreground">LLM Models</div>
              </div>
              <div className="rounded-xl border border-border bg-card px-6 py-4">
                <div className="text-2xl font-bold text-chart-3">Real-time</div>
                <div className="text-sm text-muted-foreground">Streaming</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <NeuroNetCapabilities />

      <div className="bg-card py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-border bg-background p-8 md:p-12">
            <div className="flex items-start space-x-4">
              <Sparkles className="h-8 w-8 shrink-0 text-primary" />
              <div>
                <h3 className="mb-4 text-2xl font-bold text-foreground">
                  Seamless Integration with MYNTRIX
                </h3>
                <p className="mb-6 text-muted-foreground">
                  The legacy NeuroNet codebase has been integrated into MYNTRIX Core through a sophisticated adapter layer.
                  All original modules (ai_core.py, ai_services.py, llm_utils.py, file_utils.py, shell_utils.py) are preserved
                  in <code className="rounded bg-muted px-2 py-1 font-mono text-sm">myntrix_core/lib/legacy/</code> and
                  accessed through safe wrapper functions. This architecture enables:
                </p>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 font-semibold text-foreground">Legacy Code Preservation</div>
                    <div className="text-sm text-muted-foreground">
                      Original NeuroNet files remain untouched, ensuring backward compatibility and easy updates
                    </div>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 font-semibold text-foreground">Modern API Integration</div>
                    <div className="text-sm text-muted-foreground">
                      New MYNTRIX endpoints leverage legacy AI capabilities through clean adapter interfaces
                    </div>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 font-semibold text-foreground">Safety Wrappers</div>
                    <div className="text-sm text-muted-foreground">
                      Timeout protection, error handling, and validation layers around legacy functions
                    </div>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 font-semibold text-foreground">Gradual Migration Path</div>
                    <div className="text-sm text-muted-foreground">
                      Ability to refactor legacy code incrementally while maintaining full system functionality
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
