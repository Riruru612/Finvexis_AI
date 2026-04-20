import { useState } from "react";
import BackgroundPaths from "@/components/landing/BackgroundPaths";
import LandingNavbar from "@/components/landing/LandingNavbar";
import PremiumLandingHero from "@/components/landing/PremiumLandingHero";
import DepartmentOrbitVisual from "@/components/landing/DepartmentOrbitVisual";
import ProductValueSection from "@/components/landing/ProductValueSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import AboutTeaserSection from "@/components/landing/AboutTeaserSection";
import DashboardPreviewSection from "@/components/landing/DashboardPreviewSection";
import LandingFooter from "@/components/landing/LandingFooter";
import LoginOverlay from "@/components/auth/LoginOverlay";
import AppShell from "@/components/app/AppShell";
import type { AppSection } from "@/components/app/TopNavbar";

const Index = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);
  const [section, setSection] = useState<AppSection>("about");

  const openLogin = () => setLoginOpen(true);

  if (isLoggedIn) {
    return (
      <AppShell
        section={section}
        onChangeSection={setSection}
        onLogout={() => {
          setIsLoggedIn(false);
          setSection("about");
        }}
      />
    );
  }

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="relative min-h-screen bg-background text-foreground selection:bg-primary/20">
      <div className="fixed inset-0 z-0">
        <BackgroundPaths />
      </div>

      <div className="sticky top-0 z-40">
        <LandingNavbar onGetStarted={openLogin} onNavigate={scrollTo} />
      </div>

      <main className="relative z-10 pt-2">
        <section id="hero" className="scroll-mt-20">
          <PremiumLandingHero
            onGetStarted={openLogin}
            onExplore={() => scrollTo("value")}
          />
        </section>

        <section id="value" className="scroll-mt-20">
          <ProductValueSection />
        </section>

        <section id="how-it-works" className="scroll-mt-20">
          <HowItWorksSection />
        </section>

        <section id="preview" className="scroll-mt-20">
          <DashboardPreviewSection />
        </section>

        <section id="about" className="scroll-mt-20">
          <AboutTeaserSection />
        </section>

        <LandingFooter />
      </main>

      <LoginOverlay
        open={loginOpen}
        onClose={() => setLoginOpen(false)}
        onSuccess={() => {
          setLoginOpen(false);
          setIsLoggedIn(true);
        }}
      />
    </div>
  );
};

export default Index;
