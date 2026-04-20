import { motion } from "framer-motion";
import MetricCard from "./MetricCard";
import { AlertTriangle, Lightbulb, TrendingUp } from "lucide-react";
import type { DepartmentAnalysis } from "@/lib/mockAnalysis";

interface AnalysisCardsProps {
  analysis: DepartmentAnalysis;
  rich?: boolean; 
}

const Sparkline = ({ data }: { data: number[] }) => {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const span = Math.max(1, max - min);
  const w = 600;
  const h = 120;
  const step = w / (data.length - 1);
  const pts = data
    .map((v, i) => `${i * step},${h - ((v - min) / span) * (h - 16) - 8}`)
    .join(" ");
  const area = `M0,${h} L${pts} L${w},${h} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-28">
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="hsl(40 65% 60%)" stopOpacity="0.45" />
          <stop offset="100%" stopColor="hsl(40 65% 60%)" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#trendFill)" />
      <polyline points={pts} stroke="hsl(40 60% 50%)" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};

const severityTone: Record<string, string> = {
  high: "bg-destructive/10 text-destructive border-destructive/20",
  medium: "bg-accent/10 text-accent border-accent/20",
  low: "bg-olive/10 text-olive border-olive/20",
};

const AnalysisCards = ({ analysis, rich }: AnalysisCardsProps) => {
  return (
    <div className="space-y-5">
      {}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl border border-border/60 bg-gradient-editorial p-5"
      >
        <p className="text-[10px] uppercase tracking-[0.18em] text-primary mb-2">
          Executive summary
        </p>
        <p className="text-foreground/90 leading-relaxed text-pretty">{analysis.summary}</p>
      </motion.div>

      {}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {analysis.metrics.map((m, i) => (
          <MetricCard key={m.label} metric={m} index={i} />
        ))}
      </div>

      {rich && (
        <div className="rounded-2xl border border-border/60 bg-card/70 p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="text-sm text-foreground">Trend · 24 periods</span>
            </div>
            <span className="text-xs text-muted-foreground">Synthesized from upload</span>
          </div>
          <Sparkline data={analysis.trend} />
        </div>
      )}

      {}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {analysis.insights.map((insight, i) => (
          <motion.div
            key={insight.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="rounded-xl border border-border/60 bg-card/70 p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-primary" />
              <p className="text-xs uppercase tracking-wider text-muted-foreground">
                Insight {i + 1}
              </p>
            </div>
            <p className="font-serif text-base text-foreground">{insight.title}</p>
            <p className="text-sm text-muted-foreground mt-1.5 leading-relaxed">
              {insight.body}
            </p>
          </motion.div>
        ))}
      </div>

      {}
      <div className="rounded-2xl border border-border/60 bg-card/70 p-5">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle className="h-4 w-4 text-accent" />
          <p className="text-sm text-foreground">Anomalies worth attention</p>
        </div>
        <ul className="space-y-2">
          {analysis.anomalies.map((a, i) => (
            <li
              key={i}
              className={`flex items-start gap-3 rounded-lg border px-3 py-2.5 ${severityTone[a.severity]}`}
            >
              <span className="text-[10px] uppercase tracking-wider mt-0.5 font-semibold">
                {a.severity}
              </span>
              <span className="text-sm text-foreground/90">{a.message}</span>
            </li>
          ))}
        </ul>
      </div>

      {rich && (
        <div className="rounded-2xl border border-border/60 bg-card/70 p-5">
          <p className="text-sm text-foreground mb-3">Forecast preview</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {analysis.forecast.map((f) => (
              <div key={f.period} className="rounded-xl bg-surface-muted/70 p-4 border border-border/40">
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{f.period}</p>
                <p className="font-serif text-xl text-foreground mt-0.5">{f.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{f.note}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisCards;
