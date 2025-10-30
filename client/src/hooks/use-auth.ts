import { useState, useEffect } from "react";
import { useLocation } from "wouter";

interface AuthState {
  isLoggedIn: boolean;
  token: string | null;
  // You might want to add user info here later, e.g., user: { id: string; username: string; email: string } | null;
}

export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>({
    isLoggedIn: false,
    token: null,
  });
  const [, setLocation] = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setAuthState({
        isLoggedIn: true,
        token: token,
      });
    } else {
      setAuthState({
        isLoggedIn: false,
        token: null,
      });
    }
  }, [setLocation]);

  const login = (token: string) => {
    localStorage.setItem("access_token", token);
    setAuthState({
      isLoggedIn: true,
      token: token,
    });
    setLocation("/dashboard");
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setAuthState({
      isLoggedIn: false,
      token: null,
    });
    setLocation("/"); // Redirect to home page after logout
  };

  return { ...authState, login, logout };
}
