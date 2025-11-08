import { ThemeToggle } from "@/components/dashboard/theme-provider";
import {
  SidebarContent,
  SidebarFooter,
} from '@/components/ui';

export function MainSidebarContent() {
  return (
    <>
      <SidebarContent>
        {/* Add any other main sidebar content here if needed */}
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center justify-center p-3 border-t">
          <ThemeToggle />
        </div>
      </SidebarFooter>
    </>
  );
}