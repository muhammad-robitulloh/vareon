import { useLocation } from 'wouter';
import { cn } from '@/lib/utils';
import { useStore } from '../lib/store';
import {
  Layers,
  Search,
  Cpu,
  Network,
  Terminal,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  module: string;
}

const navItems: NavItem[] = [
  { icon: Layers, label: 'VAREON', path: '/', module: 'vareon' },
  { icon: Search, label: 'NEOSYNTIS', path: '/neosyntis', module: 'neosyntis' },
  { icon: Cpu, label: 'MYNTRIX', path: '/myntrix', module: 'myntrix' },
  { icon: Network, label: 'COGNISYS', path: '/cognisys', module: 'cognisys' },
  { icon: Terminal, label: 'ARCANA', path: '/arcana', module: 'arcana' },
];

export function Sidebar() {
  const [location, setLocation] = useLocation();
  const { sidebarCollapsed, toggleSidebar } = useStore();

  return (
    <aside
      className={cn(
        'h-full bg-sidebar border-r flex flex-col transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-56'
      )}
    >
      <div className="flex items-center justify-between p-3 border-b">
        {!sidebarCollapsed && (
          <span className="font-semibold text-sm text-sidebar-foreground">Modules</span>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="h-8 w-8"
          data-testid="button-sidebar-toggle"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {navItems.map((item) => {
          const isActive = location === item.path;
          const Icon = item.icon;

          const button = (
            <Button
              key={item.path}
              variant={isActive ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3',
                sidebarCollapsed && 'justify-center px-0'
              )}
              onClick={() => setLocation(item.path)}
              data-testid={`link-${item.module}`}
            >
              <Icon className="h-4 w-4" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </Button>
          );

          if (sidebarCollapsed) {
            return (
              <Tooltip key={item.path} delayDuration={0}>
                <TooltipTrigger asChild>
                  {button}
                </TooltipTrigger>
                <TooltipContent side="right">
                  {item.label}
                </TooltipContent>
              </Tooltip>
            );
          }

          return button;
        })}
      </nav>

      <div className="p-3 border-t">
        <div className={cn(
          'flex items-center gap-2',
          sidebarCollapsed && 'justify-center'
        )}>
          <div className={cn(
            'h-2 w-2 rounded-full bg-green-500',
            sidebarCollapsed && 'h-3 w-3'
          )} />
          {!sidebarCollapsed && (
            <span className="text-xs text-muted-foreground">All Systems Online</span>
          )}
        </div>
      </div>
    </aside>
  );
}
