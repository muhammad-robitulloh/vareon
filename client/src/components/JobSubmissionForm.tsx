import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Play, CheckCircle, XCircle } from "lucide-react";

export default function JobSubmissionForm() {
  const [content, setContent] = useState("G1 X10 Y10 F500\nG1 X20 Y20\nG1 X0 Y0");
  const [node, setNode] = useState("cnc-node-1");
  const [mode, setMode] = useState("dry-run");
  const [status, setStatus] = useState<"idle" | "validating" | "success" | "error">("idle");
  const [result, setResult] = useState("");

  const handleSubmit = () => {
    setStatus("validating");
    setResult("");

    setTimeout(() => {
      if (mode === "dry-run") {
        setStatus("success");
        setResult("✓ Validation passed\n✓ No forbidden commands detected\n✓ Coordinates within safe bounds\n✓ Feedrate acceptable (500 mm/min)\n\nSimulated execution complete. Ready for approval.");
      } else {
        setStatus("success");
        setResult("Job submitted for approval.\nJob ID: job_" + Math.random().toString(36).substr(2, 9));
      }
    }, 1500);
  };

  return (
    <Card className="border border-card-border p-6">
      <div className="mb-6">
        <h3 className="mb-2 text-xl font-semibold text-foreground">Submit Job</h3>
        <p className="text-sm text-muted-foreground">
          Create and validate manufacturing jobs with AI-powered safety checks
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-foreground">
            G-code / Task Content
          </label>
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="min-h-[120px] font-mono text-sm"
            placeholder="Enter G-code or task description..."
            data-testid="input-job-content"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">
              Target Node
            </label>
            <Select value={node} onValueChange={setNode}>
              <SelectTrigger data-testid="select-node">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="cnc-node-1">CNC Node 1</SelectItem>
                <SelectItem value="cnc-node-2">CNC Node 2</SelectItem>
                <SelectItem value="cnc-node-3">CNC Node 3</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-medium text-foreground">
              Execution Mode
            </label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger data-testid="select-mode">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dry-run">Dry Run (Simulate)</SelectItem>
                <SelectItem value="validate">Validate Only</SelectItem>
                <SelectItem value="execute">Execute (Requires Approval)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button 
          onClick={handleSubmit} 
          className="w-full" 
          disabled={status === "validating"}
          data-testid="button-submit-job"
        >
          {status === "validating" ? (
            <>
              <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
              Validating...
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Run {mode === "dry-run" ? "Dry Run" : "Job"}
            </>
          )}
        </Button>

        {result && (
          <div
            className={`rounded-lg border p-4 ${
              status === "success"
                ? "border-chart-3 bg-chart-3/10"
                : "border-destructive bg-destructive/10"
            }`}
          >
            <div className="mb-2 flex items-center space-x-2">
              {status === "success" ? (
                <CheckCircle className="h-5 w-5 text-chart-3" />
              ) : (
                <XCircle className="h-5 w-5 text-destructive" />
              )}
              <span className="font-semibold text-foreground">
                {status === "success" ? "Validation Result" : "Error"}
              </span>
            </div>
            <pre className="whitespace-pre-wrap font-mono text-sm text-foreground">
              {result}
            </pre>
          </div>
        )}
      </div>
    </Card>
  );
}
