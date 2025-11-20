import Hero from "@/components/Hero";
import DivisionsSection from "@/components/DivisionsSection";
import ArchitectureFlow from "@/components/ArchitectureFlow";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Hero />
      <DivisionsSection />
      <ArchitectureFlow />
    </div>
  );
}
