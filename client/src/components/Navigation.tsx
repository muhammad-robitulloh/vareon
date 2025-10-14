import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { useState } from "react";

export default function Navigation() {
  const [location] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: "/", label: "Home" },
    { path: "/neuronet", label: "NeuroNet AI" },
    { path: "/neosyntis", label: "NEOSYNTIS" },
    { path: "/myntrix", label: "MYNTRIX" },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/">
            <a className="flex items-center space-x-2 hover-elevate active-elevate-2 rounded-lg px-3 py-2">
              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary">
                <span className="text-sm font-bold text-primary-foreground">V</span>
              </div>
              <span className="text-xl font-bold text-foreground">VAREON</span>
            </a>
          </Link>

          <div className="hidden items-center space-x-1 md:flex">
            {navItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <a
                  className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors hover-elevate active-elevate-2 ${
                    location === item.path
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {item.label}
                </a>
              </Link>
            ))}
          </div>

          <div className="hidden md:flex md:items-center md:space-x-4">
            <Button variant="ghost" size="sm">
              Sign In
            </Button>
            <Button size="sm" data-testid="button-get-started">
              Get Started
            </Button>
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="button-mobile-menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        {mobileMenuOpen && (
          <div className="border-t border-border py-4 md:hidden">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => (
                <Link key={item.path} href={item.path}>
                  <a
                    className={`rounded-lg px-4 py-2 text-sm font-medium hover-elevate active-elevate-2 ${
                      location === item.path
                        ? "text-primary"
                        : "text-muted-foreground"
                    }`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {item.label}
                  </a>
                </Link>
              ))}
              <div className="flex flex-col space-y-2 pt-4">
                <Button variant="ghost" size="sm">
                  Sign In
                </Button>
                <Button size="sm">Get Started</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
