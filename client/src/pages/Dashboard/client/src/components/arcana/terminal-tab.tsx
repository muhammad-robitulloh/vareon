import { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Tabs, TabsList, TabsTrigger } from '../ui/tabs';
import { Plus, X } from 'lucide-react';

interface TerminalInstance {
  id: string;
  name: string;
  terminal: XTerm;
  fitAddon: FitAddon;
}

export default function TerminalTab() {
  const terminalContainerRef = useRef<HTMLDivElement>(null);
  const [terminals, setTerminals] = useState<TerminalInstance[]>([]);
  const [activeTerminal, setActiveTerminal] = useState<string>('');

  const createTerminal = () => {
    const id = Date.now().toString();
    const name = `Terminal ${terminals.length + 1}`;
    
    const terminal = new XTerm({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'JetBrains Mono, monospace',
      theme: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        cursor: 'hsl(var(--primary))',
        black: 'hsl(var(--muted))',
        red: '#ef4444',
        green: '#22c55e',
        yellow: '#eab308',
        blue: '#3b82f6',
        magenta: '#a855f7',
        cyan: '#06b6d4',
        white: 'hsl(var(--foreground))',
      },
    });

    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    const newTerminal: TerminalInstance = {
      id,
      name,
      terminal,
      fitAddon,
    };

    setTerminals([...terminals, newTerminal]);
    setActiveTerminal(id);

    setTimeout(() => {
      if (terminalContainerRef.current) {
        terminal.open(terminalContainerRef.current);
        fitAddon.fit();

        terminal.writeln('Welcome to ARCANA Terminal');
        terminal.writeln('Cognitive Shell Interface v2.1.0');
        terminal.writeln('');
        terminal.write('$ ');

        let currentLine = '';
        terminal.onData((data) => {
          if (data === '\r') {
            terminal.writeln('');
            
            if (currentLine.trim()) {
              const command = currentLine.trim();
              terminal.writeln(`Mock output for: ${command}`);
              terminal.writeln('This would execute the command in production');
            }
            
            terminal.write('$ ');
            currentLine = '';
          } else if (data === '\u007F') {
            if (currentLine.length > 0) {
              currentLine = currentLine.slice(0, -1);
              terminal.write('\b \b');
            }
          } else {
            currentLine += data;
            terminal.write(data);
          }
        });
      }
    }, 100);
  };

  const closeTerminal = (id: string) => {
    const terminalToClose = terminals.find(t => t.id === id);
    if (terminalToClose) {
      terminalToClose.terminal.dispose();
    }
    
    const newTerminals = terminals.filter(t => t.id !== id);
    setTerminals(newTerminals);
    
    if (activeTerminal === id && newTerminals.length > 0) {
      setActiveTerminal(newTerminals[0].id);
    }
  };

  useEffect(() => {
    if (terminals.length === 0) {
      createTerminal();
    }

    return () => {
      terminals.forEach(t => t.terminal.dispose());
    };
  }, []);

  useEffect(() => {
    const activeT = terminals.find(t => t.id === activeTerminal);
    if (activeT && terminalContainerRef.current) {
      terminalContainerRef.current.innerHTML = '';
      activeT.terminal.open(terminalContainerRef.current);
      activeT.fitAddon.fit();
    }
  }, [activeTerminal]);

  return (
    <div className="h-full flex flex-col p-6">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <div className="border-b bg-card/50 px-4 py-2 flex items-center justify-between">
          <Tabs value={activeTerminal} onValueChange={setActiveTerminal} className="flex-1">
            <div className="flex items-center gap-2">
              <TabsList className="bg-transparent h-9">
                {terminals.map((term) => (
                  <TabsTrigger
                    key={term.id}
                    value={term.id}
                    className="gap-2 data-[state=active]:bg-background"
                    data-testid={`tab-terminal-${term.id}`}
                  >
                    {term.name}
                    {terminals.length > 1 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          closeTerminal(term.id);
                        }}
                        className="ml-1 hover:bg-muted rounded-sm p-0.5"
                        data-testid={`button-close-terminal-${term.id}`}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </TabsTrigger>
                ))}
              </TabsList>
              <Button
                variant="ghost"
                size="sm"
                onClick={createTerminal}
                data-testid="button-new-terminal"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </Tabs>
        </div>

        <div className="flex-1 p-4 overflow-hidden">
          <div
            ref={terminalContainerRef}
            className="h-full w-full rounded-md overflow-hidden bg-background"
          />
        </div>
      </Card>

      <div className="mt-4 text-xs text-muted-foreground flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span>CWD: ~/projects/vareon</span>
          <span>Shell: bash</span>
        </div>
        <div className="flex items-center gap-2">
          <kbd className="px-2 py-1 bg-muted rounded text-xs">Ctrl+C</kbd>
          <span>Interrupt</span>
          <kbd className="px-2 py-1 bg-muted rounded text-xs ml-4">Ctrl+L</kbd>
          <span>Clear</span>
        </div>
      </div>
    </div>
  );
}
