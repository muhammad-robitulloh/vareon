import { Suspense, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Cpu, Upload, Activity, Box } from 'lucide-react';
import { StatusIndicator } from '../status-indicator';
import { mockDevices } from '@/pages/Dashboard/client/src/lib/mockApi';
import { useQuery } from '@tanstack/react-query';

function Cube() {
  return (
    <mesh>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="hsl(var(--primary))" />
    </mesh>
  );
}

export default function DeviceControlTab() {
  const [activeDevice, setActiveDevice] = useState('1');

  const { data: devices } = useQuery({
    queryKey: ['/api/devices'],
    initialData: mockDevices,
  });

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
            {devices?.map((device) => (
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
                  <div className="text-2xl font-bold mt-1">42°C</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Speed</div>
                  <div className="text-2xl font-bold mt-1">1200 RPM</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Position X</div>
                  <div className="text-2xl font-bold mt-1 font-mono">125.4</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="text-sm text-muted-foreground">Position Y</div>
                  <div className="text-2xl font-bold mt-1 font-mono">87.2</div>
                </div>
              </div>
              <div className="mt-4 p-4 bg-background/50 rounded-lg font-mono text-xs space-y-1">
                <div className="text-green-500">[12:34:56] Device connected</div>
                <div className="text-blue-500">[12:35:01] Homing sequence started</div>
                <div className="text-blue-500">[12:35:04] Homing complete</div>
                <div className="text-yellow-500">[12:35:10] Temperature reading: 42°C</div>
                <div className="text-green-500">[12:35:15] Ready for operation</div>
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
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover-elevate cursor-pointer">
                <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">
                  Drop G-code or firmware file here
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports .gcode, .nc, .hex, .bin formats
                </p>
              </div>
              <Button className="w-full" data-testid="button-upload-to-device">
                <Upload className="h-4 w-4 mr-2" />
                Upload to Device
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
