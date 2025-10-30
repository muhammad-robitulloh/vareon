import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Activity } from "lucide-react";

export default function TelemetryChart() {
  const [dataPoints, setDataPoints] = useState(
    Array.from({ length: 20 }, (_, i) => ({
      x: i,
      y: 30 + Math.random() * 40,
    }))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setDataPoints((prevDataPoints) => {
        const newDataPoints = [...prevDataPoints.slice(1), { // Shift data points to the left
          x: prevDataPoints[prevDataPoints.length - 1].x + 1,
          y: 30 + Math.random() * 40, // Generate new random data point
        }];
        return newDataPoints;
      });
    }, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  const maxY = 100;
  const height = 200;

  const latestY = dataPoints[dataPoints.length - 1].y;
  const averageY = dataPoints.reduce((a, b) => a + b.y, 0) / dataPoints.length;
  const peakY = Math.max(...dataPoints.map(d => d.y));

  return (
    <Card className="border border-card-border p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-primary" />
          <span className="font-semibold text-foreground">Real-time Telemetry</span>
        </div>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 rounded-full bg-chart-1" />
            <span className="text-muted-foreground">CPU Load</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="h-2 w-2 rounded-full bg-chart-3" />
            <span className="text-muted-foreground">Status: Running</span>
          </div>
        </div>
      </div>

      <div className="relative h-[200px] rounded-lg bg-muted/30 p-4">
        <svg width="100%" height={height} className="overflow-visible">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="hsl(var(--chart-1))" stopOpacity="0.3" />
              <stop offset="100%" stopColor="hsl(var(--chart-1))" stopOpacity="0.05" />
            </linearGradient>
          </defs>
          
          <path
            d={`M 0 ${height} ${dataPoints
              .map((point, i) => {
                const x = (i / (dataPoints.length - 1)) * 100;
                const y = height - (point.y / maxY) * height;
                return `L ${x}% ${y}`;
              })
              .join(" ")} L 100% ${height} Z`}
            fill="url(#chartGradient)"
          />
          
          <polyline
            points={dataPoints
              .map((point, i) => {
                const x = (i / (dataPoints.length - 1)) * 100;
                const y = height - (point.y / maxY) * height;
                return `${x}%,${y}`;
              })
              .join(" ")}
            fill="none"
            stroke="hsl(var(--chart-1))"
            strokeWidth="2"
            className="transition-all duration-500 ease-linear" // Added for smooth transitions
          />
        </svg>

        <div className="absolute bottom-4 left-4 right-4 flex justify-between text-xs text-muted-foreground">
          <span>0s</span>
          <span>10s</span>
          <span>20s</span>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-muted/50 p-3">
          <div className="text-2xl font-bold text-foreground">{latestY.toFixed(1)}%</div>
          <div className="text-xs text-muted-foreground">Current Load</div>
        </div>
        <div className="rounded-lg bg-muted/50 p-3">
          <div className="text-2xl font-bold text-foreground">
            {averageY.toFixed(1)}%
          </div>
          <div className="text-xs text-muted-foreground">Average</div>
        </div>
        <div className="rounded-lg bg-muted/50 p-3">
          <div className="text-2xl font-bold text-foreground">
            {peakY.toFixed(1)}%
          </div>
          <div className="text-xs text-muted-foreground">Peak</div>
        </div>
      </div>
    </Card>
  );
}
