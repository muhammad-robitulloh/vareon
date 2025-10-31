import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, FlaskConical, Cpu, ArrowRight } from "lucide-react";
import { Link } from "wouter";

const divisions = [
  {
    icon: Brain,
    title: "Arcana AI",
    description: "Multi-model LLM orchestration with intent detection, code generation, and reasoning capabilities. The intelligent core powering the entire ecosystem.",
    features: ["Intent Detection", "Code Generation", "Shell Commands", "Reasoning System"],
    href: "/arcana-demo",
    color: "text-primary"
  },
  {
    icon: FlaskConical,
    title: "NEOSYNTIS Lab",
    description: "Interactive research dashboard for AI-powered development. Real-time collaboration, telemetry visualization, and intelligent task execution.",
    features: ["AI Chat Interface", "File Management", "WebSocket Terminal", "Analytics"],
    href: "/neosyntis-demo",
    color: "text-chart-2"
  },
  {
    icon: Cpu,
    title: "MYNTRIX Core",
    description: "Manufacturing execution system adapted from NeuroNet architecture. Intelligent job planning, validation, and execution with human-in-loop safety.",
    features: ["Job Planning", "Safety Validation", "Dry-run Mode", "MQTT Integration"],
    href: "/myntrix-demo",
    color: "text-chart-3"
  }
];

export default function DivisionsSection() {
  return (
    <div className="bg-background py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-foreground">
            Integrated Ecosystem
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Three powerful platforms working in harmony to deliver adaptive intelligence from development to deployment.
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-3">
          {divisions.map((division) => (
            <Card key={division.title} className="group relative overflow-hidden border border-card-border p-6 transition-all duration-300 hover:shadow-lg hover:border-primary/50">
              <div className="mb-4">
                <division.icon className={`h-12 w-12 ${division.color} transition-transform duration-300 group-hover:scale-110`} />
              </div>
              
              <h3 className="mb-3 text-2xl font-semibold text-foreground">
                {division.title}
              </h3>
              
              <p className="mb-6 text-muted-foreground">
                {division.description}
              </p>

              <div className="mb-6 space-y-2">
                {division.features.map((feature) => (
                  <div key={feature} className="flex items-center space-x-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="text-sm text-foreground">{feature}</span>
                  </div>
                ))}
              </div>

              <Link href={division.href}>
                <Button variant="ghost" className="group/btn w-full justify-between" data-testid={`button-explore-${division.title.toLowerCase().replace(' ', '-')}`}>
                  Explore {division.title}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover/btn:translate-x-1" />
                </Button>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
