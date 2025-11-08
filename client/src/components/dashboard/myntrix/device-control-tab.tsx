import { Suspense, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Badge, Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui';
import { Cpu, Upload, Activity, Box, Loader2 } from 'lucide-react';
import { StatusIndicator } from '../status-indicator';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@/hooks/dashboard/use-toast';

function Cube() {
  return (
    <mesh>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="hsl(var(--primary))" />
    </mesh>
  );
}

import { Device } from './types';

export default function DeviceControlTab() {
  const [activeDevice, setActiveDevice] = useState('1');

  const { data: devices } = useQuery<Device[]>({
    queryKey: ['/api/devices'],
    queryFn: async () => {
      const response = await fetch('/api/devices');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    },
  });

  const { toast } = useToast();
  const queryClient = useQueryClient();

  const connectDeviceMutation = useMutation({
    mutationFn: async (deviceId: string) => {
      const response = await fetch(`/api/devices/${deviceId}/connect`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to connect to device');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Device Connected', description: 'Successfully connected to device.' });
      queryClient.invalidateQueries({ queryKey: ['/api/devices'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to connect: ${error.message}`, variant: 'destructive' });
    },
  });

  const disconnectDeviceMutation = useMutation({
    mutationFn: async (deviceId: string) => {
      const response = await fetch(`/api/devices/${deviceId}/disconnect`, { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to disconnect from device');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Device Disconnected', description: 'Successfully disconnected from device.' });
      queryClient.invalidateQueries({ queryKey: ['/api/devices'] });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to disconnect: ${error.message}`, variant: 'destructive' });
    },
  });

  const sendCommandMutation = useMutation({
    mutationFn: async ({ deviceId, command }: { deviceId: string; command: string }) => {
      const response = await fetch(`/api/devices/${deviceId}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command }),
      });
      if (!response.ok) {
        throw new Error('Failed to send command');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'Command Sent', description: 'Command successfully sent to device.' });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to send command: ${error.message}`, variant: 'destructive' });
    },
  });

  const uploadFileMutation = useMutation({
    mutationFn: async ({ deviceId, file }: { deviceId: string; file: File }) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch(`/api/devices/${deviceId}/upload`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Failed to upload file');
      }
      return response.json();
    },
    onSuccess: () => {
      toast({ title: 'File Uploaded', description: 'File successfully uploaded to device.' });
    },
    onError: (error) => {
      toast({ title: 'Error', description: `Failed to upload file: ${error.message}`, variant: 'destructive' });
    },
  });

  const [telemetryData, setTelemetryData] = useState<any>({});
  const [telemetryLogs, setTelemetryLogs] = useState<string[]>([]);

  useEffect(() => {
    if (!activeDevice) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const accessToken = localStorage.getItem("access_token");
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/telemetry/${activeDevice}?token=${accessToken}`);

    ws.onopen = () => {
      console.log(`Telemetry WebSocket connected for device ${activeDevice}`);
      setTelemetryLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Connected to telemetry stream.`]);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'telemetry') {
        setTelemetryData(data.payload);
      } else if (data.type === 'log') {
        setTelemetryLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${data.payload}`]);
      }
    };

    ws.onclose = () => {
      console.log(`Telemetry WebSocket disconnected for device ${activeDevice}`);
      setTelemetryLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Disconnected from telemetry stream.`]);
    };

    ws.onerror = (error) => {
      console.error(`Telemetry WebSocket error for device ${activeDevice}:`, error);
      setTelemetryLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] Telemetry stream error.`]);
    };

    return () => {
      ws.close();
      setTelemetryData({});
      setTelemetryLogs([]);
    };
  }, [activeDevice]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            Device Control Center
          </CardTitle>
          <CardDescription>
            Monitor and control connected hardware devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {devices?.map((device: Device) => (
              <Card
                key={device.id}
                className={`cursor-pointer hover-elevate ${activeDevice === device.id ? 'border-primary' : ''}`}
                onClick={() => setActiveDevice(device.id)}
                data-testid={`card-device-${device.id}`}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{device.name}</CardTitle>
                    <StatusIndicator status={device.status as any} size="sm" />
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">{device.type.toUpperCase()}</Badge>
                    {device.port && (
                      <span className="text-xs text-muted-foreground font-mono">{device.port}</span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="flex justify-end gap-2">
                  {device.status === 'connected' ? (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        disconnectDeviceMutation.mutate(device.id);
                      }}
                      disabled={disconnectDeviceMutation.isPending}
                    >
                      {disconnectDeviceMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Disconnect'}
                    </Button>
                  ) : (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        connectDeviceMutation.mutate(device.id);
                      }}
                      disabled={connectDeviceMutation.isPending}
                    >
                      {connectDeviceMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Connect'}
                    </Button>
                  )}
                </CardContent>
                {device.lastSeen && (
                  <CardContent>
                    <div className="text-xs text-muted-foreground">
                      Last seen: {new Date(device.lastSeen).toLocaleString()}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="3d">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="3d" data-testid="tab-3d-viewer">
            <Box className="h-4 w-4 mr-2" />
            3D Viewer
          </TabsTrigger>
          <TabsTrigger value="telemetry" data-testid="tab-telemetry">
            <Activity className="h-4 w-4 mr-2" />
            Telemetry
          </TabsTrigger>
          <TabsTrigger value="upload" data-testid="tab-upload">
            <Upload className="h-4 w-4 mr-2" />
            Upload
          </TabsTrigger>
        </TabsList>

        <TabsContent value="3d" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">3D Model Viewer</CardTitle>
              <CardDescription>
                Preview CAD/CAM designs and G-code toolpaths
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96 bg-muted/20 rounded-lg border overflow-hidden">
                <Canvas camera={{ position: [5, 5, 5] }}>
                  <Suspense fallback={null}>
                    <ambientLight intensity={0.5} />
                    <directionalLight position={[10, 10, 5]} intensity={1} />
                    <Cube />
                    <Grid args={[10, 10]} cellColor="hsl(var(--muted-foreground))" sectionColor="hsl(var(--primary))" />
                    <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />
                  </Suspense>
                </Canvas>
              </div>
              <div className="flex gap-2 mt-4">
                <Button variant="outline" size="sm">Load STL</Button>
                <Button variant="outline" size="sm">Load OBJ</Button>
                <Button variant="outline" size="sm">Load G-Code</Button>
                <Button variant="outline" size="sm" className="ml-auto">Reset View</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="telemetry" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Live Telemetry</CardTitle>
              <CardDescription>
                Real-time device metrics and sensor data
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Temperature</div>
                  <div className="text-2xl font-bold mt-1">{telemetryData.temperature ? `${telemetryData.temperature}°C` : 'N/A'}</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Speed</div>
                  <div className="text-2xl font-bold mt-1">{telemetryData.speed ? `${telemetryData.speed} RPM` : 'N/A'}</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Position X</div>
                  <div className="text-2xl font-bold mt-1 font-mono">{telemetryData.positionX !== undefined ? telemetryData.positionX : 'N/A'}</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Position Y</div>
                  <div className="text-2xl font-bold mt-1 font-mono">{telemetryData.positionY !== undefined ? telemetryData.positionY : 'N/A'}</div>
                </div>
              </div>
              <div className="mt-4 p-4 bg-background/50 rounded-lg font-mono text-xs space-y-1 h-48 overflow-y-auto">
                {telemetryLogs.map((log, index) => (
                  <div key={index}>{log}</div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="upload" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Upload to Device</CardTitle>
              <CardDescription>
                Upload G-code or firmware to connected device
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <input
                type="file"
                id="file-upload"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0] && activeDevice) {
                    uploadFileMutation.mutate({ deviceId: activeDevice, file: e.target.files[0] });
                  }
                }}
              />
              <label htmlFor="file-upload" className="border-2 border-dashed rounded-lg p-8 text-center hover-elevate cursor-pointer block">
                <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">
                  Drop G-code or firmware file here, or click to select
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports .gcode, .nc, .hex, .bin formats
                </p>
              </label>
              <Button
                className="w-full"
                data-testid="button-upload-to-device"
                onClick={() => {
                  const fileInput = document.getElementById('file-upload') as HTMLInputElement;
                  if (fileInput) {
                    fileInput.click();
                  }
                }}
                disabled={!activeDevice || uploadFileMutation.isPending}
              >
                {uploadFileMutation.isPending ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                Upload to Device
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
