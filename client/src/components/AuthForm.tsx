import { useState } from "react";
import { Button, Input, Card, CardContent, CardHeader, CardTitle, CardDescription, Label } from '@/components/ui';
import { Mail, User, Lock, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";

const API_BASE_URL = ""; // Define your API base URL

export default function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { toast } = useToast();
  const [, setLocation] = useLocation();

  const loginMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await fetch(`${API_BASE_URL}/api/token`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }
      return response.json();
    },
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      toast({
        title: "Login Successful",
        description: "You have been logged in.",
        variant: "success",
      });
      setLocation("/dashboard"); // Redirect to dashboard
    },
    onError: (error: any) => {
      toast({
        title: "Login Failed",
        description: error.message || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (userData: { email: string; username: string; password: string }) => {
      const response = await fetch(`${API_BASE_URL}/api/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Registration failed");
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Registration Successful",
        description: "Please check your email to verify your account.",
        variant: "success",
      });
      setLocation("/waiting-for-verification"); // Redirect to waiting for verification page
    },
    onError: (error: any) => {
      toast({
        title: "Registration Failed",
        description: error.message || "An unexpected error occurred.",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isLogin) {
      const formData = new FormData();
      formData.append("username", email); // Backend expects 'username' for email in OAuth2PasswordRequestForm
      formData.append("password", password);
      loginMutation.mutate(formData);
    } else {
      registerMutation.mutate({ email, username, password });
    }
  };

  const isLoading = loginMutation.isPending || registerMutation.isPending;

  return (
    <Card className="w-full max-w-md mx-auto bg-card/80 backdrop-blur-sm border-primary/20 shadow-lg">
      <CardHeader className="text-center">
        <CardTitle className="text-3xl font-bold">{isLogin ? "Welcome Back" : "Create Account"}</CardTitle>
        <CardDescription>{isLogin ? "Sign in to access your dashboard" : "Get started with VAREON"}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="pl-10"
            />
          </div>
          
          <div className={`transition-all duration-300 ease-in-out ${isLogin ? 'max-h-0 opacity-0 overflow-hidden' : 'max-h-20 opacity-100'}`}>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                id="username"
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required={!isLogin}
                className="pl-10"
              />
            </div>
          </div>

          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              id="password"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="pl-10"
            />
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? <Loader2 className="animate-spin" /> : (isLogin ? "Login" : "Sign Up")}
          </Button>
          
          <p className="text-center text-sm text-muted-foreground">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <Button
              variant="link"
              className="pl-1"
              onClick={() => setIsLogin(!isLogin)}
              type="button"
            >
              {isLogin ? "Sign Up" : "Login"}
            </Button>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}
