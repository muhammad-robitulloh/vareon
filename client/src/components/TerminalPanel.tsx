import { useState } from "react";
import { Terminal as TerminalIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function TerminalPanel() {
  const [output, setOutput] = useState([
    "$ NeuroNet Shell v2.0",
    "$ Connected to NEOSYNTIS Lab",
    "$ Type 'help' for available commands",
    ""
  ]);
  const [input, setInput] = useState("");

  const handleCommand = (cmd: string) => {
    const newOutput = [...output, `$ ${cmd}`];
    
    // Mock command responses
    if (cmd === "help") {
      newOutput.push("Available commands:", "  ls     - List files", "  pwd    - Print working directory", "  clear  - Clear terminal", "");
    } else if (cmd === "ls") {
      newOutput.push("ai_core.py  ai_services.py  config.py  main.py", "");
    } else if (cmd === "pwd") {
      newOutput.push("/workspace/neuronet", "");
    } else if (cmd === "clear") {
      setOutput(["$ NeuroNet Shell v2.0", ""]);
      setInput("");
      return;
    } else if (cmd) {
      newOutput.push(`Command '${cmd}' not found. Type 'help' for available commands.`, "");
    }
    
    setOutput(newOutput);
    setInput("");
  };

  return (
    <div className="flex h-[400px] flex-col rounded-xl border border-border bg-black/50 font-mono text-sm">
      <div className="flex items-center justify-between border-b border-border bg-muted/30 px-4 py-2">
        <div className="flex items-center space-x-2">
          <TerminalIcon className="h-4 w-4 text-chart-3" />
          <span className="text-xs font-semibold text-foreground">WebSocket Shell</span>
        </div>
        <div className="flex space-x-1">
          <div className="h-3 w-3 rounded-full bg-chart-5" />
          <div className="h-3 w-3 rounded-full bg-chart-2" />
          <div className="h-3 w-3 rounded-full bg-chart-3" />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {output.map((line, idx) => (
            <div key={idx} className={line.startsWith('$') ? "text-chart-3" : "text-foreground/80"}>
              {line}
            </div>
          ))}
          <div className="flex items-center space-x-2">
            <span className="text-chart-3">$</span>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleCommand(input);
                }
              }}
              className="flex-1 bg-transparent text-foreground outline-none"
              placeholder="Enter command..."
              data-testid="input-terminal-command"
            />
          </div>
        </div>
      </div>

      <div className="border-t border-border bg-muted/30 px-4 py-2">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Press Enter to execute</span>
          <Button variant="ghost" size="sm" className="h-6 text-xs" onClick={() => handleCommand(input)} data-testid="button-execute-command">
            Execute
          </Button>
        </div>
      </div>
    </div>
  );
}
