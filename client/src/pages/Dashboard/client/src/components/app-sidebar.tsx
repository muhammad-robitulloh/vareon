import { useLocation } from 'wouter';
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from '../../../../components/ui/sidebar';
import {
  Layers,
  Search,
  Cpu,
  Network,
  Terminal,
} from 'lucide-react';

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  module: string;
}

const navItems: NavItem[] = [
  { icon: Layers, label: 'VAREON', path: '/dashboard', module: 'vareon' },
  { icon: Search, label: 'NEOSYNTIS', path: '/dashboard/neosyntis', module: 'neosyntis' },
  { icon: Cpu, label: 'MYNTRIX', path: '/dashboard/myntrix', module: 'myntrix' },
  { icon: Network, label: 'COGNISYS', path: '/dashboard/cognisys', module: 'cognisys' },
  { icon: Terminal, label: 'ARCANA', path: '/dashboard/arcana', module: 'arcana' },
];

export function AppSidebar() {
  const [location, setLocation] = useLocation();

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Modules</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const isActive = location === item.path;
                const Icon = item.icon;

                return (
                  <SidebarMenuItem key={item.path}>
                    <SidebarMenuButton
                      isActive={isActive}
                      onClick={() => setLocation(item.path)}
                      data-testid={`link-${item.module}`}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-2 px-4 py-3">
          <div className="h-2 w-2 rounded-full bg-green-500" data-testid="status-indicator-online" />
          <span className="text-xs text-muted-foreground">All Systems Online</span>
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
