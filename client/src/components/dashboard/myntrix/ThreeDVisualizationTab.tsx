import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Sphere, Box, Html } from '@react-three/drei';
import * as THREE from 'three';

interface AgentProps {
  id: string;
  offset: number;
  color: string;
  speed: number;
}

interface DeviceProps {
  id: string;
  position: [number, number, number];
  color: string;
}

// Component for an orbiting agent
function Agent({ id, offset, color, speed }: AgentProps) {
  const ref = useRef<THREE.Mesh>(null!);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed + offset;
    const x = 5 * Math.cos(t);
    const z = 5 * Math.sin(t);
    ref.current.position.set(x, 0, z);
  });

  return (
    <Sphere ref={ref} args={[0.3, 32, 32]}>
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} />
      <Html distanceFactor={10} position={[0, 0.5, 0]} className="text-white text-xs whitespace-nowrap">
        {id}
      </Html>
    </Sphere>
  );
}

// Component for a static device
function Device({ id, position, color }: DeviceProps) {
  return (
    <Box position={position} args={[0.5, 0.5, 0.5]}>
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.2} />
      <Html distanceFactor={10} position={[0, 0.5, 0]} className="text-white text-xs whitespace-nowrap">
        {id}
      </Html>
    </Box>
  );
}

// Main 3D Scene
function Scene() {
  const agents: AgentProps[] = useMemo(() => [
    { id: 'Agent-001', offset: 0, color: '#33a0e8', speed: 0.5 },
    { id: 'Agent-002', offset: Math.PI / 2, color: '#33e885', speed: 0.4 },
    { id: 'Agent-003', offset: Math.PI, color: '#e8335a', speed: 0.6 },
    { id: 'Agent-004', offset: 3 * Math.PI / 2, color: '#e8e233', speed: 0.3 },
  ], []);

  const devices: DeviceProps[] = useMemo(() => [
    { id: 'Device-A', position: [3, 2, -3], color: '#888' },
    { id: 'Device-B', position: [-3, -2, 3], color: '#888' },
    { id: 'Device-C', position: [4, -1, 4], color: '#888' },
  ], []);

  return (
    <>
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={1} />

      {/* Central Core */}
      <Sphere args={[1, 32, 32]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={0.8} roughness={0.2} metalness={0.8} />
        <Html distanceFactor={10} position={[0, 1.3, 0]} className="text-white text-sm whitespace-nowrap">
          MYNTRIX Core
        </Html>
      </Sphere>

      {/* Agents */}
      {agents.map(agent => <Agent key={agent.id} {...agent} />)}

      {/* Devices */}
      {devices.map(device => <Device key={device.id} {...device} />)}

      <OrbitControls enablePan={true} enableZoom={true} enableRotate={true} />

      {/* Add a grid helper for context */}
      <gridHelper args={[20, 20, '#555', '#222']} />
    </>
  );
}

export default function ThreeDVisualizationTab() {
  return (
    <div className="w-full h-[calc(100vh-200px)] bg-gray-900 rounded-lg overflow-hidden">
      <Canvas camera={{ position: [0, 5, 12], fov: 60 }}>
        <Scene />
      </Canvas>
    </div>
  );
}
