import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import type { Metric } from "@/lib/mockAnalysis";
import { motion } from "framer-motion";

interface MetricCardProps {
  metric: Metric;
  index?: number;
}

const MetricCard = ({ metric, index = 0 }: MetricCardProps) => {
  const Icon =
    metric.trend === "up" ? ArrowUpRight : metric.trend === "down" ? ArrowDownRight : Minus;
  const tone =
    metric.trend === "up"
      ? "text-primary bg-primary/10"
      : metric.trend === "down"
      ? "text-accent bg-accent/10"
      : "text-muted-foreground bg-muted";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
      className="rounded-xl border border-border/60 bg-card/70 p-4"
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
            {metric.label}
          </p>
          <p className="font-serif text-2xl text-foreground mt-1">{metric.value}</p>
        </div>
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-medium ${tone}`}>
          <Icon className="h-3 w-3" />
          {metric.delta}
        </span>
      </div>
      {metric.hint && (
        <p className="text-[11px] text-muted-foreground mt-2 italic">{metric.hint}</p>
      )}
    </motion.div>
  );
};

export default MetricCard;
