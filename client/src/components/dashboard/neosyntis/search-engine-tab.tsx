import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Button, Badge, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui';
import { Search, Save, Database, ExternalLink, Sparkles, Activity, Users, MapPin, Building } from 'lucide-react';
import { useToast } from '@/hooks/dashboard/use-toast';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// TYPE DEFINITIONS
interface SearchResultItem {
  title: string;
  snippet: string;
  url: string;
}

interface Entity {
  type: 'Person' | 'Organization' | 'Location';
  text: string;
  count: number;
}

interface SearchResult {
  id: string;
  query: string;
  provider: string;
  createdAt: string;
  saved?: boolean;
  summary: string;
  results: SearchResultItem[];
  entities: Entity[];
  sentiment: { positive: number; neutral: number; negative: number };
}

// MOCK DATA
const MOCK_SEARCH_RESULT: SearchResult = {
  id: 'res-1',
  query: 'Impact of AI on renewable energy',
  provider: 'google',
  createdAt: new Date().toISOString(),
  summary: 'AI is revolutionizing the renewable energy sector by optimizing grid management, improving forecasting for wind and solar, and accelerating the discovery of new materials for batteries and solar panels. This leads to increased efficiency, lower costs, and greater grid stability.',
  results: [
    { title: 'How AI is transforming renewable energy - McKinsey', snippet: 'AI can help optimize energy consumption, improve the accuracy of weather forecasting for renewables, and support the development of new clean energy technologies.', url: '#' },
    { title: 'The Role of AI in the Energy Transition - BCG', snippet: 'Artificial intelligence is a critical enabler for the energy transition, helping to integrate variable renewables and manage complex power grids.', url: '#' },
  ],
  entities: [
    { type: 'Organization', text: 'McKinsey', count: 1 },
    { type: 'Organization', text: 'BCG', count: 1 },
    { type: 'Person', text: 'Sundar Pichai', count: 0 }, // Example
    { type: 'Location', text: 'California', count: 0 }, // Example
  ],
  sentiment: { positive: 85, neutral: 10, negative: 5 },
};

const EntityIcon = ({ type }: { type: Entity['type'] }) => {
  switch (type) {
    case 'Person': return <Users className="h-4 w-4 text-blue-400" />;
    case 'Organization': return <Building className="h-4 w-4 text-green-400" />;
    case 'Location': return <MapPin className="h-4 w-4 text-red-400" />;
    default: return null;
  }
};

export default function SearchEngineTab() {
  const [query, setQuery] = useState('Impact of AI on renewable energy');
  const [provider, setProvider] = useState('google');
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: searchResult, refetch, isLoading } = useQuery({
    queryKey: ['/api/search', query, provider],
    queryFn: async (): Promise<SearchResult> => {
      // Mocking API call
      if (!query.trim()) return Promise.reject(new Error('Query is empty'));
      return Promise.resolve(MOCK_SEARCH_RESULT);
    },
    enabled: false, // Manually refetch
  });

  // Other mutations (saveToMemory, addToDataset) would be here...

  const handleSearch = () => {
    if (query.trim()) {
      refetch();
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Intelligent Search Engine
          </CardTitle>
          <CardDescription>
            Search the web with AI-powered summarization and knowledge extraction.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="google">Google</SelectItem>
                <SelectItem value="bing">Bing</SelectItem>
              </SelectContent>
            </Select>
            <Input
              placeholder="Enter your search query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={isLoading}>
              {isLoading ? <Activity className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}<span className="ml-2">Search</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {isLoading && <div className="text-center p-12">Searching...</div>}

      {searchResult ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Search Results for "{searchResult.query}"</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 bg-primary/5 rounded-lg border border-primary/10">
                  <div className="flex items-start gap-2 mb-2">
                    <Sparkles className="h-4 w-4 text-primary mt-0.5" />
                    <span className="text-sm font-medium">AI Summary</span>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {searchResult.summary}
                  </p>
                </div>
                {searchResult.results.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/50">
                    <ExternalLink className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-sm truncate">{item.title}</h5>
                      <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                        {item.snippet}
                      </p>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary hover:underline mt-1 inline-block">
                        {item.url}
                      </a>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Knowledge Panel</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Extracted Entities</h4>
                  <div className="space-y-2">
                    {searchResult.entities.filter(e => e.count > 0).map(entity => (
                      <div key={entity.text} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <EntityIcon type={entity.type} />
                          <span>{entity.text}</span>
                        </div>
                        <Badge variant="secondary">{entity.count}</Badge>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium mb-2">Sentiment Analysis</h4>
                  <ResponsiveContainer width="100%" height={150}>
                    <BarChart data={[
                      { name: 'Positive', value: searchResult.sentiment.positive, fill: '#22c55e' },
                      { name: 'Neutral', value: searchResult.sentiment.neutral, fill: '#a1a1aa' },
                      { name: 'Negative', value: searchResult.sentiment.negative, fill: '#ef4444' },
                    ]} layout="vertical">
                      <XAxis type="number" hide />
                      <YAxis type="category" dataKey="name" tickLine={false} axisLine={false} width={60} fontSize={12} />
                      <Tooltip cursor={{ fill: 'rgba(128,128,128,0.1)' }} />
                      <Bar dataKey="value" barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      ) : (
        !isLoading && (
          <Card className="p-12">
            <div className="text-center space-y-2">
              <Search className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
              <h3 className="text-lg font-medium">No search results yet</h3>
              <p className="text-sm text-muted-foreground">
                Enter a query above to start searching
              </p>
            </div>
          </Card>
        )
      )}
    </div>
  );
}
