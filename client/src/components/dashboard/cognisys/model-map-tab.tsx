import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { mockModels } from '@/lib/dashboard/mockApi';
import { Network, Zap } from 'lucide-react';
import * as d3 from 'd3';
import { useEffect, useRef } from 'react';

export default function ModelMapTab() {
  const svgRef = useRef<SVGSVGElement>(null);

  const { data: models } = useQuery({
    queryKey: ['/api/models'],
    initialData: mockModels,
  });

  useEffect(() => {
    if (!svgRef.current || !models) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = 400;

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 150;

    const angleStep = (2 * Math.PI) / models.length;

    svg.append('circle')
      .attr('cx', centerX)
      .attr('cy', centerY)
      .attr('r', 60)
      .attr('fill', 'hsl(var(--card))')
      .attr('stroke', 'hsl(var(--primary))')
      .attr('stroke-width', 3);

    svg.append('text')
      .attr('x', centerX)
      .attr('y', centerY - 10)
      .attr('text-anchor', 'middle')
      .attr('class', 'fill-current font-bold text-sm')
      .text('COGNISYS');

    svg.append('text')
      .attr('x', centerX)
      .attr('y', centerY + 10)
      .attr('text-anchor', 'middle')
      .attr('class', 'fill-current text-xs text-muted-foreground')
      .text('Orchestrator');

    models.forEach((model, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      svg.append('line')
        .attr('x1', centerX)
        .attr('y1', centerY)
        .attr('x2', x)
        .attr('y2', y)
        .attr('stroke', model.isActive ? 'hsl(var(--primary))' : 'hsl(var(--muted))')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.3);

      svg.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 35)
        .attr('fill', 'hsl(var(--card))')
        .attr('stroke', model.isActive ? 'hsl(var(--primary))' : 'hsl(var(--muted))')
        .attr('stroke-width', 2);

      const text = svg.append('text')
        .attr('x', x)
        .attr('y', y)
        .attr('text-anchor', 'middle')
        .attr('class', 'fill-current text-xs');

      const words = model.name.split('-');
      words.forEach((word, i) => {
        text.append('tspan')
          .attr('x', x)
          .attr('dy', i === 0 ? -5 : 12)
          .text(word.length > 8 ? word.substring(0, 8) : word);
      });
    });
  }, [models]);

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5 text-primary" />
            Model Relationship Map
          </CardTitle>
          <CardDescription>
            Visual representation of all connected AI models
          </CardDescription>
        </CardHeader>
        <CardContent>
          <svg ref={svgRef} className="w-full" height="400" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Active Models</CardTitle>
          <CardDescription>
            Models currently available for routing
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {models?.filter(m => m.isActive).map((model) => (
              <div key={model.id} className="flex items-start gap-3 p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-sm">{model.name}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">{model.provider}</Badge>
                    <Badge variant="outline" className="text-xs">{model.type}</Badge>
                    {model.reasoning && (
                      <Badge variant="secondary" className="text-xs gap-1">
                        <Zap className="h-3 w-3" />
                        Reasoning
                      </Badge>
                    )}
                  </div>
                  {(model as any).role && (
                    <div className="text-xs text-muted-foreground mt-1">
                      Role: {(model as any).role.replace(/_/g, ' ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
