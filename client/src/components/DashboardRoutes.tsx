import { Route, Switch } from "wouter";
import { ProtectedRoute } from "@/components";
import DashboardLayout from "@/components/DashboardLayout";
import {
  NotFound as NotFoundDash,
  Dashboard,
  Neosyntis,
  Myntrix,
  Cognisys,
  Arcana,
  UserProfile,
} from '@/pages/dashboard-pages';
import { AuraPage, NexaPage, PricingPage } from "@/pages"; // Import non-dashboard pages that use DashboardLayout
import ArcanaCliManager from "@/components/dashboard/ArcanaCliManager";

export default function DashboardRoutes() {
  return (
    <ProtectedRoute>
      <DashboardLayout>
        <Switch>
          <Route path="/pricing" component={PricingPage} />
          <Route path="/dashboard" component={Dashboard} />
          <Route path="/dashboard/neosyntis" component={Neosyntis} />
          <Route path="/dashboard/myntrix" component={Myntrix} />
          <Route path="/dashboard/cognisys" component={Cognisys} />
          <Route path="/dashboard/arcana" component={Arcana} />
          <Route path="/dashboard/arcana/cli" component={ArcanaCliManager} />
          <Route path="/dashboard/profile" component={UserProfile} />
          <Route path="/dashboard/aura" component={AuraPage} />
          <Route path="/dashboard/nexa" component={NexaPage} />
          <Route component={NotFoundDash} /> {/* Dashboard specific 404 */}
        </Switch>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
