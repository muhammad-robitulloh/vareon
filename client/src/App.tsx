import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster, TooltipProvider } from '@/components/ui';
import { ThemeProvider } from "@/components/dashboard/theme-provider";
import { CommandPalette } from "@/components/dashboard/command-palette";

import AppLayout from "./components/AppLayout";
import { Helmet } from "react-helmet-async";
import DashboardRoutes from "./components/DashboardRoutes"; // Import DashboardRoutes
import { AnimatePresence, motion } from "framer-motion"; // Import AnimatePresence and motion

import {
  Home,
  ArcanaDemo,
  NeosyntisDemo,
  MyntrixDemo,
  NotFound,
  Auth,
  VerifyEmail,
  WaitingForVerification,
} from '@/pages';
  
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
        <Route path="/dashboard/:rest*" component={DashboardRoutes} />
        <Route path="/pricing" component={DashboardRoutes} />
        <Route component={NotFound} />
      </Switch>
    );
  }
  export default function App() {
  const [location] = useLocation(); // Get current location for AnimatePresence key

  const pageVariants = {
    initial: { opacity: 0, x: 50 },
    in: { opacity: 1, x: 0 },
    out: { opacity: 0, x: -50 }
  };

  const pageTransition = {
    type: "tween",
    ease: "anticipate",
    duration: 0.4
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Helmet
        titleTemplate="%s | VAREON"
        defaultTitle="VAREON - Engineering Adaptive Intelligence"
      >
        <meta name="description" content="Vareon is an advanced platform to build, manage, and orchestrate multi-agent AI systems. Connect, automate, and visualize your agentic workflows." />
      </Helmet>
      <ThemeProvider>
        <TooltipProvider>
          <AppLayout>
            <AnimatePresence mode="wait">
              <motion.div
                key={location}
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
                className="h-full w-full"
              >
                <Router />
              </motion.div>
            </AnimatePresence>
          </AppLayout>
          <CommandPalette />
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

