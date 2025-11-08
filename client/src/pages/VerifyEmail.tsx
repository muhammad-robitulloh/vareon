import { useState, useEffect } from "react";
import { Button, Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui';
import { Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { useLocation } from "wouter";

const API_BASE_URL = ""; // Assuming API is served from the same origin

export default function VerifyEmail() {
  const [location, setLocation] = useLocation();
  const [emailFromUrl, setEmailFromUrl] = useState<string | null>(null);
  const [tokenFromUrl, setTokenFromUrl] = useState<string | null>(null);
  const { toast } = useToast();

  const verifyEmailMutation = useMutation({
    mutationFn: async ({ email, token }: { email: string; token: string }) => {
      const response = await fetch(`${API_BASE_URL}/api/verify-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, token }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Verification failed.");
      }
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Success!",
        description: data.message || "Email verified successfully.",
        variant: "default",
      });
      // No immediate redirect, button will change to 'Back to Login'
    },
    onError: (error: any) => {
      toast({
        title: "Verification Failed",
        description: error.message || "An error occurred during verification.",
        variant: "destructive",
      });
    },
  });

  useEffect(() => {
    const queryString = window.location.search.substring(1); // Get query string without '?'
    const params = new URLSearchParams(queryString || "");
    const email = params.get("email");
    const token = params.get("token");

    setEmailFromUrl(email);
    setTokenFromUrl(token);

    if (!email || !token) {
      toast({
        title: "Invalid Link",
        description: "The verification link is missing required parameters.",
        variant: "destructive",
      });
    }
  }, [location, toast]);

  const handleBackToLogin = () => {
    setLocation("/auth");
  };

  const handleVerifyEmail = () => {
    if (emailFromUrl && tokenFromUrl) {
      verifyEmailMutation.mutate({ email: emailFromUrl, token: tokenFromUrl });
    } else {
      toast({
        title: "Error",
        description: "Cannot verify: email or token is missing.",
        variant: "destructive",
      });
    }
  };

  const renderButton = () => {
    if (verifyEmailMutation.isPending) {
      return (
        <Button className="w-full" disabled>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Verifying...
        </Button>
      );
    } else if (verifyEmailMutation.isSuccess) {
      return (
        <Button onClick={handleBackToLogin} className="w-full">
          Back to Login
        </Button>
      );
    } else if (emailFromUrl && tokenFromUrl) {
      return (
        <Button onClick={handleVerifyEmail} className="w-full">
          Verify Email
        </Button>
      );
    } else {
      return (
        <Button onClick={handleBackToLogin} className="w-full">
          Back to Login
        </Button>
      );
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center py-12">
      <Card className="w-full max-w-md mx-auto bg-card/80 backdrop-blur-sm border-primary/20 shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">
            Email Verification
          </CardTitle>
          <CardDescription>
            {verifyEmailMutation.isPending
              ? "Verifying your email address..."
              : verifyEmailMutation.isSuccess
              ? "Your email has been successfully verified!"
              : verifyEmailMutation.isError
              ? "There was an issue verifying your email. Please try again or request a new link."
              : "Click the button below to verify your email address."}
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          {renderButton()}
        </CardContent>
      </Card>
    </div>
  );
}