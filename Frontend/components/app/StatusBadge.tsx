import type { WorkspaceStatus } from "@/hooks/useWorkspaceState";
import { Loader2, CheckCircle2, Clock, FileText, MessageCircle } from "lucide-react";

interface StatusBadgeProps {
  status: WorkspaceStatus;
  deptId?: string;
  className?: string;
}

const getLabel = (status: WorkspaceStatus, deptId?: string) => {
  if (status === "analyzing") {
    if (deptId === "finance") return "Performing financial audit";
    if (deptId === "sales-hr") return "Screening talent & leads";
    return "Analyzing business data";
  }
  
  const labels: Record<WorkspaceStatus, string> = {
    idle: "Waiting for upload",
    uploaded: "File received",
    analyzing: "Analyzing data",
    generating: "Generating report",
    complete: "Report ready · Chat unlocked",
    error: "Analysis failed"
  };
  return labels[status];
};

const StatusBadge = ({ status, deptId, className = "" }: StatusBadgeProps) => {
  const label = getLabel(status, deptId);
  const Icon = status === "complete" ? CheckCircle2 : (status === "idle" ? Clock : (status === "uploaded" ? FileText : (status === "error" ? Clock : Loader2)));
  const tone = status === "idle" ? "bg-surface-muted text-muted-foreground" : (status === "uploaded" ? "bg-olive/15 text-olive" : (status === "error" ? "bg-destructive/15 text-destructive" : "bg-primary/15 text-primary"));
  const spin = status === "analyzing" || status === "generating";
  
  return (
    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium ${tone} ${className}`}>
      <Icon className={`h-3.5 w-3.5 ${spin ? "animate-spin" : ""}`} />
      {label}
      {status === "complete" && <MessageCircle className="h-3.5 w-3.5 ml-1 opacity-70" />}
    </span>
  );
};

export default StatusBadge;
