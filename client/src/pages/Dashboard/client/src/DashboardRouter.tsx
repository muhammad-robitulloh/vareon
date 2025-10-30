import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "./components/ui/toaster";
import { TooltipProvider } from "./components/ui/tooltip";
import { SidebarProvider, SidebarTrigger } from "./components/ui/sidebar";
import { ThemeProvider, ThemeToggle } from "./components/theme-provider";
import { CommandPalette } from "./components/command-palette";
import { AppSidebar } from "./components/app-sidebar";
import { Navbar } from "./components/navbar";
import NotFound from "./pages/not-found";
import Dashboard from "./pages/dashboard";
import Neosyntis from "./pages/neosyntis";
import Myntrix from "./pages/myntrix";
import CognisysPage from "./pages/Cognisys";
import Arcana from "./pages/arcana";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/neosyntis" component={Neosyntis} />
      <Route path="/myntrix" component={Myntrix} />
      <Route path="/cognisys" component={CognisysPage} />
      <Route path="/arcana" component={Arcana} />
      <Route component={NotFound} />
    </Switch>
  );
}

export default function DashboardRouter() {
  const style = {
    "--sidebar-width": "16rem",
    "--sidebar-width-icon": "3rem",
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <SidebarProvider style={style as React.CSSProperties}>
            <div className="flex h-screen w-full">
              <AppSidebar />
              <div className="flex flex-col flex-1 overflow-hidden">
                <header className="flex items-center justify-between p-3 border-b bg-card">
                  <SidebarTrigger data-testid="button-sidebar-toggle" />
                  <div className="flex items-center gap-2">
                    <ThemeToggle />
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


