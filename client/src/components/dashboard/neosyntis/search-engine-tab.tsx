import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search, Save, Database, ExternalLink, Sparkles } from 'lucide-react';
import { mockSearchResults } from '@/lib/dashboard/mockApi';
import { useToast } from '@/hooks/dashboard/use-toast';

export default function SearchEngineTab() {
  const [query, setQuery] = useState('');
  const [provider, setProvider] = useState('google');
  const { toast } = useToast();

  const { data: searchResults, refetch, isLoading } = useQuery({
    queryKey: ['/api/search', query],
    enabled: false,
    initialData: mockSearchResults,
  });

  const saveToMemory = useMutation({
    mutationFn: async () => {
      await new Promise(resolve => setTimeout(resolve, 500));
      return { success: true };
    },
    onSuccess: () => {
      toast({
        title: 'Saved to Memory',
        description: 'Search result saved to temporary memory',
      });
    },
  });

  const handleSearch = () => {
    if (query.trim()) {
      refetch();
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Intelligent Search Engine
          </CardTitle>
          <CardDescription>
            Search the web with AI-powered summarization and automatic memory storage
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-3">
            <Select value={provider} onValueChange={setProvider}>
              <SelectTrigger className="w-[180px]" data-testid="select-search-provider">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="google">Google</SelectItem>
                <SelectItem value="bing">Bing</SelectItem>
                <SelectItem value="duckduckgo">DuckDuckGo</SelectItem>
                <SelectItem value="serper">Serper API</SelectItem>
              </SelectContent>
            </Select>

            <Input
              placeholder="Enter your search query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
              data-testid="input-search-query"
            />

            <Button onClick={handleSearch} disabled={isLoading} data-testid="button-search">
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          <div className="flex gap-2 text-sm text-muted-foreground">
            <Badge variant="outline" className="gap-1">
              <Sparkles className="h-3 w-3" />
              Auto-summarization enabled
            </Badge>
            <Badge variant="outline">Temp memory active</Badge>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {searchResults?.map((result) => (
          <Card key={result.id} className="hover-elevate">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <CardTitle className="text-lg">{result.query}</CardTitle>
                  <CardDescription className="flex items-center gap-2 mt-1">
                    Provider: {result.provider} • {new Date(result.createdAt).toLocaleString()}
                    {result.saved && (
                      <Badge variant="secondary" className="ml-2">Saved</Badge>
                    )}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => saveToMemory.mutate(result.id)}
                    disabled={result.saved}
                    data-testid={`button-save-${result.id}`}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {result.saved ? 'Saved' : 'Save to Memory'}
                  </Button>
                  <Button variant="outline" size="sm" data-testid={`button-dataset-${result.id}`}>
                    <Database className="h-4 w-4 mr-2" />
                    Add to Dataset
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 bg-primary/5 rounded-lg border border-primary/10">
                <div className="flex items-start gap-2 mb-2">
                  <Sparkles className="h-4 w-4 text-primary mt-0.5" />
                  <span className="text-sm font-medium">AI Summary</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {result.summary}
                </p>
              </div>

              <div className="space-y-2">
                <h4 className="text-sm font-medium">Search Results</h4>
                {result.results?.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    className="flex items-start gap-3 p-3 rounded-lg border hover-elevate"
                  >
                    <ExternalLink className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-sm truncate">{item.title}</h5>
                      <p className="text-xs text-muted-foreground line-clamp-2 mt-1">
                        {item.snippet}
                      </p>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline mt-1 inline-block"
                      >
                        {item.url}
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}

        {searchResults?.length === 0 && (
          <Card className="p-12">
            <div className="text-center space-y-2">
              <Search className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
              <h3 className="text-lg font-medium">No search results yet</h3>
              <p className="text-sm text-muted-foreground">
                Enter a query above to start searching
              </p>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
