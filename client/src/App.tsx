import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Home from "@/pages/Home";
import Arcanademo from "@/pages/ArcanaDemo";
import Neosyntisdemo from "@/pages/NeosyntisDemo";
import Myntrixdemo from "@/pages/MyntrixDemo";
import NotFound from "@/pages/not-found";
import Auth from "@/pages/Auth";
import VerifyEmail from "@/pages/VerifyEmail";
import DashboardRouter from "@/pages/Dashboard/client/src/DashboardRouter";
import ProtectedRoute from "@/components/ProtectedRoute"; // Import ProtectedRoute

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/arcana-demo" component={Arcanademo} />
      <Route path="/neosyntis-demo" component={Neosyntisdemo} />
      <Route path="/myntrix-demo" component={Myntrixdemo} />
      <Route path="/auth" component={Auth} />
      <Route path="/verify-email" component={VerifyEmail} />
      <Route path="/dashboard">
        <ProtectedRoute>
          <DashboardRouter />
        </ProtectedRoute>
      </Route>
      <Route component={NotFound} />
    </Switch>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}
