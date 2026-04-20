import type { DepartmentId } from "./departments";

export interface Metric {
  label: string;
  value: string;
  delta: string;
  trend: "up" | "down" | "flat";
  hint?: string;
}

export interface Insight {
  title: string;
  body: string;
}

export interface Anomaly {
  severity: "low" | "medium" | "high";
  message: string;
}

export interface DepartmentAnalysis {
  summary: string;
  metrics: Metric[];
  insights: Insight[];
  anomalies: Anomaly[];
  forecast: { period: string; value: string; note: string }[];
  reportBody: string;
  trend: number[]; 
  rawResults?: any; 
}

const baseTrend = (seed: number) =>
  Array.from({ length: 24 }, (_, i) =>
    Math.round(40 + Math.sin(i / 2.2 + seed) * 14 + i * 1.6 + (i % 5) * 2)
  );

export const mockAnalyses: Record<DepartmentId, DepartmentAnalysis> = {
  finance: {
    summary:
      "Independent Finance LLM has processed your ledger and tax history. We've detected a 12% opportunity in tax optimization and flagged 4 high-risk investment profiles in your current portfolio.",
    metrics: [
      { label: "Predicted Tax", value: "$42.1K", delta: "-12.4%", trend: "up", hint: "Optimized via Tax Agent" },
      { label: "Invoice Health", value: "98.2%", delta: "+2.1%", trend: "up" },
      { label: "Risk Exposure", value: "Moderate", delta: "-5 pts", trend: "up", hint: "Investment Risk Agent" },
      { label: "Budget Accuracy", value: "94.8%", delta: "+3.2%", trend: "up" },
    ],
    insights: [
      { title: "Tax Optimization detected", body: "The Tax Calculator Agent identified deductible expenses in your operational costs that were previously unclassified. Potential savings: $14,200." },
      { title: "Invoice Automation success", body: "The Invoice Generator Agent has cleared the 30-day backlog. 98% of outgoing invoices are now automated and tracked." },
      { title: "Financial Advisor Recommendation", body: "Reallocate 15% of your cash reserves into low-risk treasury bonds to improve your long-term financial health score." },
    ],
    anomalies: [
      { severity: "high", message: "Investment Risk Agent flagged a high-volatility outlier in your Q3 capital allocation." },
      { severity: "medium", message: "Tax Calculator detected a potential compliance gap in international vendor payments." },
    ],
    forecast: [
      { period: "Next Quarter", value: "$1.2M Cash", note: "Predicted after tax optimization" },
      { period: "Year End", value: "$4.8M Assets", note: "Based on Financial Advisor's growth strategy" },
      { period: "Tax Liability", value: "$165K", note: "Estimated total for FY" },
    ],
    reportBody:
      "FINANCE AGENT REPORT\n\nFinvexis Finance LLM analyzed your uploaded financial documents. The system has successfully generated invoices, calculated tax liabilities, and estimated investment risks.\n\n- Tax Calculator: Identified $14.2K in potential tax savings.\n- Invoice Generator: Automated 98% of current billing cycles.\n- Investment Risk: Flagged high-volatility capital allocation in Q3.\n- AI Financial Advisor: Recommends 15% cash reallocation for portfolio stability.",
    trend: baseTrend(1.2),
  },
  bi: {
    summary:
      "Independent BI LLM has analyzed market patterns and competitor trends. Strategic recommendations are ready, focusing on a 22% growth potential in the mid-market segment.",
    metrics: [
      { label: "Market Share", value: "14.2%", delta: "+2.1%", trend: "up" },
      { label: "Competitor Gap", value: "-4.2%", delta: "-1.1%", trend: "up", hint: "Market Research Agent" },
      { label: "Forecast Accuracy", value: "97.1%", delta: "+0.8%", trend: "up" },
      { label: "Strategy Score", value: "88/100", delta: "+12", trend: "up" },
    ],
    insights: [
      { title: "Competitor Pattern Detected", body: "The Market Research Analyst identified a shift in competitor pricing for mid-market clients. Our current strategy is 8% underpriced for this value." },
      { title: "Growth Forecast Updated", body: "The Forecasting Agent predicts a 22% increase in revenue for the next 6 months based on historical historical patterns and market signals." },
      { title: "Strategic Recommendation", body: "Pivot marketing spend towards 'Expert-led' content to capitalize on the emerging trend in executive decision support." },
    ],
    anomalies: [
      { severity: "high", message: "Forecasting Agent detected a significant outlier in industry growth that may impact your Q4 supply chain." },
      { severity: "medium", message: "Market Research Analyst flagged a new competitor entry in the EU sector." },
    ],
    forecast: [
      { period: "Next 6 Months", value: "+22% Rev", note: "High confidence forecast" },
      { period: "Market Gap", value: "$450K", note: "Potential revenue from segment pivot" },
      { period: "FY Growth", value: "$15.4M", note: "Strategic base case" },
    ],
    reportBody:
      "BUSINESS INTELLIGENCE REPORT\n\nThe BI system has analyzed market patterns and competitor trends. Strategic recommendations are ready, focusing on a 22% growth potential in the mid-market segment.\n\n- KPI Tracker: Revenue and market share trending above baseline.\n- Market Analyst: Platform is currently undervalued by 8% relative to competitors.\n- Forecasting: High confidence in a 22% growth spurt over the next 6 months.\n- Strategic Agent: Recommends content-led pivot to capture executive attention.",
    trend: baseTrend(2.7),
  },
  "sales-hr": {
    summary:
      "Independent Sales & HR LLM has qualified 142 leads and screened 84 job applicants. Lead conversion is predicted to rise, and HR policy compliance is at 100%.",
    metrics: [
      { label: "Lead Quality", value: "High", delta: "+14%", trend: "up", hint: "Qualification Agent" },
      { label: "CRM Sync Health", value: "100%", delta: "Stable", trend: "flat" },
      { label: "Applicant Fit", value: "82%", delta: "+6%", trend: "up", hint: "Resume Screener" },
      { label: "HR Query Res", value: "1.2s", delta: "-0.4s", trend: "up" },
    ],
    insights: [
      { title: "Lead Qualification Breakthrough", body: "The Lead Qualification Agent has identified a 'Power User' cohort in your CRM that is 4x more likely to convert." },
      { title: "Resume Screener efficiency", body: "Screened 84 applicants for the Engineering lead role; 12 have been prioritized for immediate interview based on tech-stack match." },
      { title: "HR Policy Insights", body: "The HR Chat Assistant has resolved 142 policy inquiries this week with 98% user satisfaction and zero escalation." },
    ],
    anomalies: [
      { severity: "medium", message: "CRM Integration Agent flagged a data duplication risk in the Sales pipeline." },
      { severity: "low", message: "Resume Screener detected a shortage of senior-level candidates in the current applicant pool." },
    ],
    forecast: [
      { period: "Sales Bookings", value: "$2.1M", note: "Predicted from High Quality leads" },
      { period: "Headcount", value: "+12", note: "Based on current screener priority" },
      { period: "Lead Conv", value: "31%", note: "Target for next 30 days" },
    ],
    reportBody:
      "SALES & HR INSIGHT REPORT\n\nSales & HR analysis complete. Leads have been ranked, applicants screened, and HR policy support automated.\n\n- Lead Qualification: Identified 'Power User' leads with 4x conversion probability.\n- CRM Integration: Pipeline data synchronized; duplication risks addressed.\n- Resume Screener: 12 top-tier candidates prioritized for Engineering roles.\n- HR Assistant: Policy inquiry resolution automated with high satisfaction.",
    trend: baseTrend(4.1),
  },
};

