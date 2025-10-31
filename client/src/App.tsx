import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

// Layout components
import { SidebarProvider, SidebarTrigger, Sidebar } from "@/components/ui/sidebar";
import { ThemeProvider } from "@/components/dashboard/theme-provider";
import { CommandPalette } from "@/components/dashboard/command-palette";
import { AppSidebar } from "@/components/dashboard/app-sidebar";
import { Navbar } from "@/components/dashboard/navbar";
import { MainSidebarContent } from "@/components/MainSidebarContent";

// Pages
import Home from "@/pages/Home";
import Arcanademo from "@/pages/ArcanaDemo";
import Neosyntisdemo from "@/pages/NeosyntisDemo";
import Myntrixdemo from "@/pages/MyntrixDemo";
import NotFound from "@/pages/not-found";
import Auth from "@/pages/Auth";
import VerifyEmail from "@/pages/VerifyEmail";
import ProtectedRoute from "@/components/ProtectedRoute";

// Dashboard Pages
import NotFoundDash from "@/pages/dashboard-pages/not-found";
import Dashboard from "@/pages/dashboard-pages/dashboard";
import Neosyntis from "@/pages/dashboard-pages/neosyntis";
import Myntrix from "@/pages/dashboard-pages/myntrix";
import CognisysPage from "@/pages/dashboard-pages/Cognisys";
import Arcana from "@/pages/dashboard-pages/arcana";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/arcana-demo" component={Arcanademo} />
      <Route path="/neosyntis-demo" component={Neosyntisdemo} />
      <Route path="/myntrix-demo" component={Myntrixdemo} />
      <Route path="/auth" component={Auth} />
      <Route path="/verify-email" component={VerifyEmail} />
      <ProtectedRoute>
        <Route path="/dashboard" component={Dashboard} />
        <Route path="/dashboard/neosyntis" component={Neosyntis} />
        <Route path="/dashboard/myntrix" component={Myntrix} />
        <Route path="/dashboard/cognisys" component={CognisysPage} />
        <Route path="/dashboard/arcana" component={Arcana} />
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
              {location.startsWith("/dashboard") ? (
                <Sidebar> {/* Conditionally rendered Sidebar container */}
                  <AppSidebar />
                </Sidebar>
              ) : (
                <Sidebar> {/* Conditionally rendered Sidebar container */}
                  <MainSidebarContent />
                </Sidebar>
              )}
              <div className="flex flex-col flex-1 overflow-hidden">
                <header className="flex items-center justify-between p-3 border-b bg-card">
                  <SidebarTrigger data-testid="button-sidebar-toggle" />
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
