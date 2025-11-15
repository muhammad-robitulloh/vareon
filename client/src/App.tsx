import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster, TooltipProvider, SidebarProvider, SidebarTrigger, Sidebar } from '@/components/ui';
import { ThemeProvider } from "@/components/dashboard/theme-provider";
import { CommandPalette } from "@/components/dashboard/command-palette";
import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { Navbar } from "@/components/dashboard/navbar";
import { MainSidebarContent, ProtectedRoute } from '@/components';

import {
  Home,
  ArcanaDemo,
  NeosyntisDemo,
  MyntrixDemo,
  NotFound,
    Auth,
    VerifyEmail,
    WaitingForVerification,
    PricingPage, // Import the new PricingPage
  } from '@/pages';
  
  
  import {
    NotFound as NotFoundDash,
    Dashboard,
    Neosyntis,
    Myntrix,
    Cognisys as CognisysPage,
    Arcana,
    UserProfile, // Import UserProfile
  } from '@/pages/dashboard-pages';
  
  function Router() {
    return (
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/arcana-demo" component={ArcanaDemo} />
        <Route path="/neosyntis-demo" component={NeosyntisDemo} />
        <Route path="/myntrix-demo" component={MyntrixDemo} />
        <Route path="/auth" component={Auth} />
        <Route path="/verify-email" component={VerifyEmail} />
        <Route path="/waiting-for-verification" component={WaitingForVerification} />
        <ProtectedRoute>
          <Route path="/pricing" component={PricingPage} /> {/* Add the new pricing route */}
          <Route path="/dashboard" component={Dashboard} />
          <Route path="/dashboard/neosyntis" component={Neosyntis} />
          <Route path="/dashboard/myntrix" component={Myntrix} />
          <Route path="/dashboard/cognisys" component={CognisysPage} />
          <Route path="/dashboard/arcana" component={Arcana} />
          <Route path="/dashboard/profile" component={UserProfile} /> {/* New User Profile Route */}
        </ProtectedRoute>
     <Route component={NotFound} />
      </Switch>
    );
  }
  export default function App() {
  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  const [location] = useLocation();

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <SidebarProvider style={style as React.CSSProperties}>
            <div className="flex h-screen w-full">
              {location.startsWith("/dashboard") && ( // Only render sidebar if on a dashboard route
                <Sidebar>
                  <AppSidebar />
                </Sidebar>
              )}
              <div className="flex flex-col flex-1 overflow-hidden">
                <header className="flex items-center justify-between p-3 border-b bg-card">
                  {location.startsWith("/dashboard") && ( // Only show sidebar toggle on dashboard routes
                    <SidebarTrigger data-testid="button-sidebar-toggle" />
                  )}
                  <div className="flex items-center gap-2">
                    {/* ThemeToggle removed from here */}
                  </div>
                </header>
                <main className="flex-1 overflow-auto">
                  <Router />
                </main>
              </div>
            </div>
          </SidebarProvider>
          <CommandPalette />
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
