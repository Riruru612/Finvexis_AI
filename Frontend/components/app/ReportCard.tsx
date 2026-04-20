import { Download, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import type { DepartmentAnalysis } from "@/lib/mockAnalysis";

interface ReportCardProps {
  title: string;
  fileName: string | null;
  analysis: DepartmentAnalysis;
}

const ReportCard = ({ title, fileName, analysis }: ReportCardProps) => {
  const handleDownload = () => {
    const meta = `Source: ${fileName ?? "uploaded file"}\nGenerated: ${new Date().toISOString()}\n\n`;
    const blob = new Blob([meta + analysis.reportBody], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, "-")}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="relative rounded-2xl border border-border/60 bg-gradient-editorial overflow-hidden"
    >
      <div className="absolute -top-12 -right-12 h-40 w-40 rounded-full bg-primary/15 blur-3xl pointer-events-none" />
      <div className="relative p-5 md:p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-primary">Generated</p>
              <p className="font-serif text-xl text-foreground">{title}</p>
            </div>
          </div>
          <Button onClick={handleDownload} className="bg-gradient-gold text-primary-foreground shadow-soft hover:opacity-95">
            <Download className="h-4 w-4" />
            Download report
          </Button>
        </div>

        <div className="mt-5 rounded-xl bg-card/80 border border-border/50 p-4 max-h-56 overflow-auto">
          <pre className="text-xs text-foreground/80 whitespace-pre-wrap font-sans leading-relaxed">
            {analysis.reportBody.slice(0, 480)}…
          </pre>
        </div>

        <p className="text-[11px] text-muted-foreground mt-3">
          The full report is included in the download. The assistant below has the complete context.
        </p>
      </div>
    </motion.div>
  );
};

export default ReportCard;
