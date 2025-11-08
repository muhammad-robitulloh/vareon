import { Button, Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui';
import { useLocation } from "wouter";

export default function WaitingForVerification() {
  const [, setLocation] = useLocation();

  const handleBackToLogin = () => {
    setLocation("/auth");
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center py-12">
      <Card className="w-full max-w-md mx-auto bg-card/80 backdrop-blur-sm border-primary/20 shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold">Check Your Email</CardTitle>
          <CardDescription>
            A verification link has been sent to your email address. Please click the link in the email to verify your account and complete your registration.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col items-center space-y-4">
          <Button onClick={handleBackToLogin} className="w-full">
            Back to Login
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
