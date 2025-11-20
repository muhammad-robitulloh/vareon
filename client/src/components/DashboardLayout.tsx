import React from "react";
import { useLocation } from "wouter";
import { SidebarProvider, SidebarTrigger, Sidebar } from '@/components/ui';
import { AppSidebar } from '@/components/dashboard/app-sidebar';
import { Navbar } from '@/components/dashboard/navbar'; // Assuming a separate dashboard Navbar

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [location] = useLocation();

  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  return (
    <SidebarProvider style={style as React.CSSProperties}>
      <div className="flex h-screen w-full overflow-hidden">
        {/* Sidebar */}
        <Sidebar>
          <AppSidebar />
        </Sidebar>

        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Header/Navbar */}
          <header className="flex items-center justify-between p-3 border-b border-border bg-card">
            <SidebarTrigger data-testid="button-sidebar-toggle" />
            <Navbar /> {/* Dashboard specific Navbar */}
          </header>

          {/* Main Content */}
          <main className="flex-1 overflow-auto p-6 bg-background">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
