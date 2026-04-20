import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface LandingNavbarProps {
  onGetStarted: () => void;
  onNavigate: (id: string) => void;
}

const LandingNavbar = ({ onGetStarted, onNavigate }: LandingNavbarProps) => {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 glass-strong w-full">
      <div className="w-full px-4 md:px-8 lg:px-12 flex h-16 items-center justify-between gap-4">
        <button
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="flex items-center gap-2 group"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-gold shadow-soft">
            <Sparkles className="h-4 w-4 text-primary-foreground" />
          </span>
          <span className="font-serif text-lg text-foreground tracking-tight">
            Finvexis<span className="text-primary"> AI</span>
          </span>
        </button>

        <nav className="hidden md:flex items-center gap-1">
          <NavButton onClick={() => onNavigate("hero")} label="Home" />
          <NavButton onClick={() => onNavigate("value")} label="Value" />
          <NavButton onClick={() => onNavigate("how-it-works")} label="Process" />
          <NavButton onClick={() => onNavigate("about")} label="About" />
        </nav>

        <div className="flex items-center gap-4">
          <Button
            onClick={onGetStarted}
            size="sm"
            className="bg-gradient-gold text-primary-foreground shadow-soft hover:opacity-95 hover-lift px-6"
          >
            Login
          </Button>
        </div>
      </div>
    </header>
  );
};

const NavButton = ({ onClick, label }: { onClick: () => void; label: string }) => (
  <button
    onClick={onClick}
    className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors relative group"
  >
    {label}
    <span className="absolute bottom-1.5 left-4 right-4 h-0.5 bg-primary/40 scale-x-0 group-hover:scale-x-100 transition-transform origin-left" />
  </button>
);

export default LandingNavbar;
