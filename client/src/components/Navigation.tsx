import { Link, useLocation } from "wouter";
import { Button } from '@/components/ui';
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth"; // Import useAuth hook
import { AnimatePresence, motion } from "framer-motion"; // Import framer-motion

export default function Navigation() {
  const [location, setLocation] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { isLoggedIn, logout } = useAuth(); // Use the useAuth hook

  const navItems = [
    { path: "/", label: "Home" },
    { path: "/arcana-demo", label: "Arcana AI" },
    { path: "/neosyntis-demo", label: "NEOSYNTIS" },
    { path: "/myntrix-demo", label: "MYNTRIX" },
    { path: "/dashboard", label: "Dashboard" },
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
    <nav className="w-full">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <Link href="/">
            <a className="flex items-center space-x-2 rounded-lg py-2 group">
              <motion.div
                className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary"
                whileHover={{ scale: 1.1 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <span className="text-xl font-bold text-primary-foreground">V</span>
              </motion.div>
              <span className="text-2xl font-extrabold text-foreground text-glow">VAREON</span>
            </a>
          </Link>

          <div className="hidden items-center space-x-4 md:flex">
            {navItems.map((item) => (
              <Link key={item.path} href={item.path}>
                <motion.a
                  className="relative px-3 py-2 text-sm font-medium transition-colors duration-200 text-muted-foreground hover:text-primary"
                  whileHover={{ color: "hsl(var(--primary))" }}
                >
                  {item.label}
                  {location === item.path && (
                    <motion.span
                      layoutId="underline"
                      className="absolute inset-x-0 bottom-0 h-0.5 bg-primary rounded-full"
                      initial={{ scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                </motion.a>
              </Link>
            ))}
          </div>

          <div className="hidden md:flex md:items-center md:space-x-4">
            {isLoggedIn ? (
              <>
                <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-foreground">
                  Logout
                </Button>
                <Link href="/dashboard">
                  <Button size="sm" className="bg-primary text-primary-foreground hover:bg-primary/90">
                    Dashboard
                  </Button>
                </Link>
              </>
            ) : (
              <>
                <Link href="/auth">
                  <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                    Sign In
                  </Button>
                </Link>
                <Button size="sm" onClick={handleGetStartedClick} data-testid="button-get-started" className="bg-primary text-primary-foreground hover:bg-primary/90">
                  Get Started
                </Button>
              </>
            )}
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden text-muted-foreground hover:text-foreground"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="button-mobile-menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>

        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="border-t border-border py-4 md:hidden"
            >
              <div className="flex flex-col space-y-2">
                {navItems.map((item) => (
                  <Link key={item.path} href={item.path}>
                    <a
                      className="rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground hover:bg-muted/50 hover:text-foreground"
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
                        <Button variant="ghost" size="sm" onClick={() => setMobileMenuOpen(false)} className="w-full justify-start text-muted-foreground hover:text-foreground">
                          Dashboard
                        </Button>
                      </Link>
                      <Button size="sm" onClick={handleLogout} className="w-full justify-start bg-primary text-primary-foreground hover:bg-primary/90">
                        Logout
                      </Button>
                    </>
                  ) : (
                    <>
                      <Link href="/auth">
                        <Button variant="ghost" size="sm" onClick={() => setMobileMenuOpen(false)} className="w-full justify-start text-muted-foreground hover:text-foreground">
                          Sign In
                        </Button>
                      </Link>
                      <Button size="sm" onClick={handleGetStartedClick} className="w-full justify-start bg-primary text-primary-foreground hover:bg-primary/90">
                        Get Started
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
}
