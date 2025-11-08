import { Button } from '@/components/ui';
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "wouter";

export default function Hero() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-background" />
      {/* Animated background grid */}
      <div className="absolute inset-0 z-0 opacity-20" style={{
        backgroundImage: `radial-gradient(circle at 2px 2px, hsl(var(--primary) / 0.15) 1px, transparent 0)`,
        backgroundSize: '32px 32px'
      }} />
      <div className="absolute inset-0 z-0 animate-pulse-slow bg-gradient-to-br from-primary/5 via-transparent to-transparent" />

      <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8">
        <div className="flex min-h-[80vh] flex-col items-center justify-center text-center">
          <div className="mb-6 inline-flex items-center space-x-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2 animate-fade-in" data-testid="hero-sparkles-badge">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">
              Powered by Arcana AI
            </span>
          </div>

          <h1 className="mb-6 text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl animate-fade-in-up">
            Engineering
            <br />
            <span className="bg-gradient-to-r from-primary to-chart-2 bg-clip-text text-transparent">
              Adaptive Intelligence
            </span>
          </h1>

          <p className="mb-12 max-w-2xl text-lg text-muted-foreground sm:text-xl animate-fade-in-up animation-delay-200">
            The VAREON ecosystem integrates cutting-edge AI with manufacturing execution systems.
            From research to production, powered by Arcana's multi-model orchestration.
          </p>

          <div className="flex flex-col items-center space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0 animate-fade-in-up animation-delay-400">
            <Link href="/neosyntis-demo">
              <Button size="lg" className="group" data-testid="button-try-neosyntis">
                Try NEOSYNTIS Lab
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/arcana-demo">
              <Button size="lg" variant="outline" data-testid="button-explore-arcana">
                Explore Arcana AI
              </Button>
            </Link>
          </div>

          <div className="mt-20 grid gap-6 sm:grid-cols-3 animate-fade-in animation-delay-600">
            <div className="rounded-xl border border-border bg-card p-6 hover-elevate">
              <div className="mb-2 text-3xl font-bold text-primary">150K+</div>
              <div className="text-sm text-muted-foreground">AI Inferences Daily</div>
            </div>
            <div className="rounded-xl border border-border bg-card p-6 hover-elevate">
              <div className="mb-2 text-3xl font-bold text-chart-2">99.9%</div>
              <div className="text-sm text-muted-foreground">System Uptime</div>
            </div>
            <div className="rounded-xl border border-border bg-card p-6 hover-elevate">
              <div className="mb-2 text-3xl font-bold text-chart-3">24/7</div>
              <div className="text-sm text-muted-foreground">Real-time Monitoring</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
