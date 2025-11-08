import { useEffect, useMemo } from 'react';
import { useLocation } from 'wouter';
import { useStore } from '../../lib/dashboard/store';
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui';
import {
  Cpu,
  Network,
  Bot,
  Terminal,
  Database,
  Search,
  Workflow,
  Settings,
  BarChart3,
  FileText,
  Layers,
} from 'lucide-react';

export function CommandPalette() {
  const [, setLocation] = useLocation();
  const { commandPaletteOpen, toggleCommandPalette } = useStore();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        toggleCommandPalette();
      }
    };

    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, [toggleCommandPalette]);

  const commands = useMemo(() => [
    {
      group: 'Modules',
      items: [
        { icon: Layers, label: 'VAREON Dashboard', path: '/dashboard', keywords: 'home dashboard portal' },
        { icon: Search, label: 'NEOSYNTIS Lab', path: '/dashboard/neosyntis', keywords: 'research workflow dataset search' },
        { icon: Cpu, label: 'MYNTRIX Core', path: '/dashboard/myntrix', keywords: 'agents hardware cnc device' },
        { icon: Network, label: 'COGNISYS', path: '/dashboard/cognisys', keywords: 'models routing orchestration' },
        { icon: Terminal, label: 'ARCANA System', path: '/dashboard/arcana', keywords: 'chat ai terminal shell' },
      ],
    },
    {
      group: 'NEOSYNTIS',
      items: [
        { icon: Search, label: 'Search Engine', path: '/dashboard/neosyntis?tab=search', keywords: 'research workflow dataset search' },
        { icon: Database, label: 'Datasets', path: '/dashboard/neosyntis?tab=datasets', keywords: 'data dataset huggingface' },
        { icon: Workflow, label: 'Workflow Builder', path: '/dashboard/neosyntis?tab=workflow', keywords: 'workflow nodes automation' },
        { icon: BarChart3, label: 'Telemetry', path: '/dashboard/neosyntis?tab=telemetry', keywords: 'metrics stats logs' },
        { icon: Settings, label: 'Device Settings', path: '/dashboard/neosyntis?tab=devices', keywords: 'cnc esp32 arduino' },
      ],
    },
    {
      group: 'MYNTRIX',
      items: [
        { icon: Bot, label: 'Agent Manager', path: '/dashboard/myntrix?tab=agents', keywords: 'agents ai bots' },
        { icon: Workflow, label: 'Task Scheduler', path: '/dashboard/myntrix?tab=scheduler', keywords: 'tasks schedule cron' },
        { icon: Cpu, label: 'Device Control', path: '/dashboard/myntrix?tab=devices', keywords: 'device cnc 3d hardware' },
        { icon: BarChart3, label: 'Resource Monitor', path: '/dashboard/myntrix?tab=monitor', keywords: 'cpu memory resources' },
      ],
    },
    {
      group: 'Actions',
      items: [
        { icon: Bot, label: 'Start New Chat', path: '/dashboard/arcana?action=new-chat', keywords: 'chat conversation' },
        { icon: Terminal, label: 'Open Terminal', path: '/dashboard/arcana?tab=terminal', keywords: 'shell command line' },
        { icon: FileText, label: 'Create Workflow', path: '/dashboard/neosyntis?tab=workflow&action=new', keywords: 'workflow create new' },
        { icon: Settings, label: 'Settings', path: '/dashboard/settings', keywords: 'settings preferences config' },
      ],
    },
  ], []);

  const handleSelect = (path: string) => {
    setLocation(path);
    toggleCommandPalette();
  };

  return (
    <CommandDialog open={commandPaletteOpen} onOpenChange={toggleCommandPalette}>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        {commands.map((group) => (
          <CommandGroup key={group.group} heading={group.group}>
            {group.items.map((item) => (
              <CommandItem
                key={item.path}
                value={`${item.label} ${item.keywords}`}
                onSelect={() => handleSelect(item.path)}
                data-testid={`command-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <item.icon className="mr-2 h-4 w-4" />
                <span>{item.label}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        ))}
      </CommandList>
    </CommandDialog>
  );
}
