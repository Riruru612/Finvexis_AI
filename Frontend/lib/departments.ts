import {
  TrendingUp,
  BarChart3,
  Users,
  type LucideIcon,
} from "lucide-react";

export type DepartmentId = "finance" | "bi" | "sales-hr";

export interface DepartmentConfig {
  id: DepartmentId;
  name: string;
  shortName: string;
  tagline: string;
  description: string;
  icon: LucideIcon;
  accentClass: string;        
  accentBgClass: string;      
  ringClass: string;          
  promptPlaceholder: string;
  reportTitle: string;
}

export const departments: DepartmentConfig[] = [
  {
    id: "finance",
    name: "Finance",
    shortName: "Finance",
    tagline: "Capital intelligence for confident decisions",
    description:
      "Reconcile, forecast, and pressure-test your financial position with agents trained on real business mechanics.",
    icon: TrendingUp,
    accentClass: "text-accent",
    accentBgClass: "bg-accent/10",
    ringClass: "ring-accent/30",
    promptPlaceholder: "Ask about cash flow, margins, or budget variance…",
    reportTitle: "Finance Insight Report",
  },
  {
    id: "bi",
    name: "Business Intelligence",
    shortName: "Business Intelligence",
    tagline: "See your business in one place",
    description:
      "KPI synthesis, anomaly detection, and forecasts that translate raw data into a clear strategic picture.",
    icon: BarChart3,
    accentClass: "text-primary",
    accentBgClass: "bg-primary/10",
    ringClass: "ring-primary/30",
    promptPlaceholder: "Ask about KPIs, trends, anomalies, or forecasts…",
    reportTitle: "Business Intelligence Report",
  },
  {
    id: "sales-hr",
    name: "Sales & HR",
    shortName: "Sales & HR",
    tagline: "Pipeline and people, working in concert",
    description:
      "Pipeline health, conversion patterns, attrition signals and headcount planning — analyzed together.",
    icon: Users,
    accentClass: "text-olive",
    accentBgClass: "bg-olive/10",
    ringClass: "ring-olive/30",
    promptPlaceholder: "Ask about pipeline, churn, retention, or hiring…",
    reportTitle: "Sales & HR Insight Report",
  },
];

export const getDepartment = (id: DepartmentId) =>
  departments.find((d) => d.id === id)!;
