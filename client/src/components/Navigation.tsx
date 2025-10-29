import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth"; // Import useAuth hook

export default function Navigation() {
  const [location, setLocation] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isLoggedIn, logout } = useAuth(); // Use the useAuth hook

  const navItems = [
    { path: "/", label: "Home" },
    { path: "/arcana-demo", label: "Arcana AI" },
    { path: "/neosyntis-demo", label: "NEOSYNTIS" },
    { path: "/myntrix-demo", label: "MYNTRIX" },
  ];

  const handleGetStartedClick = () => {
    if (isLoggedIn) {
      setLocation("/dashboard");
    } else {
      setLocation("/auth");
    }
    setMobileMenuOpen(false); // Close mobile menu on click
  };

  const handleLogout = () => {
    logout();
    setMobileMenuOpen(false); // Close mobile menu on logout
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/">
            <a className="flex items-center space-x-2 rounded-lg px-3 py-2 group">
              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary group-hover:animate-pulse-sm">
                <span className="text-sm font-bold text-primary-foreground">V</span>
              </div>
              <span className="text-xl font-bold text-foreground">VAREON</span>
            </a>
          </Link>

          <div className="hidden items-center space-x-1 md:flex">
            {navItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <a
                  className={`relative rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                    location === item.path
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }`}
                >
                  {item.label}
                  {location === item.path && (
                    <span className="absolute inset-x-0 bottom-0 h-0.5 bg-primary animate-grow-x" />
                  )}
                </a>
              </Link>
            ))}
          </div>

          <div className="hidden md:flex md:items-center md:space-x-4">
            {isLoggedIn ? (
              <>
                <Link href="/dashboard">
                  <Button variant="ghost" size="sm">
                    Dashboard
                  </Button>
                </Link>
                <Button size="sm" onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/auth">
                  <Button variant="ghost" size="sm">
                    Sign In
                  </Button>
                </Link>
                <Button size="sm" onClick={handleGetStartedClick} data-testid="button-get-started">
                  Get Started
                </Button>
              </>
            )}
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
                {isLoggedIn ? (
                  <>
                    <Link href="/dashboard">
                      <Button variant="ghost" size="sm" onClick={() => setMobileMenuOpen(false)}>
                        Dashboard
                      </Button>
                    </Link>
                    <Button size="sm" onClick={handleLogout}>
                      Logout
                    </Button>
                  </>
                ) : (
                  <>
                    <Link href="/auth">
                      <Button variant="ghost" size="sm" onClick={() => setMobileMenuOpen(false)}>
                        Sign In
                      </Button>
                    </Link>
                    <Button size="sm" onClick={handleGetStartedClick}>
                      Get Started
                    </Button>
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
