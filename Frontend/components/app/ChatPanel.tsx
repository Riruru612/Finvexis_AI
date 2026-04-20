import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Lock, Send, Sparkles, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { DepartmentConfig } from "@/lib/departments";

import type { DepartmentAnalysis } from "@/lib/mockAnalysis";

interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
  ts: number;
}

interface ChatPanelProps {
  dept: DepartmentConfig;
  enabled: boolean;
  fileName: string | null;
  file: File | null;
  analysisData: DepartmentAnalysis | null;
  reportReady: boolean;
}

const ChatPanel = ({ dept, enabled, fileName, file, analysisData, reportReady }: ChatPanelProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [thinking, setThinking] = useState(false);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (enabled && messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content: `Hello! I'm your ${dept.name} assistant. ${
            fileName 
              ? `I've reviewed ${fileName} and the ${dept.reportTitle.toLowerCase()}. Ask me anything about the data.`
              : `Ask me anything — I can help you with insights, forecasts, or general ${dept.name.toLowerCase()} questions even before you upload a file.`
          }`,
          ts: Date.now(),
        },
      ]);
    }
    if (!enabled) {
      setMessages([]);
      setDraft("");
    }
  }, [enabled, fileName, dept, messages.length]);

  useEffect(() => {
    scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  const send = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text) return;

    const userMsg: ChatMessage = { id: Math.random().toString(36).substring(7), role: "user", content: text, ts: Date.now() };
    setMessages((m) => [...m, userMsg]);
    setDraft("");
    setThinking(true);

    try {
      let responseContent = "";
      console.log(`Sending message to ${dept.id} department:`, text);
      
      if (dept.id === "bi") {
        const response = await fetch("/api/business/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            prompt: text,
            analysis_results: analysisData?.rawResults || analysisData,
            context_summary: analysisData?.summary 
          }),
        });
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`BI service error: ${response.status} ${errorText}`);
        }
        const data = await response.json();
        
        const rawResponse = data.response || data.message || JSON.stringify(data);
        responseContent = rawResponse.replace(/\*\*/g, "");
      } else if (dept.id === "finance") {
        const formData = new FormData();
        formData.append("query", text);
        if (file) {
          formData.append("file", file);
        }
        const response = await fetch("/api/finance/process", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Finance service error: ${response.status} ${errorText}`);
        }
        const data = await response.json();
        
        const rawNarrative = data.narrative || data.response || data.message || JSON.stringify(data);
        responseContent = rawNarrative.replace(/\*\*/g, "");
      } else if (dept.id === "sales-hr") {
        const formData = new FormData();
        formData.append("query", text);
        if (file) {
          formData.append("file", file);
        }
        const response = await fetch("/api/sales/process", {
          method: "POST",
          body: formData,
        });
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Sales & HR service error: ${response.status} ${errorText}`);
        }
        const data = await response.json();
        
        responseContent = data.response || data.message || JSON.stringify(data);
      }

      setMessages((m) => [
        ...m,
        { id: Math.random().toString(36).substring(7), role: "assistant", content: responseContent, ts: Date.now() },
      ]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((m) => [
        ...m,
        { 
          id: Math.random().toString(36).substring(7), 
          role: "error", 
          content: err instanceof Error ? err.message : "An unexpected error occurred. Please make sure the backend is running.", 
          ts: Date.now() 
        },
      ]);
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-border/60 bg-card/80 overflow-hidden shadow-elegant relative">
      {}
      <div className="flex items-center justify-between gap-3 border-b border-border/60 px-5 py-3 bg-surface-muted/60">
        <div className="flex items-center gap-2 min-w-0">
          <Sparkles className="h-4 w-4 text-primary flex-shrink-0" />
          <p className="text-xs text-foreground truncate">
            {fileName
              ? (dept.id === "sales-hr" ? `Context: ${fileName}` : `Context: ${fileName} · ${reportReady ? "Report ready" : "Analysis ready"}`)
              : `Context: General ${dept.name} Assistant`}
          </p>
        </div>
        <span className="text-[10px] uppercase tracking-wider px-2 py-1 rounded-full bg-primary/15 text-primary">
          Unlocked
        </span>
      </div>

      {}
      <div ref={scrollerRef} className="flex-1 overflow-y-auto px-5 py-5 space-y-3">
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-gradient-gold text-primary-foreground rounded-br-md"
                    : m.role === "error"
                      ? "bg-destructive/10 text-destructive border border-destructive/20 rounded-md"
                      : "bg-surface-muted text-foreground rounded-bl-md border border-border/40"
                }`}
              >
                {m.role === "assistant" && (
                  <div className="flex items-center gap-1.5 mb-1 opacity-70">
                    <Sparkles className="h-3 w-3 text-primary" />
                    <span className="text-[10px] uppercase tracking-wider">Finvexis</span>
                  </div>
                )}
                {m.role === "error" && (
                  <div className="flex items-center gap-1.5 mb-1 opacity-70">
                    <AlertCircle className="h-3 w-3 text-destructive" />
                    <span className="text-[10px] uppercase tracking-wider">System Error</span>
                  </div>
                )}
                <p className="whitespace-pre-wrap text-pretty">{m.content}</p>
              </div>
            </motion.div>
          ))}
          {thinking && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-surface-muted text-muted-foreground rounded-2xl rounded-bl-md px-4 py-3 border border-border/40">
                <div className="flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "120ms" }} />
                  <span className="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style={{ animationDelay: "240ms" }} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {}
      <form onSubmit={send} className="border-t border-border/60 bg-card/90 p-3">
        <div className="flex items-center gap-2">
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={dept.promptPlaceholder}
            className="h-11 bg-surface-muted/60 border-border/60 focus-visible:ring-primary/40"
          />
          <Button
            type="submit"
            disabled={!draft.trim()}
            className="h-11 px-4 bg-gradient-gold text-primary-foreground shadow-soft disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
