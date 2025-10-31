import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { GitBranch, Plus, Trash2 } from 'lucide-react';

const routingRules = [
  { intent: 'code_generation', condition: 'contains("code") || contains("function")', targetModel: 'Codestral', priority: 1 },
  { intent: 'reasoning', condition: 'requires_deep_thinking()', targetModel: 'Claude-3.5-Sonnet', priority: 1 },
  { intent: 'conversation', condition: 'is_chat_message()', targetModel: 'GPT-4', priority: 2 },
  { intent: 'shell_command', condition: 'contains("terminal") || contains("shell")', targetModel: 'Command-R', priority: 1 },
];

export default function RoutingRulesTab() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-primary" />
                Routing Rules
              </CardTitle>
              <CardDescription className="mt-1">
                Define intent-based routing to appropriate models
              </CardDescription>
            </div>
            <Button data-testid="button-add-rule">
              <Plus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Intent Type</Label>
              <Select>
                <SelectTrigger data-testid="select-intent-type">
                  <SelectValue placeholder="Select intent..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="code_generation">Code Generation</SelectItem>
                  <SelectItem value="reasoning">Reasoning</SelectItem>
                  <SelectItem value="conversation">Conversation</SelectItem>
                  <SelectItem value="summarization">Summarization</SelectItem>
                  <SelectItem value="shell_command">Shell Command</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Condition</Label>
              <Input placeholder='contains("keyword")' data-testid="input-condition" />
            </div>
            <div className="space-y-2">
              <Label>Target Model</Label>
              <Select>
                <SelectTrigger data-testid="select-target-model">
                  <SelectValue placeholder="Select model..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="claude">Claude-3.5-Sonnet</SelectItem>
                  <SelectItem value="codestral">Codestral</SelectItem>
                  <SelectItem value="gemini">Gemini-Pro</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Active Rules</CardTitle>
          <CardDescription>
            Rules are evaluated in order of priority
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {routingRules.map((rule, idx) => (
            <Card key={idx} className="bg-card/50">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="default" className="text-xs">
                        {rule.intent.replace(/_/g, ' ')}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        Priority {rule.priority}
                      </Badge>
                    </div>
                    <div className="mt-2">
                      <div className="text-xs text-muted-foreground mb-1">Condition:</div>
                      <div className="text-sm font-mono bg-muted/30 px-2 py-1 rounded">
                        {rule.condition}
                      </div>
                    </div>
                    <div className="mt-2">
                      <div className="text-xs text-muted-foreground mb-1">Target:</div>
                      <Badge variant="secondary" className="text-xs">
                        {rule.targetModel}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="sm">Edit</Button>
                    <Button variant="ghost" size="sm" data-testid={`button-delete-rule-${idx}`}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))}
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-primary/10 via-background to-accent/10 border-primary/20">
        <CardHeader>
          <CardTitle className="text-base">Routing Logic</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            COGNISYS evaluates each request against routing rules in priority order:
          </p>
          <ol className="list-decimal list-inside space-y-1 ml-2">
            <li>Intent detection identifies the request type</li>
            <li>Matching rules are found based on conditions</li>
            <li>Highest priority matching rule determines the target model</li>
            <li>Request is routed to the selected model</li>
            <li>Optional reasoning step is applied if configured</li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}
