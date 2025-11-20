import { Search, Bell } from 'lucide-react';
import { ThemeToggle } from './theme-provider';
import { useStore } from '@/lib/dashboard/store';
import { Button, Input, Badge, Avatar, AvatarFallback, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui';
import { motion } from "framer-motion";

export function Navbar() {
  const { toggleCommandPalette, performanceMode, togglePerformanceMode } = useStore();

  return (
    <nav className="h-14 flex items-center justify-between px-4 gap-4" data-testid="navbar">
      <div className="flex items-center gap-4 flex-1">
        <div className="flex items-center gap-2" data-testid="logo">
          <motion.div
            className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center font-mono font-bold text-sm"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
            data-testid="logo-icon"
          >
            <span className="text-primary-foreground text-lg">V</span>
          </motion.div>
          <span className="font-extrabold text-xl hidden sm:inline text-foreground text-glow" data-testid="logo-text">VAREON</span>
        </div>

        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" data-testid="icon-search" />
          <Input
            placeholder="Search or press Ctrl+K..."
            className="pl-9 cursor-pointer"
            onClick={toggleCommandPalette}
            readOnly
            data-testid="input-global-search"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-card px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100" data-testid="kbd-shortcut">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {performanceMode && (
          <Badge variant="outline" className="hidden sm:inline-flex" data-testid="badge-performance-mode">
            Performance Mode
          </Badge>
        )}

        <Button
          variant="ghost"
          size="icon"
          className="relative"
          data-testid="button-notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-primary" data-testid="notification-dot" />
        </Button>

        <ThemeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="relative h-9 w-9 rounded-full"
              data-testid="button-user-menu"
            >
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-primary" data-testid="avatar-initials">
                  AD
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel data-testid="menu-label">My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem data-testid="menu-profile">
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem data-testid="menu-settings">
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={togglePerformanceMode}
              data-testid="menu-performance-mode"
            >
              {performanceMode ? 'Disable' : 'Enable'} Performance Mode
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive" data-testid="menu-logout">
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </nav>
  );
}
