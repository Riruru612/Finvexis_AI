import { motion } from "framer-motion";
import { TrendingUp, FileText, MessagesSquare, Sparkles } from "lucide-react";

const DashboardPreviewSection = () => {
  return (
    <section className="relative py-8 md:py-10">
      <div className="container relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary mb-4">
            A glimpse
          </p>
          <h2 className="font-serif text-4xl md:text-5xl text-foreground text-balance">
            Inside the{" "}
            <span className="italic text-gradient-gold">workspace</span>.
          </h2>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="relative mx-auto max-w-7xl"
        >
          <div className="absolute -inset-6 bg-gradient-amber opacity-20 blur-3xl rounded-full pointer-events-none" />
          <div className="relative rounded-3xl glass-strong shadow-elegant p-5 md:p-7">
            <div className="flex items-center justify-between pb-4 border-b border-border/60">
              <div className="flex items-center gap-3">
                <div className="h-2.5 w-2.5 rounded-full bg-accent/70" />
                <div className="h-2.5 w-2.5 rounded-full bg-primary/60" />
                <div className="h-2.5 w-2.5 rounded-full bg-olive/60" />
                <span className="ml-3 text-xs text-muted-foreground">finvexis.ai · Business Intelligence</span>
              </div>
              <span className="text-[11px] uppercase tracking-wider text-primary">Report ready</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-5">
              {}
              <div className="lg:col-span-7 space-y-5">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { l: "MRR", v: "$1.07M", d: "+4.8%" },
                    { l: "Accounts", v: "2,184", d: "+126" },
                    { l: "NPS", v: "62", d: "+5" },
                    { l: "Churn", v: "1.9%", d: "+0.3pp" },
                  ].map((m) => (
                    <div key={m.l} className="rounded-xl bg-surface-muted/70 p-3.5 border border-border/40 hover-lift group/kpi">
                      <p className="text-[10px] uppercase tracking-wider text-muted-foreground group-hover/kpi:text-primary transition-colors">{m.l}</p>
                      <p className="font-serif text-xl text-foreground mt-0.5 group-hover/kpi:scale-105 origin-left transition-transform">{m.v}</p>
                      <p className="text-xs text-accent mt-0.5">{m.d}</p>
                    </div>
                  ))}
                </div>

                {}
                <div className="rounded-2xl border border-border/50 bg-card/70 p-5 hover-lift transition-all duration-500 hover:ring-1 hover:ring-primary/20">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-primary animate-pulse" />
                      <span className="text-sm text-foreground">Revenue trajectory · 24 weeks</span>
                    </div>
                    <span className="text-xs text-muted-foreground">Base case</span>
                  </div>
                  <svg viewBox="0 0 600 160" className="w-full h-36">
                    <defs>
                      <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="hsl(40 65% 60%)" stopOpacity="0.45" />
                        <stop offset="100%" stopColor="hsl(40 65% 60%)" stopOpacity="0" />
                      </linearGradient>
                    </defs>
                    <motion.path
                      d="M0,130 C40,120 80,90 120,95 S200,60 240,70 S320,40 360,52 S440,28 480,38 S560,24 600,18 L600,160 L0,160 Z"
                      fill="url(#areaFill)"
                      initial={{ opacity: 0 }}
                      whileInView={{ opacity: 1 }}
                      transition={{ duration: 1.5 }}
                    />
                    <motion.path
                      d="M0,130 C40,120 80,90 120,95 S200,60 240,70 S320,40 360,52 S440,28 480,38 S560,24 600,18"
                      stroke="hsl(40 60% 50%)"
                      strokeWidth="2"
                      fill="none"
                      initial={{ pathLength: 0 }}
                      whileInView={{ pathLength: 1 }}
                      transition={{ duration: 2, ease: "easeInOut" }}
                    />
                  </svg>
                </div>
              </div>

              {}
              <div className="lg:col-span-5 space-y-5">
                <div className="rounded-2xl border border-border/50 bg-card/70 p-5 hover-lift transition-all duration-500 hover:ring-1 hover:ring-primary/20">
                  <div className="flex items-center gap-2 mb-3">
                    <FileText className="h-4 w-4 text-primary" />
                    <span className="text-sm text-foreground">Insight report</span>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    MRR is accelerating in the mid-market. Three anomalies worth executive attention; recommended actions on page two.
                  </p>
                  <button className="mt-4 inline-flex items-center gap-2 rounded-lg bg-gradient-gold text-primary-foreground px-4 py-2 text-xs font-medium shadow-soft hover-lift hover:opacity-95">
                    Download report
                  </button>
                </div>

                <div className="rounded-2xl border border-border/50 bg-card/70 p-5 hover-lift transition-all duration-500 hover:ring-1 hover:ring-primary/20">
                  <div className="flex items-center gap-2 mb-3">
                    <MessagesSquare className="h-4 w-4 text-primary" />
                    <span className="text-sm text-foreground">Assistant</span>
                  </div>
                  <div className="space-y-3">
                    <motion.div 
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 }}
                      className="rounded-xl bg-surface-muted/80 px-3.5 py-2.5 text-sm max-w-[85%]"
                    >
                      What is driving the small churn uptick?
                    </motion.div>
                    <motion.div 
                      initial={{ opacity: 0, x: 10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1.2 }}
                      className="ml-auto rounded-xl bg-primary/10 text-foreground px-3.5 py-2.5 text-sm max-w-[90%]"
                    >
                      <Sparkles className="inline h-3.5 w-3.5 text-primary mr-1.5 -mt-0.5" />
                      Support volume on the EU cluster led the trend by ~2 weeks. I'd start there.
                    </motion.div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default DashboardPreviewSection;