export const generateAssistantReply = (
  deptId: DepartmentId,
  question: string,
  fileName?: string,
): string => {
  const a = mockAnalyses[deptId];
  const q = question.toLowerCase().trim();
  const ctx = fileName ? ` Based on ${fileName},` : "";

  if (q.includes("summary") || q.includes("overall") || q.includes("tl;dr")) {
    return `${ctx ? ctx.trim() + " " : ""}${a.summary}`;
  }
  if (q.includes("risk") || q.includes("anomal")) {
    const top = a.anomalies[0];
    return `The most important risk to flag right now: ${top.message} I would treat this as ${top.severity} severity and address it before next reporting cycle.`;
  }
  if (q.includes("forecast") || q.includes("predict") || q.includes("project")) {
    return `${ctx} the base-case forecast is ${a.forecast[0].value} for ${a.forecast[0].period} (${a.forecast[0].note}). The trajectory holds if leading indicators stay within current bands.`;
  }
  if (q.includes("recommend") || q.includes("action") || q.includes("do")) {
    return `Three actions I would prioritize: (1) ${a.insights[0].title.toLowerCase()} — ${a.insights[0].body} (2) ${a.insights[1].title.toLowerCase()}. (3) Re-review in 14 days against the same KPIs.`;
  }
  if (q.includes("metric") || q.includes("kpi") || q.includes("number")) {
    return `Top-line metrics from this report:\n• ${a.metrics
      .map((m) => `${m.label}: ${m.value} (${m.delta})`)
      .join("\n• ")}`;
  }
  return `${ctx} here is a focused take: ${a.insights[0].body} If you want, I can go deeper on a specific metric, segment, or time window.`;
};
