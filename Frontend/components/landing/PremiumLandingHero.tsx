import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { departments } from "@/lib/departments";

interface PremiumLandingHeroProps {
  onGetStarted: () => void;
  onExplore: () => void;
}

const PremiumLandingHero = ({ onGetStarted, onExplore }: PremiumLandingHeroProps) => {
  return (
    <section className="relative w-full min-h-[calc(100vh-64px)] flex items-center pt-8 pb-12 md:pt-10 md:pb-16 overflow-hidden">
      <div className="w-full px-4 md:px-12 lg:px-20 relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
        {}
        <div className="lg:col-span-6 space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="inline-flex items-center gap-2 rounded-full glass px-4 py-1.5 text-xs font-medium text-secondary"
          >
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            Multi-agent business intelligence
            <span className="mx-1 h-1 w-1 rounded-full bg-primary/60" />
            Prototype
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-serif text-5xl md:text-6xl lg:text-7xl leading-[1.02] text-foreground text-balance"
          >
            Turn raw data into{" "}
            <span className="italic text-gradient-amber">decisions</span>{" "}
            <br className="hidden md:block" />
            your business{" "}
            <span className="text-gradient-gold">can act on.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="max-w-xl text-lg md:text-xl text-muted-foreground leading-relaxed text-pretty"
          >
            Finvexis AI brings finance, intelligence and people analytics into one
            elegant workspace — analyze a file, generate a report, then ask the
            assistant anything.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.32, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-wrap items-center gap-4 pt-2"
          >
            <Button
              size="lg"
              onClick={onGetStarted}
              className="h-12 px-7 bg-gradient-gold text-primary-foreground hover:opacity-95 shadow-elegant hover-lift group"
            >
              Let's Get Started
              <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={onExplore}
              className="h-12 px-7 glass hover:bg-surface transition-colors hover-lift"
            >
              Explore the Ecosystem
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.6 }}
            className="flex items-center gap-6 pt-4 text-xs text-muted-foreground"
          >
            <span className="editorial-rule">Built for executive clarity</span>
            <span className="hidden sm:inline">•</span>
            <span className="hidden sm:inline">Frontend prototype — production system arrives later</span>
          </motion.div>
        </div>

        {}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
          className="lg:col-span-6 relative"
        >
          <div className="absolute -inset-10 bg-gradient-amber opacity-15 blur-[100px] rounded-full" />
          
          <div className="relative space-y-6">
            <div className="text-left space-y-2 mb-4">
              <p className="editorial-rule text-[10px] uppercase tracking-[0.22em] text-primary">
                The ecosystem
              </p>
              <h2 className="font-serif text-3xl md:text-4xl text-foreground">
                One platform.{" "}
                <span className="italic text-gradient-gold text-pretty">Three intelligences.</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 gap-3">
              {departments.map((dept, i) => {
                const Icon = dept.icon;
                return (
                  <motion.div
                    key={dept.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.6 + i * 0.1 }}
                    className="group relative rounded-2xl glass-strong p-4 shadow-elegant ring-1 ring-border/40 hover-lift transition-all hover:ring-primary/30"
                  >
                    <div className="flex items-center gap-4">
                      <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${dept.accentBgClass} ${dept.accentClass} shadow-soft flex-shrink-0 group-hover:scale-110 transition-transform duration-500`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div>
                        <p className="font-serif text-lg text-foreground leading-tight group-hover:text-primary transition-colors">{dept.name}</p>
                        <p className="text-sm text-muted-foreground mt-0.5 line-clamp-1">
                          {dept.tagline}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.2 }}
              className="flex items-center gap-3 pt-2"
            >
              <div className="h-px flex-1 bg-border/40" />
              <div className="inline-flex items-center gap-2 rounded-full glass px-4 py-1.5 shadow-soft border border-border/40">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                <span className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground font-medium">
                  Unified by Finvexis AI
                </span>
              </div>
              <div className="h-px flex-1 bg-border/40" />
            </motion.div>
          </div>
        </motion.div>
      </div>

      {}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full pointer-events-none -z-10 overflow-hidden">
        <div className="absolute top-1/2 left-1/4 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 blur-[120px] rounded-full" />
        <div className="absolute top-1/2 right-1/4 -translate-y-1/2 w-[500px] h-[500px] bg-accent/5 blur-[120px] rounded-full" />
      </div>
    </section>
  );
};

export default PremiumLandingHero;
