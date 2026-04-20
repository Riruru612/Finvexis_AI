import { motion } from "framer-motion";
import { LogOut, Menu, Sparkles, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

export type AppSection = "about" | "finance" | "bi" | "sales-hr";

const navItems: { id: AppSection; label: string }[] = [
  { id: "about", label: "About" },
  { id: "finance", label: "Finance" },
  { id: "bi", label: "Business Intelligence" },
  { id: "sales-hr", label: "Sales & HR" },
];

interface TopNavbarProps {
  active: AppSection;
  onChange: (s: AppSection) => void;
  onLogout: () => void;
}

const TopNavbar = ({ active, onChange, onLogout }: TopNavbarProps) => {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 glass-strong w-full">
      <div className="w-full px-4 md:px-8 lg:px-12 flex h-16 items-center justify-between gap-4">
        {}
        <button
          onClick={() => onChange("about")}
          className="flex items-center gap-2 group"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-gold shadow-soft">
            <Sparkles className="h-4 w-4 text-primary-foreground" />
          </span>
          <span className="font-serif text-lg text-foreground tracking-tight">
            Finvexis<span className="text-primary"> AI</span>
          </span>
        </button>

        {}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = item.id === active;
            return (
              <button
                key={item.id}
                onClick={() => onChange(item.id)}
                className="relative px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                <span className={isActive ? "text-foreground" : ""}>{item.label}</span>
                {isActive && (
                  <motion.span
                    layoutId="nav-underline"
                    className="absolute left-3 right-3 -bottom-0.5 h-[2px] bg-gradient-gold rounded-full"
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                  />
                )}
              </button>
            );
          })}
        </nav>

        {}
        <div className="hidden md:flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-full bg-surface-muted px-3 py-1.5 border border-border/60">
            <div className="h-6 w-6 rounded-full bg-gradient-amber" />
            <span className="text-xs text-foreground">Operator</span>
          </div>
          <Button variant="ghost" size="sm" onClick={onLogout} className="text-muted-foreground hover:text-foreground">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>

        {}
        <button
          className="md:hidden rounded-lg p-2 text-foreground"
          onClick={() => setOpen((s) => !s)}
          aria-label="Toggle navigation"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {}
      {open && (
        <div className="md:hidden border-t border-border/60 bg-card/90 backdrop-blur">
          <div className="container py-3 flex flex-col gap-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onChange(item.id);
                  setOpen(false);
                }}
                className={`text-left px-3 py-2.5 rounded-lg text-sm ${
                  active === item.id
                    ? "bg-primary/10 text-foreground"
                    : "text-muted-foreground hover:bg-surface-muted"
                }`}
              >
                {item.label}
              </button>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={onLogout}
              className="justify-start text-muted-foreground mt-2"
            >
              <LogOut className="h-4 w-4 mr-2" /> Log out
            </Button>
          </div>
        </div>
      )}
    </header>
  );
};

export default TopNavbar;
export { navItems };
