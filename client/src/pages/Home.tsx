import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import DivisionsSection from "@/components/DivisionsSection";
import ArchitectureFlow from "@/components/ArchitectureFlow";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <Hero />
      <DivisionsSection />
      <ArchitectureFlow />
      <Footer />
    </div>
  );
}
