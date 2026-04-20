import { motion } from "framer-motion";
import { useEffect, useCallback } from "react";
import { useWorkspaceState } from "@/hooks/useWorkspaceState";
import type { DepartmentConfig } from "@/lib/departments";
import { mockAnalyses } from "@/lib/mockAnalysis";
import StatusBadge from "./StatusBadge";
import FileDropzone from "./FileDropzone";
import AnalysisCards from "./AnalysisCards";
import ReportCard from "./ReportCard";
import ChatPanel from "./ChatPanel";
import { Loader2, AlertCircle, TrendingUp, Target, PieChart as PieIcon, ShieldAlert, Users, Zap, Search, Globe, Award, TrendingDown, ArrowUpRight, BarChart3, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { DepartmentAnalysis } from "@/lib/mockAnalysis";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, BarChart, Bar, Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface DepartmentWorkspaceProps {
  dept: DepartmentConfig;
  rich?: boolean;
}

const DepartmentWorkspace = ({ dept, rich }: DepartmentWorkspaceProps) => {
  const ws = useWorkspaceState();
  const Icon = dept.icon;

  const runAnalysis = useCallback(async (file: File) => {
    if (dept.id !== "bi" && dept.id !== "finance") {
      
      ws.setStatus("analyzing");
      setTimeout(() => ws.setStatus("generating"), 800);
      setTimeout(() => ws.setStatus("complete"), 2000);
      return;
    }

    try {
      ws.setStatus("analyzing");
      ws.setError(null);

      const formData = new FormData();
      formData.append("file", file);
      
      if (dept.id === "bi") {
        formData.append("use_llm", "true");
        const response = await fetch("/api/business/analyze", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error(`Analysis failed: ${response.statusText}`);
        const data = await response.json();
        const results = data.analysis_results;

        
        const agentSummary = `**BUSINESS INTELLIGENCE REPORT**

**1. EXECUTIVE SUMMARY**

${(results.strategy?.executive_summary || results.strategy?.summary || 'The BI Department\'s independent LLM has synthesized raw data into actionable strategic insights.').replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')}

**2. KPI AGENT ANALYSIS (Business Health)**

**2.1 Revenue & Growth:**

- Revenue: $${(results.kpi?.metrics?.revenue / 1000).toFixed(1)}K (${results.kpi?.metrics?.rev_growth}% ${results.kpi?.metrics?.rev_growth_status})
- Net Margin: ${results.kpi?.metrics?.net_margin}% (Profit efficiency indicator)
- Expense Growth: ${results.kpi?.metrics?.efficiency?.Operating_Leverage > 1 ? 'Healthy (Revenue scaling faster than expenses)' : 'Warning (Expenses scaling faster than revenue)'}

**2.2 Unit Economics:**

- CAC: $${results.kpi?.metrics?.cac} (Customer Acquisition Cost)
- LTV: $${results.kpi?.metrics?.ltv} (Projected Lifetime Value)
- LTV/CAC Ratio: ${(results.kpi?.metrics?.ltv / results.kpi?.metrics?.cac).toFixed(2)}x
- ROMI: ${results.kpi?.metrics?.romi}% (Return on Marketing Investment)

**2.3 Customer & Efficiency:**

- Retention: ${results.kpi?.metrics?.retention}% (Churn: ${results.kpi?.metrics?.churn}%)
- Burn Rate: $${(results.kpi?.metrics?.expenses / 1000).toFixed(1)}K / mo
- Runway: ${results.kpi?.metrics?.efficiency?.Runway_Months} months
- Operating Leverage: ${results.kpi?.metrics?.efficiency?.Operating_Leverage}x

**2.4 Expense Breakdown:**

${Object.entries(results.kpi?.metrics?.expense_breakdown || {}).map(([k, v]: [string, any]) => `- ${k.replace(/_/g, ' ')}: $${typeof v === 'number' ? (v / 1000).toFixed(1) + 'K' : v}`).join('\n')}

**3. MARKET AGENT ANALYSIS (Competitive Intel)**

**3.1 Positioning & Price:**

- Price Index: ${results.market?.metrics?.price_index} (1.0 = Market Avg)
- Positioning Score: ${results.market?.metrics?.positioning_score}/100
- Market Position: ${results.market?.position}

**3.2 Market Share (TAM/SAM):**

- TAM: ${results.market?.market_intelligence?.TAM}
- SAM: ${results.market?.market_intelligence?.SAM}
- Current Share: ${results.market?.metrics?.market_share}%

**3.3 SWOT Analysis:**

- Strengths: ${(results.market?.swot?.strengths || []).join(', ')}
- Weaknesses: ${(results.market?.swot?.weaknesses || []).join(', ')}
- Opportunities: ${(results.market?.swot?.opportunities || []).join(', ')}
- Threats: ${(results.market?.swot?.threats || []).join(', ')}

**3.4 Competitive Landscape:**

- Feature Coverage: ${results.market?.competitive_analysis?.our_feature_coverage}
- Top Pain Point: ${results.market?.market_intelligence?.Top_Pain_Point}

**4. FORECASTING AGENT (Predictive)**

- Realistic Forecast: $${(results.forecast?.scenarios?.realistic / 1000).toFixed(1)}K (Confidence: ${results.forecast?.confidence}%)
- Scenarios: Best Case $${(results.forecast?.scenarios?.best_case / 1000).toFixed(1)}K | Worst Case $${(results.forecast?.scenarios?.worst_case / 1000).toFixed(1)}K
- Risk Level: ${results.forecast?.risk_level}
- Sensitivity: +10% Marketing Spend impact → $${(results.forecast?.sensitivity_analysis?.marketing_spend_up_10 / 1000).toFixed(1)}K

**5. STRATEGY AGENT (Execution)**

- Strategic Moat: ${results.strategy?.strategic_moat || 'Differentiate through product depth and market agility.'}
- Resource Allocation:
${Object.entries(results.strategy?.resource_allocation || {}).map(([k, v]) => `- ${k}: ${v}`).join('\n')}

- Risk Matrix Highlights:
${(results.strategy?.risk_matrix || []).map((r: any) => `- ${r.risk} (Impact: ${r.impact}, Prob: ${r.probability})`).join('\n')}

**6. RECOMMENDED ACTIONS**

${(results.strategy?.top_priorities || []).map((p: any) => `- ${p.action}: ${p.smart_kpi}`).join('\n')}
`;

        const mappedAnalysis: DepartmentAnalysis = {
          summary: (results.strategy?.executive_summary || results.strategy?.summary || "Analysis complete.").replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, ''),
          metrics: [
            { label: "Revenue", value: `$${(results.kpi?.metrics?.revenue / 1000).toFixed(1)}K`, delta: `${results.kpi?.metrics?.rev_growth}%`, trend: results.kpi?.metrics?.rev_growth >= 0 ? "up" : "down" },
            { label: "Profit Margin", value: `${results.kpi?.metrics?.net_margin}%`, delta: "Current", trend: "flat" },
            { label: "Health Score", value: `${results.kpi?.metrics?.health_score}/100`, delta: "Overall", trend: "up" },
            { label: "Confidence", value: `${results.forecast?.confidence}%`, delta: results.forecast?.risk_level, trend: "flat" },
          ],
          insights: (results.strategy?.top_priorities || []).map((p: any) => ({ title: p.action, body: p.smart_kpi })),
          anomalies: (results.strategy?.risk_matrix || []).map((r: any) => ({ severity: "medium", message: `${r.risk}: ${r.mitigation}` })),
          forecast: [{ period: "Realistic", value: `$${(results.forecast?.scenarios?.realistic / 1000).toFixed(1)}K`, note: "Next month" }],
          reportBody: agentSummary,
          trend: results.forecast?.long_term_rev || results.forecast?.["12_month_projection"] || Array.from({ length: 24 }, () => Math.floor(Math.random() * 50) + 50),
          rawResults: results,
        };
        ws.setAnalysisData(mappedAnalysis);
      } else if (dept.id === "finance") {
        formData.append("query", "Perform a full financial audit and risk assessment on this document.");
        const response = await fetch("/api/finance/process", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error(`Finance analysis failed: ${response.statusText}`);
        const data = await response.json();
        
        
        const cleanNarrative = (data.narrative || "").replace(/\*\*/g, "");
        
        const agentSummary = `FINANCIAL MULTI-AGENT AUDIT REPORT

Executive summary

${cleanNarrative}

Key Agent Findings

1. Auditor Agent: ${data.agents_called.includes('auditor_agent') ? "Ledger audit completed. Financial records verified for consistency and potential anomalies checked." : "Audit skipped for this session."}

2. Invoice Agent: ${data.agents_called.includes('invoice_agent') ? "Invoices processed successfully. Automated tracking and ledger updates are now active." : "No new invoices detected in the uploaded dataset."}

3. Vendor Intelligence Agent: ${data.agents_called.includes('vendor_agent') ? "Vendor risk profiles and behavioral patterns analyzed. Payment cycles optimized." : "Vendor analysis skipped."}

4. FP&A Agent: ${data.agents_called.includes('fpa_agent') ? "Budget vs Actual analysis complete. Burn rate and runway projections updated." : "FP&A analysis skipped."}

Recommended Actions

- Review the executive narrative for specific departmental flags.
- Ensure all automated invoice trackers are correctly synced with the main ledger.
- Schedule a follow-up audit for the next reporting period.
`;

        const mappedAnalysis: DepartmentAnalysis = {
          summary: data.narrative.slice(0, 200) + "...",
          metrics: [
            { label: "Agents", value: `${data.agents_called.length}`, delta: "Active", trend: "up" },
            { label: "Status", value: "Verified", delta: "Audit", trend: "flat" },
            { label: "Risk", value: "Analyzed", delta: "Vendor", trend: "up" },
            { label: "Budget", value: "Checked", delta: "FP&A", trend: "up" },
          ],
          insights: data.agents_called.map((a: string) => ({ title: `Agent: ${a}`, body: `Output generated by the ${a.replace('_', ' ')}.` })),
          anomalies: [],
          forecast: [],
          reportBody: agentSummary,
          trend: Array.from({ length: 24 }, () => Math.floor(Math.random() * 40) + 30),
        };
        ws.setAnalysisData(mappedAnalysis);
      }

      ws.setStatus("generating");
      setTimeout(() => ws.setStatus("complete"), 1500);

    } catch (err) {
      console.error("Analysis error:", err);
      ws.setError(err instanceof Error ? err.message : "An unexpected error occurred.");
      ws.setStatus("error");
    }
  }, [dept.id, ws]);

  
  useEffect(() => {
    if (ws.status === "uploaded" && ws.file) {
      runAnalysis(ws.file);
    }
  }, [ws.status, ws.file, runAnalysis]);

  const analysis = ws.analysisData || mockAnalyses[dept.id];
  
  
  const hasData = !!ws.analysisData;
  const isIdle = ws.status === "idle";
  const showResults = hasData || isIdle;

  
  const showAnalysis = showResults && (ws.status === "complete") && (dept.id !== "sales-hr" && dept.id !== "bi" && dept.id !== "finance");
  const showReport = showResults && (ws.status === "complete") && (dept.id !== "sales-hr" && dept.id !== "bi" && dept.id !== "finance");
  const chatEnabled = true;

  
  const renderBIResults = () => {
    if (dept.id !== "bi" || !ws.analysisData) return null;
    
    const results = ws.analysisData.rawResults;
    const chartData = ws.analysisData.trend.map((val, i) => ({
      period: `P${i + 1}`,
      value: val,
    }));

    const handleDownload = () => {
      if (!ws.analysisData) return;
      const meta = `SOURCE: ${ws.fileName ?? "UPLOADED FILE"}\nGENERATED: ${new Date().toLocaleString()}\nDEPARTMENT: BUSINESS INTELLIGENCE\n\n`;
      
      const cleanText = ws.analysisData.reportBody
        .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '')
        .replace(/\*\*/g, "");
      
      const blob = new Blob([meta + cleanText], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `finvexis-bi-report-${new Date().getTime()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };

    const expenseData = results?.kpi?.metrics?.expense_breakdown 
      ? Object.entries(results.kpi.metrics.expense_breakdown).map(([name, value]) => ({ name, value }))
      : [];

    const scorecardData = results?.market?.scorecard 
      ? Object.entries(results.market.scorecard).map(([key, value]: [string, any]) => ({
          subject: key.replace(/_/g, ' '),
          A: parseFloat(value.split('/')[0]) || 0,
          fullMark: 10
        }))
      : [];

    const benchmarkData = results?.market?.benchmarking 
      ? [
          { name: 'Our Margin', value: parseFloat(results.kpi?.metrics?.net_margin) || 0, fill: 'hsl(var(--primary))' },
          { name: 'Industry Avg', value: parseFloat(results.market.benchmarking.Industry_Average_Margin) || 15, fill: 'hsl(var(--muted))' }
        ]
      : [];

    const resourceData = results?.strategy?.resource_allocation 
      ? Object.entries(results.strategy.resource_allocation).map(([name, value]: [string, any]) => ({
          name: name.replace(/_/g, ' '),
          value: parseFloat(value) || 0
        }))
      : [];

    const COLORS = ['#D4AF37', '#C0C0C0', '#808080', '#404040', '#A0A0A0'];

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 mt-6"
      >
        <div className="rounded-2xl border border-border/60 bg-gradient-editorial p-6 shadow-elegant">
          <div className="flex items-center justify-between mb-6 border-b border-border/40 pb-4">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                <Icon className="h-4 w-4" />
              </div>
              <h3 className="font-serif text-xl text-foreground">
                {dept.id === "bi" ? "Strategic Intelligence Dashboard" : "Financial Multi-Agent Audit"}
              </h3>
            </div>
            {dept.id === "bi" && (
              <Button 
                onClick={handleDownload} 
                size="sm" 
                className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 gap-2 h-9"
              >
                <Download className="h-4 w-4" />
                <span>Download Report</span>
              </Button>
            )}
          </div>
          
          <div className="prose prose-sm prose-invert max-w-none mb-8">
            <div className="text-sm text-black leading-relaxed whitespace-pre-wrap font-sans space-y-4">
              {ws.analysisData.reportBody.split('\n\n').map((paragraph, idx) => {
                if (paragraph.startsWith('**')) {
                  return <h4 key={idx} className="text-black font-bold text-base mt-6 mb-2">{paragraph.replace(/\*\*/g, '')}</h4>;
                }
                return <p key={idx} className="mb-4 text-black font-normal">{paragraph}</p>;
              })}
            </div>
          </div>

          {dept.id === "bi" && results && (
            <div className="space-y-10">
              {}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="rounded-xl border border-primary/20 bg-primary/5 p-4 flex flex-col items-center text-center">
                  <p className="text-[10px] uppercase tracking-widest text-primary font-bold mb-1">Runway</p>
                  <p className="text-2xl font-serif text-foreground">{results.kpi?.metrics?.efficiency?.Runway_Months} Mo</p>
                  <p className="text-[10px] text-muted-foreground mt-1">Cash sustainability</p>
                </div>
                <div className="rounded-xl border border-border/40 bg-card/40 p-4 flex flex-col items-center text-center">
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-1">Burn Rate</p>
                  <p className="text-2xl font-serif text-foreground">${(results.kpi?.metrics?.expenses / 1000).toFixed(1)}K</p>
                  <p className="text-[10px] text-muted-foreground mt-1">Monthly operational cost</p>
                </div>
                <div className="rounded-xl border border-border/40 bg-card/40 p-4 flex flex-col items-center text-center">
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-1">Op. Leverage</p>
                  <p className={`text-2xl font-serif ${results.kpi?.metrics?.efficiency?.Operating_Leverage > 1 ? 'text-green-500' : 'text-orange-500'}`}>
                    {results.kpi?.metrics?.efficiency?.Operating_Leverage}x
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1">Rev vs Exp scaling</p>
                </div>
              </div>

              {}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <TrendingUp className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Growth Trajectory</h4>
                  </div>
                  <div className="h-56 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                        <XAxis dataKey="period" hide />
                        <YAxis hide domain={['dataMin - 10', 'dataMax + 10']} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                          itemStyle={{ color: 'hsl(var(--primary))' }}
                        />
                        <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorValue)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <PieIcon className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Expense Breakdown</h4>
                  </div>
                  <div className="h-56 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={expenseData}
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {expenseData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                        />
                        <Legend verticalAlign="bottom" height={36}/>
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {}
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <Search className="h-4 w-4 text-primary" />
                  <h4 className="text-sm font-medium text-foreground">SWOT Analysis Grid</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-5 rounded-xl border border-green-500/20 bg-green-500/5 space-y-3">
                    <div className="flex items-center gap-2 text-green-500">
                      <Zap className="h-4 w-4" />
                      <span className="text-xs font-bold uppercase tracking-wider">Strengths</span>
                    </div>
                    <ul className="space-y-1">
                      {(results.market?.swot?.strengths || []).map((s: string, i: number) => (
                        <li key={i} className="text-[11px] text-foreground/80 flex items-start gap-2">
                          <span className="text-green-500/50 mt-1">•</span> {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5 rounded-xl border border-red-500/20 bg-red-500/5 space-y-3">
                    <div className="flex items-center gap-2 text-red-500">
                      <TrendingDown className="h-4 w-4" />
                      <span className="text-xs font-bold uppercase tracking-wider">Weaknesses</span>
                    </div>
                    <ul className="space-y-1">
                      {(results.market?.swot?.weaknesses || []).map((w: string, i: number) => (
                        <li key={i} className="text-[11px] text-foreground/80 flex items-start gap-2">
                          <span className="text-red-500/50 mt-1">•</span> {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5 rounded-xl border border-primary/20 bg-primary/5 space-y-3">
                    <div className="flex items-center gap-2 text-primary">
                      <ArrowUpRight className="h-4 w-4" />
                      <span className="text-xs font-bold uppercase tracking-wider">Opportunities</span>
                    </div>
                    <ul className="space-y-1">
                      {(results.market?.swot?.opportunities || []).map((o: string, i: number) => (
                        <li key={i} className="text-[11px] text-foreground/80 flex items-start gap-2">
                          <span className="text-primary/50 mt-1">•</span> {o}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="p-5 rounded-xl border border-orange-500/20 bg-orange-500/5 space-y-3">
                    <div className="flex items-center gap-2 text-orange-500">
                      <ShieldAlert className="h-4 w-4" />
                      <span className="text-xs font-bold uppercase tracking-wider">Threats</span>
                    </div>
                    <ul className="space-y-1">
                      {(results.market?.swot?.threats || []).map((t: string, i: number) => (
                        <li key={i} className="text-[11px] text-foreground/80 flex items-start gap-2">
                          <span className="text-orange-500/50 mt-1">•</span> {t}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Award className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Competitive Scorecard</h4>
                  </div>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart cx="50%" cy="50%" outerRadius="80%" data={scorecardData}>
                        <PolarGrid stroke="hsl(var(--border))" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 10]} hide />
                        <Radar
                          name="Our Performance"
                          dataKey="A"
                          stroke="hsl(var(--primary))"
                          fill="hsl(var(--primary))"
                          fillOpacity={0.5}
                        />
                        <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Industry Benchmarking</h4>
                  </div>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={benchmarkData} layout="vertical" margin={{ left: 20, right: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                        <XAxis type="number" hide />
                        <YAxis dataKey="name" type="category" tick={{ fill: 'hsl(var(--foreground))', fontSize: 11 }} />
                        <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={30}>
                          {benchmarkData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={benchmarkData[index].fill} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <p className="text-[10px] text-muted-foreground text-center mt-2">
                    {results.market?.benchmarking?.Growth_Comparison} vs industry baseline
                  </p>
                </div>
              </div>

              {}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Globe className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Market Intelligence</h4>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1 p-3 rounded-lg bg-surface-muted/30 border border-border/20">
                      <p className="text-[9px] uppercase tracking-wider text-muted-foreground">Total Addressable Market (TAM)</p>
                      <p className="text-lg font-serif text-foreground">{results.market?.market_intelligence?.TAM}</p>
                    </div>
                    <div className="space-y-1 p-3 rounded-lg bg-surface-muted/30 border border-border/20">
                      <p className="text-[9px] uppercase tracking-wider text-muted-foreground">Serviceable Market (SAM)</p>
                      <p className="text-lg font-serif text-foreground">{results.market?.market_intelligence?.SAM}</p>
                    </div>
                    <div className="space-y-1 p-3 rounded-lg bg-surface-muted/30 border border-border/20">
                      <p className="text-[9px] uppercase tracking-wider text-muted-foreground">Projected CAGR</p>
                      <p className="text-lg font-serif text-foreground">{results.market?.market_intelligence?.Projected_Growth}</p>
                    </div>
                    <div className="space-y-1 p-3 rounded-lg bg-surface-muted/30 border border-border/20">
                      <p className="text-[9px] uppercase tracking-wider text-muted-foreground">Customer Sentiment</p>
                      <p className="text-lg font-serif text-foreground">{results.market?.market_intelligence?.Customer_Sentiment}/100</p>
                    </div>
                  </div>
                  
                  {}
                  <div className="mt-6 space-y-3">
                    <p className="text-[10px] uppercase tracking-widest text-primary font-bold">Competitive Feature Gaps</p>
                    <div className="space-y-2">
                      {(results.market?.competitive_analysis?.feature_gap_analysis || []).slice(0, 3).map((gap: any, i: number) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-red-500/5 border border-red-500/10">
                          <div className="flex flex-col">
                            <span className="text-xs font-medium text-foreground">{gap.feature}</span>
                            <span className="text-[9px] text-muted-foreground">{gap.customer_perceived_value}</span>
                          </div>
                          <Badge variant="outline" className="text-[8px] border-red-500/30 text-red-500 uppercase">{gap.importance}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Target className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Strategic Execution</h4>
                  </div>
                  
                  {}
                  <div className="mb-6">
                    <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-3">Resource Allocation</p>
                    <div className="h-40 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={resourceData} layout="vertical" margin={{ left: 40, right: 20 }}>
                          <XAxis type="number" hide />
                          <YAxis dataKey="name" type="category" tick={{ fill: 'hsl(var(--foreground))', fontSize: 10 }} width={80} />
                          <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                          <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                            {resourceData.map((_, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="relative pl-6 border-l-2 border-primary/20 space-y-4">
                      <div className="relative">
                        <div className="absolute -left-[31px] top-0 h-4 w-4 rounded-full bg-primary border-4 border-card" />
                        <p className="text-[10px] uppercase font-bold text-primary mb-1">Immediate (0-90 Days)</p>
                        <div className="flex flex-wrap gap-1.5">
                          {(results.strategy?.action_plan?.immediate || []).map((a: string, i: number) => (
                            <Badge key={i} variant="secondary" className="text-[9px] py-0">{a}</Badge>
                          ))}
                        </div>
                      </div>
                      <div className="relative">
                        <div className="absolute -left-[31px] top-0 h-4 w-4 rounded-full bg-muted border-4 border-card" />
                        <p className="text-[10px] uppercase font-bold text-muted-foreground mb-1">Medium Term (3-12 Months)</p>
                        <div className="flex flex-wrap gap-1.5">
                          {(results.strategy?.action_plan?.medium_term || []).map((a: string, i: number) => (
                            <Badge key={i} variant="outline" className="text-[9px] py-0">{a}</Badge>
                          ))}
                        </div>
                      </div>
                      <div className="relative">
                        <div className="absolute -left-[31px] top-0 h-4 w-4 rounded-full bg-muted/50 border-4 border-card" />
                        <p className="text-[10px] uppercase font-bold text-muted-foreground/50 mb-1">Long Term (1 Year+)</p>
                        <div className="flex flex-wrap gap-1.5">
                          {(results.strategy?.action_plan?.long_term || []).map((a: string, i: number) => (
                            <Badge key={i} variant="outline" className="text-[9px] py-0 opacity-50">{a}</Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <ShieldAlert className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Risk Matrix</h4>
                  </div>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent border-border/40">
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Risk</TableHead>
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Impact</TableHead>
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Probability</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {(results.strategy?.risk_matrix || []).map((risk: any, i: number) => (
                          <TableRow key={i} className="hover:bg-surface-muted/20 border-border/20">
                            <TableCell className="py-2 text-xs font-medium">{risk.risk}</TableCell>
                            <TableCell className="py-2">
                              <Badge variant="outline" className={`text-[9px] uppercase ${
                                risk.impact === 'High' || risk.impact === 'Critical' ? 'border-red-500/50 text-red-500' : 'border-primary/50 text-primary'
                              }`}>
                                {risk.impact}
                              </Badge>
                            </TableCell>
                            <TableCell className="py-2 text-[10px] text-muted-foreground">{risk.probability}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>

                <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Users className="h-4 w-4 text-primary" />
                    <h4 className="text-sm font-medium text-foreground">Market Segmentation</h4>
                  </div>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="hover:bg-transparent border-border/40">
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Segment</TableHead>
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Opportunity</TableHead>
                          <TableHead className="text-[10px] uppercase tracking-wider h-8">Strategy</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {(results.market?.segmentation || []).map((seg: any, i: number) => (
                          <TableRow key={i} className="hover:bg-surface-muted/20 border-border/20">
                            <TableCell className="py-2 text-xs font-medium">{seg.name}</TableCell>
                            <TableCell className="py-2">
                              <Badge variant="outline" className={`text-[9px] uppercase ${
                                seg.opportunity === 'High' ? 'border-green-500/50 text-green-500' : 'border-primary/50 text-primary'
                              }`}>
                                {seg.opportunity}
                              </Badge>
                            </TableCell>
                            <TableCell className="py-2 text-[10px] text-muted-foreground">{seg.strategy}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </div>

              {}
              <div className="rounded-xl border border-border/40 bg-card/40 p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Target className="h-4 w-4 text-primary" />
                  <h4 className="text-sm font-medium text-foreground">Strategic Priorities & Execution</h4>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {(results.strategy?.top_priorities || []).slice(0, 4).map((priority: any, i: number) => (
                    <div key={i} className="p-4 rounded-lg bg-surface-muted/30 border border-border/20 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-[9px] uppercase tracking-widest text-primary font-bold">Priority {i + 1}</span>
                        <Badge variant="outline" className="text-[8px] border-primary/30">{priority.urgency}</Badge>
                      </div>
                      <p className="text-xs font-semibold text-foreground leading-tight">{priority.action}</p>
                      <p className="text-[10px] text-muted-foreground leading-relaxed">{priority.smart_kpi}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
          
          <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
            {ws.analysisData.metrics.map((m, i) => (
              <div key={i} className="rounded-xl border border-border/40 bg-card/40 p-3">
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">{m.label}</p>
                <p className="text-lg font-serif text-foreground">{m.value}</p>
                <p className={`text-[10px] ${m.trend === 'up' ? 'text-green-500' : m.trend === 'down' ? 'text-red-500' : 'text-muted-foreground'}`}>
                  {m.delta}
                </p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="h-[calc(100vh-100px)] flex flex-col pt-2 pb-4 overflow-hidden"
    >
      {}
      <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-4 flex-shrink-0">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <div className={`h-10 w-10 rounded-xl ${dept.accentBgClass} ${dept.accentClass} flex items-center justify-center`}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <p className="editorial-rule text-[10px] uppercase tracking-[0.22em] text-primary">
                {dept.shortName}
              </p>
              <h1 className="font-serif text-2xl md:text-3xl text-foreground">{dept.tagline}</h1>
            </div>
          </div>
          <p className="text-muted-foreground max-w-2xl text-pretty text-sm">{dept.description}</p>
        </div>
        <StatusBadge status={ws.status} deptId={dept.id} />
      </div>

      {}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 flex-1 min-h-0 overflow-hidden">
        {}
        <div className="xl:col-span-7 space-y-6 overflow-y-auto pr-2 custom-scrollbar pb-10">
          <section className="rounded-2xl border border-border/60 bg-card/70 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-[10px] uppercase tracking-[0.18em] text-primary">Step 1</p>
                <h2 className="font-serif text-xl text-foreground">Upload your file</h2>
              </div>
              {ws.fileName && (
                <button
                  onClick={ws.reset}
                  className="text-xs text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
                >
                  Start over
                </button>
              )}
            </div>
            <FileDropzone
              fileName={ws.fileName}
              onFile={ws.uploadFile}
              onClear={ws.clearFile}
              disabled={ws.status === "analyzing" || ws.status === "generating"}
            />
          </section>

          {}
          {ws.status === "error" && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="rounded-2xl border border-destructive/20 bg-destructive/5 p-5 flex items-start gap-4"
            >
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div>
                <h3 className="font-serif text-lg text-destructive">Analysis failed</h3>
                <p className="text-sm text-destructive/80 mt-1">{ws.error}</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={ws.reset}
                  className="mt-4 border-destructive/20 text-destructive hover:bg-destructive/10"
                >
                  Try again
                </Button>
              </div>
            </motion.div>
          )}

          {}
          {(ws.status === "analyzing" || ws.status === "generating") && dept.id === "bi" && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-border/60 bg-gradient-editorial p-6 flex items-center gap-4"
            >
              <Loader2 className="h-5 w-5 text-primary animate-spin" />
              <div>
                <p className="font-serif text-lg text-foreground">
                  {ws.status === "analyzing" ? "Analyzing business data" : "Generating report"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {ws.status === "analyzing"
                    ? "Reading structure, computing baseline metrics, and detecting outliers."
                    : "Synthesizing insights, recommendations and forecast into a downloadable report."}
                </p>
              </div>
            </motion.div>
          )}

          {renderBIResults()}

          {showAnalysis && <AnalysisCards analysis={analysis} rich={rich} />}

          {showReport && (
            <ReportCard 
              title={dept.reportTitle} 
              fileName={ws.fileName} 
              analysis={analysis} 
            />
          )}
        </div>

        {}
        <div className="xl:col-span-5 h-full min-h-[400px]">
          <ChatPanel
            dept={dept}
            enabled={chatEnabled}
            fileName={ws.fileName}
            file={ws.file}
            analysisData={analysis}
            reportReady={showReport}
          />
        </div>
      </div>
    </motion.div>
  );
};

export default DepartmentWorkspace;
