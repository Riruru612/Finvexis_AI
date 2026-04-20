import { motion } from "framer-motion";
import { departments } from "@/lib/departments";
import { Sparkles, ShieldCheck, BarChart3, Users, Zap } from "lucide-react";

interface AboutSectionProps {
  onOpenDepartment: (id: typeof departments[number]["id"]) => void;
}

const AboutSection = ({ onOpenDepartment }: AboutSectionProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="py-12 md:py-20 max-w-7xl mx-auto"
    >
      <div className="space-y-16">
        {}
        <section className="space-y-6">
          <div className="space-y-3">
            <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary">
              Project Description
            </p>
            <h1 className="font-serif text-4xl md:text-5xl lg:text-6xl text-foreground leading-tight">
              Finvexis AI – A Smart Multi-agent Platform for Finance, Business & Sales
            </h1>
          </div>
          
          <div className="prose prose-editorial max-w-none text-lg text-muted-foreground space-y-5 leading-relaxed">
            <p>
              <strong className="text-foreground font-serif italic text-xl">Finvexis AI</strong> is the intelligent AI-powered platform to manage finance, operations, sales & hiring all at one place for businesses. It utilizes an <span className="text-primary font-medium">Agentic AI system</span>: A new approach of multiple specialized agents, which collaborate under the auspices of one central controller (orchestrator) to address business problems.
            </p>
            <p>
              Today, most businesses use different tools for invoicing, tax calculation, KPI tracking, lead management, and hiring. Because these tools are separate, it becomes difficult to make fast and informed decisions. Finvexis AI solves this problem by combining everything into one intelligent system where AI agents collaborate to provide insights and automation.
            </p>
          </div>
        </section>

        {}
        <div className="grid grid-cols-1 gap-12">
          {}
          <section className="rounded-3xl border border-border/60 bg-card/60 p-8 md:p-10 shadow-elegant">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-xl bg-primary/15 text-primary flex items-center justify-center">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h2 className="font-serif text-3xl text-foreground">1. Finance Agents</h2>
            </div>
            <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
              This section focuses on handling financial tasks and giving smart financial suggestions. It includes:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { t: "Invoice Generator Agent", d: "This automatically generates invoices." },
                { t: "Tax Calculator Agent", d: "Predicts taxes on income and expense." },
                { t: "Investment Risk Agent", d: "Estimates the risk involved in different financial choices." },
                { t: "AI Financial Advisor", d: "Recommends actions to improve budget and financial health." },
              ].map((a) => (
                <div key={a.t} className="p-5 rounded-2xl bg-surface-muted/50 border border-border/40">
                  <h3 className="font-serif text-xl text-foreground mb-2">{a.t}</h3>
                  <p className="text-sm text-muted-foreground">{a.d}</p>
                </div>
              ))}
            </div>
            <p className="mt-8 text-sm italic text-primary/80">
              The agents help business owners make better use of their money, lower the business costs and increase profits.
            </p>
          </section>

          {}
          <section className="rounded-3xl border border-border/60 bg-card/60 p-8 md:p-10 shadow-elegant">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-xl bg-primary/15 text-primary flex items-center justify-center">
                <BarChart3 className="h-5 w-5" />
              </div>
              <h2 className="font-serif text-3xl text-foreground">2. Business Intelligence Agents</h2>
            </div>
            <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
              This section explains why it’s good for companies to know more about how well they’re doing. It includes:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { t: "Business KPI Tracker", d: "A tracker for business key performance indicators including revenue, profit and growth." },
                { t: "Market Research Analyst", d: "Analyzes competitors, market trends and industry patterns." },
                { t: "Forecasting Agent", d: "Predicts future business metrics (revenue, expenses, growth, cash flow) using historical data." },
                { t: "Strategic Recommendation Agent", d: "Analyzes insights from all agents and suggests actionable business decisions to improve performance." },
              ].map((a) => (
                <div key={a.t} className="p-5 rounded-2xl bg-surface-muted/50 border border-border/40">
                  <h3 className="font-serif text-xl text-foreground mb-2">{a.t}</h3>
                  <p className="text-sm text-muted-foreground">{a.d}</p>
                </div>
              ))}
            </div>
            <p className="mt-8 text-sm italic text-primary/80">
              These agents convert raw data into actionable insights, enabling businesses to make more informed decisions.
            </p>
          </section>

          {}
          <section className="rounded-3xl border border-border/60 bg-card/60 p-8 md:p-10 shadow-elegant">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-xl bg-primary/15 text-primary flex items-center justify-center">
                <Users className="h-5 w-5" />
              </div>
              <h2 className="font-serif text-3xl text-foreground">3. Sales & HR Agents</h2>
            </div>
            <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
              This part will also impact hiring and sales processes. It includes:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { t: "Lead Qualification Agent", d: "Ranks potential leads and pinpoints those that are best." },
                { t: "CRM Integration Agent", d: "Consolidates customer information to keep them up-to-date." },
                { t: "Resume Screener", d: "Pre-screens job applicants." },
                { t: "HR Chat Assistant", d: "Answers employee-related questions and policy-based inquiries." },
              ].map((a) => (
                <div key={a.t} className="p-5 rounded-2xl bg-surface-muted/50 border border-border/40">
                  <h3 className="font-serif text-xl text-foreground mb-2">{a.t}</h3>
                  <p className="text-sm text-muted-foreground">{a.d}</p>
                </div>
              ))}
            </div>
          </section>

          {}
          <section className="rounded-3xl border border-border/60 bg-gradient-gold/5 p-8 md:p-10 shadow-elegant border-primary/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-xl bg-primary text-primary-foreground flex items-center justify-center shadow-soft">
                <Zap className="h-5 w-5" />
              </div>
              <h2 className="font-serif text-3xl text-foreground">Independent LLM Integration</h2>
            </div>
            <div className="prose prose-editorial max-w-none text-lg text-muted-foreground space-y-5 leading-relaxed">
              <p>
                Finvexis AI is built on a distributed intelligence architecture. Rather than relying on a single central controller, each of the three departments — <span className="text-foreground font-medium">Finance, Business Intelligence, and Sales & HR</span> — features its own separate, independent LLM integration.
              </p>
              <p>
                This specialized approach ensures that each agent possesses deep, domain-specific reasoning capabilities. By having independent LLM instances, the agents can process complex tasks with higher precision, reduced latency, and expert-level focus within their respective fields.
              </p>
              <p>
                This modular design allows the platform to scale and adapt, providing businesses with highly accurate insights and automation that are tailored to the unique requirements of every department.
              </p>
            </div>
          </section>
        </div>

        {}
        <section className="text-center py-10 space-y-6">
          <div className="h-px w-24 bg-primary/30 mx-auto" />
          <p className="text-xl md:text-2xl font-serif text-foreground leading-relaxed max-w-3xl mx-auto">
            Finvexis AI shows how Agentic AI can go beyond simple chatbots and become a powerful decision-support system. By combining automation, reasoning, and domain expertise, the platform helps businesses reduce manual work and make better, data-driven decisions.
          </p>
          <div className="pt-6">
            <p className="text-sm text-muted-foreground mb-8 uppercase tracking-widest">Get started with a workspace</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {departments.map((d) => {
                const Icon = d.icon;
                return (
                  <button
                    key={d.id}
                    onClick={() => onOpenDepartment(d.id)}
                    className="text-left rounded-2xl border border-border/60 bg-card/70 p-6 hover-lift group"
                  >
                    <div className={`h-11 w-11 rounded-xl ${d.accentBgClass} ${d.accentClass} flex items-center justify-center mb-4`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <p className="font-serif text-xl text-foreground">{d.name}</p>
                    <p className="mt-4 text-[10px] uppercase tracking-wider text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                      Open workspace →
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        </section>
      </div>
    </motion.div>
  );
};

export default AboutSection;
