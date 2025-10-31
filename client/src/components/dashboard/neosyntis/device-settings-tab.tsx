import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Cpu, Usb, Code, Box } from 'lucide-react';
import { StatusIndicator } from '../status-indicator';

export default function DeviceSettingsTab() {
  const [deviceType, setDeviceType] = useState<'cnc' | 'esp32' | 'arduino'>('cnc');
  const [viewMode, setViewMode] = useState<'cad' | 'cam' | 'ide'>('cad');

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5 text-primary" />
            Device Integration Settings
          </CardTitle>
          <CardDescription>
            Configure connections to CNC machines, ESP32, Arduino, and other hardware
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Device Type</label>
              <Select value={deviceType} onValueChange={(v: any) => setDeviceType(v)}>
                <SelectTrigger data-testid="select-device-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cnc">
                    <div className="flex items-center gap-2">
                      <Box className="h-4 w-4" />
                      CNC Machine
                    </div>
                  </SelectItem>
                  <SelectItem value="esp32">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4" />
                      ESP32
                    </div>
                  </SelectItem>
                  <SelectItem value="arduino">
                    <div className="flex items-center gap-2">
                      <Cpu className="h-4 w-4" />
                      Arduino
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Serial Port</label>
              <Select>
                <SelectTrigger data-testid="select-serial-port">
                  <SelectValue placeholder="Select port..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="/dev/ttyUSB0">/dev/ttyUSB0</SelectItem>
                  <SelectItem value="/dev/ttyUSB1">/dev/ttyUSB1</SelectItem>
                  <SelectItem value="/dev/ttyUSB2">/dev/ttyUSB2</SelectItem>
                  <SelectItem value="COM3">COM3</SelectItem>
                  <SelectItem value="COM4">COM4</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2">
            <Button data-testid="button-connect-device">
              <Usb className="h-4 w-4 mr-2" />
              Connect
            </Button>
            <Button variant="outline">Disconnect</Button>
            <Button variant="outline">Test Connection</Button>
          </div>

          <div className="flex items-center gap-4 p-4 bg-card/50 rounded-lg border">
            <StatusIndicator status="connected" />
            <div className="flex-1">
              <div className="font-medium text-sm">Connection Status</div>
              <div className="text-xs text-muted-foreground">Device connected on /dev/ttyUSB0</div>
            </div>
            <Badge variant="outline">115200 baud</Badge>
          </div>
        </CardContent>
      </Card>

      {deviceType === 'cnc' ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">CNC Control Interface</CardTitle>
            <CardDescription>
              CAD/CAM mode for G-code generation and machine control
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
              <TabsList>
                <TabsTrigger value="cad" data-testid="tab-cad">CAD Mode</TabsTrigger>
                <TabsTrigger value="cam" data-testid="tab-cam">CAM Mode</TabsTrigger>
              </TabsList>
              <TabsContent value="cad" className="mt-4 space-y-4">
                <div className="h-96 bg-muted/20 rounded-lg border border-dashed flex items-center justify-center">
                  <div className="text-center space-y-2">
                    <Box className="h-12 w-12 mx-auto text-muted-foreground opacity-50" />
                    <p className="text-sm text-muted-foreground">CAD Viewer</p>
                    <p className="text-xs text-muted-foreground">3D model viewer would appear here</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline">Import STL</Button>
                  <Button variant="outline">Import OBJ</Button>
                  <Button>Generate Toolpath</Button>
                </div>
              </TabsContent>
              <TabsContent value="cam" className="mt-4 space-y-4">
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Tool Diameter (mm)</label>
                      <Input type="number" defaultValue="6" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Spindle Speed (RPM)</label>
                      <Input type="number" defaultValue="12000" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Feed Rate (mm/min)</label>
                      <Input type="number" defaultValue="800" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Depth Per Pass (mm)</label>
                      <Input type="number" defaultValue="2" />
                    </div>
                  </div>
                  <Button className="w-full">Generate G-Code</Button>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-5 w-5 text-primary" />
              Integrated Development Environment
            </CardTitle>
            <CardDescription>
              Code editor for {deviceType.toUpperCase()} development
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="h-96 bg-muted/20 rounded-lg border font-mono text-sm p-4 overflow-auto">
              <div className="space-y-1">
                <div className="text-green-500">// {deviceType.toUpperCase()} Sketch</div>
                <div>{'void setup() {'}</div>
                <div className="pl-4">Serial.begin(115200);</div>
                <div className="pl-4">pinMode(LED_BUILTIN, OUTPUT);</div>
                <div>{'}'}</div>
                <div className="mt-2">{'void loop() {'}</div>
                <div className="pl-4">digitalWrite(LED_BUILTIN, HIGH);</div>
                <div className="pl-4">delay(1000);</div>
                <div className="pl-4">digitalWrite(LED_BUILTIN, LOW);</div>
                <div className="pl-4">delay(1000);</div>
                <div>{'}'}</div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button>
                <Code className="h-4 w-4 mr-2" />
                Verify
              </Button>
              <Button variant="outline">Upload to Device</Button>
              <Button variant="outline">Serial Monitor</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
