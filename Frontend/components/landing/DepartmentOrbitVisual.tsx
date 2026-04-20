import { motion } from "framer-motion";
import { departments } from "@/lib/departments";
import { Sparkles } from "lucide-react";

interface DepartmentOrbitVisualProps {
  onSelect: () => void;
}

const DepartmentOrbitVisual = ({ onSelect }: DepartmentOrbitVisualProps) => {
  return (
    <section className="relative py-12 md:py-16">
      <div className="container relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary mb-4">
            The ecosystem
          </p>
          <h2 className="font-serif text-4xl md:text-5xl text-foreground text-balance">
            One platform.{" "}
            <span className="italic text-gradient-gold">Three intelligences.</span>
          </h2>
          <p className="mt-4 text-muted-foreground text-pretty">
            Each department is a specialized agent — connected to the same
            understanding of your business.
          </p>
        </div>

        {}
        <div className="relative mx-auto max-w-6xl">
          {}
          <svg
            viewBox="0 0 1200 160"
            className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-40 w-full hidden md:block pointer-events-none"
            fill="none"
            aria-hidden
            preserveAspectRatio="none"
          >
            <defs>
              <linearGradient id="connector-line" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="hsl(40 60% 58%)" stopOpacity="0" />
                <stop offset="20%" stopColor="hsl(40 60% 58%)" stopOpacity="0.55" />
                <stop offset="80%" stopColor="hsl(40 60% 58%)" stopOpacity="0.55" />
                <stop offset="100%" stopColor="hsl(40 60% 58%)" stopOpacity="0" />
              </linearGradient>
            </defs>
            <motion.path
              d="M 0 80 C 250 30, 450 130, 600 80 S 950 30, 1200 80"
              stroke="url(#connector-line)"
              strokeWidth="1.5"
              strokeDasharray="3 7"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.6, ease: "easeInOut" }}
            />
          </svg>

          <div className="relative grid grid-cols-1 md:grid-cols-3 gap-5 md:gap-8">
            {departments.map((dept, i) => {
              const Icon = dept.icon;
              return (
                <motion.button
                  key={dept.id}
                  type="button"
                  onClick={onSelect}
                  initial={{ opacity: 0, y: 18 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.15 + i * 0.12, ease: [0.16, 1, 0.3, 1] }}
                  whileHover={{ y: -8 }}
                  className="group text-left"
                >
                  <div className="relative h-full rounded-2xl glass-strong p-6 shadow-card hover-lift cursor-pointer ring-1 ring-border/40 transition-all duration-500 group-hover:ring-primary/30 group-hover:shadow-elegant">
                    <div
                      className={`inline-flex h-11 w-11 items-center justify-center rounded-xl ${dept.accentBgClass} ${dept.accentClass} mb-4 group-hover:scale-110 group-hover:rotate-3 transition-transform duration-500 shadow-soft`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <p className="font-serif text-xl text-foreground group-hover:text-primary transition-colors duration-300">{dept.name}</p>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed group-hover:text-foreground/80 transition-colors duration-300">
                      {dept.tagline}
                    </p>
                  </div>
                </motion.button>
              );
            })}
          </div>

          {}
          <div className="mt-10 flex justify-center">
            <div className="inline-flex items-center gap-2 rounded-full glass-strong px-4 py-2 shadow-soft">
              <Sparkles className="h-3.5 w-3.5 text-primary" />
              <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                Unified by Finvexis AI
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DepartmentOrbitVisual;
