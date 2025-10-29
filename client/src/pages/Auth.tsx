import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import AuthForm from "@/components/AuthForm";

export default function Auth() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navigation />
      <main className="flex-grow flex items-center justify-center py-12">
        <AuthForm />
      </main>
      <Footer />
    </div>
  );
}
