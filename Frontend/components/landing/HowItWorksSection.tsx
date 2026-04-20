import { motion } from "framer-motion";
import { Upload, Cpu, FileText, MessagesSquare } from "lucide-react";

const steps = [
  { icon: Upload, label: "Upload", body: "Drop a CSV, PDF, XLSX, JSON or DOCX." },
  { icon: Cpu, label: "Analyze", body: "Department agent reads, structures and reasons over your file." },
  { icon: FileText, label: "Report", body: "A clean, downloadable insight report with recommendations." },
  { icon: MessagesSquare, label: "Ask", body: "Follow-up questions become available in the assistant." },
];

const HowItWorksSection = () => {
  return (
    <section className="relative py-8 md:py-10">
      <div className="w-full px-4 md:px-12 lg:px-20 relative z-10">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary mb-4">
            The flow
          </p>
          <h2 className="font-serif text-4xl md:text-5xl text-foreground text-balance">
            Four steps from{" "}
            <span className="italic text-gradient-gold">file to decision.</span>
          </h2>
        </div>

        <div className="relative">
          {}
          <div className="absolute top-7 left-0 right-0 h-px bg-gradient-to-r from-transparent via-border to-transparent hidden md:block" />

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 md:gap-3">
            {steps.map((s, i) => {
              const Icon = s.icon;
              return (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="relative text-center px-2 group"
                >
                  <div className="relative mx-auto h-14 w-14 rounded-full glass-strong shadow-card flex items-center justify-center text-primary group-hover:scale-110 group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-500">
                    <Icon className="h-5 w-5" />
                    <span className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-foreground text-background text-[10px] font-medium flex items-center justify-center group-hover:bg-accent group-hover:text-accent-foreground transition-colors">
                      {i + 1}
                    </span>
                  </div>
                  <h3 className="font-serif text-xl mt-5 text-foreground group-hover:text-primary transition-colors">{s.label}</h3>
                  <p className="text-sm text-muted-foreground mt-2 leading-relaxed max-w-[18rem] mx-auto group-hover:text-foreground/80 transition-colors">
                    {s.body}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
