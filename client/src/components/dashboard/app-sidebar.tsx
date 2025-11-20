import { useLocation } from 'wouter';
import { useState } from 'react';
import {
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
} from '@/components/ui';
import {
  Layers,
  Search,
  Cpu,
  Network,
  Terminal,
  User,
  CreditCard, // Import the CreditCard icon
  CommandIcon, // Import CommandIcon icon for CLI
  Code, // Import Code icon for Aura
  Gem, // Import Gem icon for Nexa
} from 'lucide-react';
import { UsageCreditBar } from './UsageCreditBar'; // Add this line

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  module: string;
}

const navItems: NavItem[] = [
  { icon: Search, label: 'NEOSYNTIS', path: '/dashboard/neosyntis', module: 'neosyntis' },
  { icon: Cpu, label: 'MYNTRIX', path: '/dashboard/myntrix', module: 'myntrix' },
  { icon: Network, label: 'COGNISYS', path: '/dashboard/cognisys', module: 'cognisys' },
];

export function AppSidebar() {
  const [location, setLocation] = useLocation();
  const [isDeveloper, setIsDeveloper] = useState(true); // Mock state for developer license

  return (
    <>
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

        <SidebarGroup>
          <SidebarGroupLabel>Arcana Tools</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton
                  isActive={location === '/dashboard/arcana'}
                  onClick={() => setLocation('/dashboard/arcana')}
                  data-testid="link-arcana"
                >
                  <Terminal className="h-4 w-4" />
                  <span>ARCANA</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  isActive={location === '/dashboard/arcana/cli'}
                  onClick={() => setLocation('/dashboard/arcana/cli')}
                  data-testid="link-arcana-cli"
                >
                  <CommandIcon className="h-4 w-4" />
                  <span>Arcana CLI</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {isDeveloper && (
          <SidebarGroup>
            <SidebarGroupLabel>Developer Tools</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    isActive={location === '/dashboard/aura'}
                    onClick={() => setLocation('/dashboard/aura')}
                    data-testid="link-aura"
                  >
                    <Code className="h-4 w-4" />
                    <span>AURA (SDK)</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    isActive={location === '/dashboard/nexa'}
                    onClick={() => setLocation('/dashboard/nexa')}
                    data-testid="link-nexa"
                  >
                    <Gem className="h-4 w-4" />
                    <span>NEXA (Rewards)</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}
      </SidebarContent>
            <SidebarFooter>
              <UsageCreditBar currentCredit={750} maxCredit={1000} lowCreditThreshold={200} />
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    isActive={location === '/pricing'}
                    onClick={() => setLocation('/pricing')}
                    data-testid="link-pricing"
                  >
                    <CreditCard className="h-4 w-4" />
                    <span>Pricing</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
                <SidebarMenuItem>
                  <SidebarMenuButton
                    isActive={location === '/dashboard/profile'}
                    onClick={() => setLocation('/dashboard/profile')}
                    data-testid="link-user-profile"
                  >
                    <User className="h-4 w-4" />
                    <span>User Profile</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
              <div className="flex items-center gap-2 px-4 py-3">
                <div className="h-2 w-2 rounded-full bg-green-500" data-testid="status-indicator-online" />
                <span className="text-xs text-muted-foreground">All Systems Online</span>
              </div>
            </SidebarFooter>
          </>
        );
      }
      