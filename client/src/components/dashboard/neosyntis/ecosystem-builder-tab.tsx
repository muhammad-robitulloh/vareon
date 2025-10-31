import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Box, Layers, Network, Plus } from 'lucide-react';

export default function EcosystemBuilderTab() {
  const modules = [
    { name: 'VAREON', color: 'bg-blue-500', connected: true },
    { name: 'NEOSYNTIS', color: 'bg-purple-500', connected: true },
    { name: 'MYNTRIX', color: 'bg-green-500', connected: true },
    { name: 'COGNISYS', color: 'bg-orange-500', connected: true },
    { name: 'ARCANA', color: 'bg-pink-500', connected: true },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Box className="h-5 w-5 text-primary" />
            Ecosystem Architecture Builder
          </CardTitle>
          <CardDescription>
            Visualize and customize your VAREON ecosystem architecture
          </CardDescription>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">System Architecture</CardTitle>
          <CardDescription>
            Visual representation of module connections and data flow
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-96 bg-gradient-to-br from-primary/5 via-background to-accent/5 rounded-lg border border-dashed flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center">
              <svg className="w-full h-full" viewBox="0 0 800 600">
                <defs>
                  <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.3" />
                    <stop offset="50%" stopColor="hsl(var(--accent))" stopOpacity="0.5" />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0.3" />
                  </linearGradient>
                </defs>
                
                <line x1="400" y1="100" x2="400" y2="200" stroke="url(#line-gradient)" strokeWidth="2" />
                <line x1="400" y1="250" x2="250" y2="350" stroke="url(#line-gradient)" strokeWidth="2" />
                <line x1="400" y1="250" x2="550" y2="350" stroke="url(#line-gradient)" strokeWidth="2" />
                <line x1="250" y1="400" x2="150" y2="500" stroke="url(#line-gradient)" strokeWidth="2" />
                <line x1="250" y1="400" x2="350" y2="500" stroke="url(#line-gradient)" strokeWidth="2" />
                <line x1="550" y1="400" x2="650" y2="500" stroke="url(#line-gradient)" strokeWidth="2" />
                
                <circle cx="400" cy="100" r="60" fill="hsl(var(--card))" stroke="hsl(var(--primary))" strokeWidth="3" />
                <text x="400" y="110" textAnchor="middle" className="fill-current text-sm font-bold">VAREON</text>
                
                <circle cx="400" cy="250" r="50" fill="hsl(var(--card))" stroke="hsl(var(--primary))" strokeWidth="2" />
                <text x="400" y="260" textAnchor="middle" className="fill-current text-xs font-medium">COGNISYS</text>
                
                <circle cx="250" cy="400" r="45" fill="hsl(var(--card))" stroke="hsl(var(--accent))" strokeWidth="2" />
                <text x="250" y="407" textAnchor="middle" className="fill-current text-xs">NEOSYNTIS</text>
                
                <circle cx="550" cy="400" r="45" fill="hsl(var(--card))" stroke="hsl(var(--accent))" strokeWidth="2" />
                <text x="550" y="407" textAnchor="middle" className="fill-current text-xs">MYNTRIX</text>
                
                <circle cx="150" cy="520" r="35" fill="hsl(var(--card))" stroke="hsl(var(--chart-3))" strokeWidth="2" />
                <text x="150" y="527" textAnchor="middle" className="fill-current text-xs">Search</text>
                
                <circle cx="350" cy="520" r="35" fill="hsl(var(--card))" stroke="hsl(var(--chart-3))" strokeWidth="2" />
                <text x="350" y="527" textAnchor="middle" className="fill-current text-xs">Workflow</text>
                
                <circle cx="650" cy="520" r="35" fill="hsl(var(--card))" stroke="hsl(var(--chart-4))" strokeWidth="2" />
                <text x="650" y="527" textAnchor="middle" className="fill-current text-xs">ARCANA</text>
              </svg>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Layers className="h-5 w-5 text-primary" />
              Active Modules
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {modules.map((module) => (
              <div key={module.name} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`h-3 w-3 rounded-full ${module.color}`} />
                  <span className="font-medium">{module.name}</span>
                </div>
                <Badge variant={module.connected ? 'default' : 'outline'}>
                  {module.connected ? 'Connected' : 'Disconnected'}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Network className="h-5 w-5 text-primary" />
              Integration Points
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">NEOSYNTIS → ARCANA</div>
              <div className="text-xs text-muted-foreground mt-1">
                Search results auto-save to chat memory
              </div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">ARCANA → MYNTRIX</div>
              <div className="text-xs text-muted-foreground mt-1">
                Chat commands trigger agent jobs
              </div>
            </div>
            <div className="p-3 border rounded-lg">
              <div className="font-medium text-sm">COGNISYS → ALL</div>
              <div className="text-xs text-muted-foreground mt-1">
                Model routing for all modules
              </div>
            </div>
            <Button variant="outline" className="w-full mt-2" data-testid="button-add-integration">
              <Plus className="h-4 w-4 mr-2" />
              Add Custom Integration
            </Button>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Custom Architecture</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            This is a placeholder for advanced ecosystem customization. You can define:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Custom module relationships and data flows</li>
            <li>Conditional routing rules between components</li>
            <li>Event-driven triggers and webhooks</li>
            <li>Custom API endpoints and integrations</li>
            <li>Resource allocation and scaling policies</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
