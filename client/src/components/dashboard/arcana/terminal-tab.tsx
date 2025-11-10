import { useEffect, useRef, useState } from 'react';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import 'xterm/css/xterm.css';
import { Card, Button, Tabs, TabsList, TabsTrigger } from '@/components/ui';
import { Plus, X } from 'lucide-react';

interface TerminalInstance {
  id: string;
  name: string;
  terminal: XTerm;
  fitAddon: FitAddon;
  ws: WebSocket;
}

export default function TerminalTab() {
  console.log('TerminalTab component rendered');
  const terminalContainerRef = useRef<HTMLDivElement>(null);
  const [terminals, setTerminals] = useState<TerminalInstance[]>([]);
  const [activeTerminal, setActiveTerminal] = useState<string>('');
  const [fontSize, setFontSize] = useState<number>(10); // Default font size

  const createTerminal = () => {
    console.log('createTerminal called');
    const id = crypto.randomUUID();
    const name = `Terminal ${terminals.length + 1}`;

    const terminal = new XTerm({
      cursorBlink: true,
      fontSize: fontSize, // Use the fontSize state
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
    const webLinksAddon = new WebLinksAddon(); // Initialize WebLinksAddon
    terminal.loadAddon(webLinksAddon); // Load WebLinksAddon

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const accessToken = localStorage.getItem("access_token");
    // Connect to the new orchestrator endpoint
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws-api/ws/arcana/${id}?token=${accessToken}`);

    ws.onopen = () => {
      console.log(`Orchestrator WebSocket connected for terminal ${id}`);
      terminal.writeln('Welcome to ARCANA Terminal (via Orchestrator)');
      terminal.writeln('Cognitive Shell Interface v2.2.0');
      terminal.writeln('');
      // The backend shell process will send the initial prompt
      fitAddon.fit();
      const resizeEvent = {
        type: 'shell_resize',
        payload: { cols: terminal.cols, rows: terminal.rows }
      };
      ws.send(JSON.stringify(resizeEvent));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'shell_output' && message.payload.data) {
            terminal.write(message.payload.data);
        } else {
            console.log("Received unhandled message type:", message.type);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
        // Fallback for non-JSON data if needed, though protocol should be JSON
        terminal.write(event.data);
      }
    };

    ws.onclose = () => {
      console.log(`Terminal ${id} WebSocket disconnected`);
      terminal.writeln('\n\rConnection to terminal backend lost.');
    };

    ws.onerror = (error) => {
      console.error(`Terminal ${id} WebSocket error:`, error);
      terminal.writeln('\n\rTerminal connection error.');
    };

    terminal.onData((data) => {
      console.log(`terminal.onData for ${id}. Data: ${data}`);
      if (ws.readyState === WebSocket.OPEN) {
        const inputEvent = {
          type: 'shell_input',
          payload: { data: data }
        };
        ws.send(JSON.stringify(inputEvent));
      }
    });

    terminal.onResize((size) => {
      if (ws.readyState === WebSocket.OPEN) {
        const resizeEvent = {
          type: 'shell_resize',
          payload: { cols: size.cols, rows: size.rows }
        };
        ws.send(JSON.stringify(resizeEvent));
      }
    });

    const newTerminal: TerminalInstance = {
      id,
      name,
      terminal,
      fitAddon,
      ws, // Store WebSocket instance
    };

    setTerminals((prevTerminals) => [...prevTerminals, newTerminal]);
    setActiveTerminal(id);
  };

  const closeTerminal = (id: string) => {
    console.log(`closeTerminal called for ${id}`);
    const terminalToClose = terminals.find(t => t.id === id);
    if (terminalToClose) {
      terminalToClose.terminal.dispose();
      terminalToClose.ws.close(); // Close WebSocket connection
    }
    
    const newTerminals = terminals.filter(t => t.id !== id);
    setTerminals(newTerminals);
    
    if (activeTerminal === id && newTerminals.length > 0) {
      setActiveTerminal(newTerminals[0].id);
    } else if (activeTerminal === id && newTerminals.length === 0) {
      setActiveTerminal(''); // No active terminal if all are closed
    }
  };

  const handleFontSizeChange = (change: number) => {
    setFontSize((prevSize) => {
      const newSize = Math.max(5, Math.min(20, prevSize + change)); // Clamp between 5 and 20
      terminals.forEach(t => {
        t.terminal.options.fontSize = newSize; // Use direct option setting
        t.fitAddon.fit();
      });
      return newSize;
    });
  };

  useEffect(() => {
    console.log('useEffect [terminals] triggered. terminals.length:', terminals.length);
    if (terminals.length === 0) {
      createTerminal();
    }

    const resizeObserver = new ResizeObserver(() => { // Integrate ResizeObserver
      console.log('ResizeObserver triggered.');
      terminals.forEach(t => t.fitAddon.fit());
    });

    if (terminalContainerRef.current) {
      console.log('Observing terminalContainerRef.current for resize.');
      resizeObserver.observe(terminalContainerRef.current);
    } else {
      console.warn('terminalContainerRef.current is null in useEffect [terminals]. Cannot observe for resize.');
    }

    return () => {
      console.log('useEffect [terminals] cleanup function executed.');
      terminals.forEach(t => {
        console.log(`Disposing terminal ${t.id}.`);
        t.terminal.dispose();
        // t.ws.close(); // Removed: WebSocket should only be closed when explicitly closing a terminal
      });
      resizeObserver.disconnect(); // Disconnect ResizeObserver
    };
  }, [terminals]); // Added terminals to dependency array

  useEffect(() => {
    console.log('useEffect [activeTerminal] triggered. activeTerminal:', activeTerminal);
    const activeT = terminals.find(t => t.id === activeTerminal);

    // Detach all other terminals from the DOM
    terminals.forEach(t => {
      if (t.id !== activeTerminal && t.terminal.element && t.terminal.element.parentNode) {
        t.terminal.element.parentNode.removeChild(t.terminal.element);
        console.log(`Detached terminal ${t.id}`);
      }
    });

    if (activeT && terminalContainerRef.current) {
      console.log(`Attempting to display terminal ${activeT.id} in container.`);
      // If the terminal is not currently attached to the DOM, attach it
      if (!activeT.terminal.element || activeT.terminal.element.parentNode !== terminalContainerRef.current) {
        // Clear previous content if any, before attaching the new terminal
        if (terminalContainerRef.current.innerHTML !== '') {
          terminalContainerRef.current.innerHTML = '';
        }
        activeT.terminal.open(terminalContainerRef.current);
        console.log(`Terminal ${activeT.id} opened/reattached.`);
      }
      activeT.terminal.focus(); // Ensure the active terminal has focus
      activeT.fitAddon.fit();
      console.log(`FitAddon.fit() called for terminal ${activeT.id}.`);
    } else {
      console.warn('No active terminal or terminalContainerRef.current is null in useEffect [activeTerminal].');
    }
  }, [activeTerminal, terminals]); // Added terminals to dependency array for activeT find

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
                        <X className="h-4 w-4" />
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
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => handleFontSizeChange(-1)}>-</Button>
            <span>{fontSize}px</span>
            <Button variant="ghost" size="sm" onClick={() => handleFontSizeChange(1)}>+</Button>
          </div>
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
