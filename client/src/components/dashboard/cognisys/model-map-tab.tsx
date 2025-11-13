import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Badge, Button } from '@/components/ui';
import { Network, Zap, Loader2, Trash2, Star } from 'lucide-react';
import * as d3 from 'd3';
import { useEffect, useRef } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { useToast } from '@/hooks/dashboard/use-toast';

// --- Interfaces ---
interface LLMModel {
  id: string;
  provider_id: string;
  model_name: string;
  type: string;
  is_active: boolean;
  reasoning: boolean;
  role?: string;
  max_tokens: number;
  cost_per_token: number;
  created_at: string;
  updated_at: string;
}

interface LLMProvider {
  id: string;
  name: string;
}

export default function ModelMapTab() {
  const svgRef = useRef<SVGSVGElement>(null);
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Fetch LLM Models
  const { data: models, isLoading: isLoadingModels, error: modelsError } = useQuery<LLMModel[]>({
    queryKey: ['cognisysLLMModels'],
    queryFn: async () => {
      const response = await fetch('/api/cognisys/models/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LLM models');
      }
      return response.json();
    },
    enabled: !!token,
  });

  // Fetch LLM Providers (to display provider names)
  const { data: providers, isLoading: isLoadingProviders, error: providersError } = useQuery<LLMProvider[]>({
    queryKey: ['cognisysLLMProvidersMinimal'], // Use a different key to avoid conflicts
    queryFn: async () => {
      const response = await fetch('/api/cognisys/providers/', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch LLM providers');
      }
      return response.json();
    },
    enabled: !!token,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  // Fetch User LLM Preferences
  const { data: userLLMPreferences, isLoading: isLoadingUserLLMPreferences, error: userLLMPreferencesError } = useQuery({
    queryKey: ['userLLMPreferences'],
    queryFn: async () => {
      const response = await fetch('/api/arcana/llm/preferences', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error('Failed to fetch user LLM preferences');
      }
      return response.json();
    },
    enabled: !!token,
  });

  const deleteModelMutation = useMutation({
    mutationFn: async (modelId: string) => {
      const response = await fetch(`/api/cognisys/models/${modelId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response (Delete Model):", errorBody);
        throw new Error(`Failed to delete model: ${response.status} ${response.statusText} - ${errorBody}`);
      }
      return { message: 'Model deleted successfully' };
    },
    onSuccess: () => {
      toast({ title: 'Model Deleted', description: 'LLM model has been successfully deleted.' });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMModels'] });
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to delete model: ${err.message}`, variant: 'destructive' });
    },
  });

  const setDefaultModelMutation = useMutation({
    mutationFn: async (modelId: string) => {
      const response = await fetch('/api/arcana/llm/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ default_model_id: modelId }),
      });
      if (!response.ok) {
        const errorBody = await response.text();
        console.error("API Error Response (Set Default Model):", errorBody);
        throw new Error(`Failed to set default model: ${response.status} ${response.statusText} - ${errorBody}`);
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Default Model Set', description: 'Default LLM model has been successfully updated.' });
      // Invalidate queries that depend on user preferences or default model
      queryClient.invalidateQueries({ queryKey: ['userLLMPreferences'] });
      queryClient.invalidateQueries({ queryKey: ['cognisysLLMModels'] }); // To potentially update UI if default model is highlighted
    },
    onError: (err) => {
      toast({ title: 'Error', description: `Failed to set default model: ${err.message}`, variant: 'destructive' });
    },
  });

  const getProviderName = (providerId: string) => {
    return providers?.find(p => p.id === providerId)?.name || 'Unknown Provider';
  };

  useEffect(() => {
    if (!svgRef.current || !models || !providers) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = 400;

    const centerX = width / 2;
    const centerY = height / 2;
    const radius = 150;

    const activeModels = models.filter(m => m.is_active);
    const angleStep = (2 * Math.PI) / activeModels.length;

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

    activeModels.forEach((model, index) => {
      const angle = index * angleStep - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      svg.append('line')
        .attr('x1', centerX)
        .attr('y1', centerY)
        .attr('x2', x)
        .attr('y2', y)
        .attr('stroke', model.is_active ? 'hsl(var(--primary))' : 'hsl(var(--muted))')
        .attr('stroke-width', 1.5)
        .attr('opacity', 0.3);

      svg.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 35)
        .attr('fill', 'hsl(var(--card))')
        .attr('stroke', model.is_active ? 'hsl(var(--primary))' : 'hsl(var(--muted))')
        .attr('stroke-width', 2);

      const text = svg.append('text')
        .attr('x', x)
        .attr('y', y)
        .attr('text-anchor', 'middle')
        .attr('class', 'fill-current text-xs');

      const words = model.model_name.split('-');
      words.forEach((word, i) => {
        text.append('tspan')
          .attr('x', x)
          .attr('dy', i === 0 ? -5 : 12)
          .text(word.length > 8 ? word.substring(0, 8) : word);
      });
    });
  }, [models, providers]);

  if (isLoadingModels || isLoadingProviders || isLoadingUserLLMPreferences) return <div className="p-4 text-center"><Loader2 className="h-6 w-6 animate-spin mx-auto" /> Loading models...</div>;
  if (modelsError) return <div className="p-4 text-center text-red-500">Error loading models: {modelsError.message}</div>;
  if (providersError) return <div className="p-4 text-center text-red-500">Error loading providers: {providersError.message}</div>;
  if (userLLMPreferencesError) return <div className="p-4 text-center text-red-500">Error loading user preferences: {userLLMPreferencesError.message}</div>;

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
            {models?.filter(m => m.is_active).map((model) => (
              <div key={model.id} className="flex items-start gap-3 p-4 border rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-sm flex items-center gap-2">
                    {model.model_name}
                    {userLLMPreferences?.default_model_id === model.id && (
                      <Badge variant="secondary" className="text-xs gap-1">
                        <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        Default
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">{getProviderName(model.provider_id)}</Badge>
                    <Badge variant="outline" className="text-xs">{model.type}</Badge>
                    {model.reasoning && (
                      <Badge variant="secondary" className="text-xs gap-1">
                        <Zap className="h-3 w-3" />
                        Reasoning
                      </Badge>
                    )}
                  </div>
                  {model.role && (
                    <div className="text-xs text-muted-foreground mt-1">
                      Role: {model.role.replace(/_/g, ' ')}
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setDefaultModelMutation.mutate(model.id)}
                    disabled={setDefaultModelMutation.isPending || userLLMPreferences?.default_model_id === model.id}
                  >
                    {setDefaultModelMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Star className="h-4 w-4" />}
                    Set as Default
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteModelMutation.mutate(model.id)}
                    disabled={deleteModelMutation.isPending}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
