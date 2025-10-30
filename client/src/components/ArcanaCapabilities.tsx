import { Card } from "@/components/ui/card";
import { Brain, Code, Terminal, Zap, MessageSquare, FileCode } from "lucide-react";

const capabilities = [
  {
    icon: Brain,
    title: "Intent Detection",
    description: "Automatically classifies user requests into shell commands, code generation, or conversation using specialized LLM models.",
    model: "mistralai/mistral-small-3.2-24b",
  },
  {
    icon: Code,
    title: "Code Generation",
    description: "Generates complete, runnable code in multiple languages with context-aware suggestions and error fixing capabilities.",
    model: "moonshotai/kimi-dev-72b",
  },
  {
    icon: Terminal,
    title: "Shell Command Translation",
    description: "Converts natural language instructions into safe, executable shell commands with whitelist-based security.",
    model: "nvidia/llama-3.3-nemotron-super-49b",
  },
  {
    icon: Zap,
    title: "Reasoning System",
    description: "Generates detailed reasoning traces explaining the AI's thought process and planned actions before execution.",
    enabled: "Configurable",
  },
  {
    icon: MessageSquare,
    title: "Conversational AI",
    description: "Maintains context-aware conversations with chat history, providing helpful assistance for general queries.",
    model: "mistralai/mistral-small-3.2-24b",
  },
  {
    icon: FileCode,
    title: "File Operations",
    description: "Manages generated code files, uploaded documents, and system artifacts with security-restricted access controls.",
    storage: "In-memory / File system",
  },
];

export default function ArcanaCapabilities() {
  return (
    <div className="bg-background py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-foreground">
            Arcana AI Capabilities
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Multi-model LLM orchestration powering the entire VAREON ecosystem
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {capabilities.map((capability) => (
            <Card key={capability.title} className="group border border-card-border p-6 transition-all duration-300 hover:shadow-lg hover:border-primary/50">
              <div className="mb-4 flex items-center justify-between">
                <capability.icon className="h-10 w-10 text-primary transition-transform duration-300 group-hover:scale-110" />
                <div className="h-2 w-2 rounded-full bg-chart-3" />
              </div>
              
              <h3 className="mb-3 text-lg font-semibold text-foreground">
                {capability.title}
              </h3>
              
              <p className="mb-4 text-sm text-muted-foreground">
                {capability.description}
              </p>

              {(capability.model || capability.enabled || capability.storage) && (
                <div className="rounded-lg bg-muted/50 px-3 py-2">
                  <div className="text-xs font-medium text-muted-foreground">
                    {capability.model && `Model: ${capability.model.split('/')[1]}`}
                    {capability.enabled && `Status: ${capability.enabled}`}
                    {capability.storage && `Storage: ${capability.storage}`}
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>

        <div className="mt-16 rounded-2xl border border-primary/20 bg-primary/10 p-8">
          <div className="text-center">
            <h3 className="mb-4 text-2xl font-bold text-foreground">
              Legacy Integration Architecture
            </h3>
            <p className="mx-auto max-w-3xl text-muted-foreground">
                  The legacy Arcana codebase has been integrated into MYNTRIX Core through a sophisticated adapter layer.
              All legacy modules (ai_core.py, ai_services.py, llm_utils.py) are preserved in myntrix_core/lib/legacy/ and accessed
              via safe wrapper functions, enabling the entire ecosystem to leverage proven AI capabilities while maintaining
              modern architecture standards.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
