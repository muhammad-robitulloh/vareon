import { useEffect } from "react";
import { useLocation } from "wouter";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const [, setLocation] = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLocation("/auth");
    }
  }, [setLocation]);

  const token = localStorage.getItem("access_token");

  return token ? <>{children}</> : null; // Render children only if token exists, otherwise null (redirect handled by useEffect)
}
