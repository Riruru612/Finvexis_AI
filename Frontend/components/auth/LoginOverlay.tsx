import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Eye, EyeOff, Loader2, Lock, Mail, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface LoginOverlayProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const LoginOverlay = ({ open, onClose, onSuccess }: LoginOverlayProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [touched, setTouched] = useState(false);

  useEffect(() => {
    if (!open) {
      setSubmitting(false);
      setTouched(false);
    }
  }, [open]);

  
  useEffect(() => {
    if (open) {
      const prev = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => { document.body.style.overflow = prev; };
    }
  }, [open]);

  const emailValid = /\S+@\S+\.\S+/.test(email);
  const pwdValid = password.length >= 6;
  const valid = emailValid && pwdValid;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!valid) return;
    setSubmitting(true);
    window.setTimeout(() => onSuccess(), 900);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          key="login-backdrop"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="fixed inset-0 z-[100] flex items-center justify-center px-4"
          style={{
            background:
              "radial-gradient(ellipse at center, hsl(38 50% 92% / 0.55), hsl(28 25% 30% / 0.35))",
            backdropFilter: "blur(18px) saturate(140%)",
            WebkitBackdropFilter: "blur(18px) saturate(140%)",
          }}
          onClick={onClose}
        >
          <motion.div
            key="login-card"
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97, y: 8 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md rounded-2xl glass-strong shadow-elegant p-8"
          >
            {}
            <div className="absolute -inset-0.5 rounded-2xl bg-gradient-amber opacity-15 blur-xl pointer-events-none" />

            <div className="relative">
              <div className="flex items-center gap-2 text-primary">
                <Sparkles className="h-4 w-4" />
                <span className="text-[11px] uppercase tracking-[0.2em]">Finvexis AI</span>
              </div>

              <h2 className="font-serif text-3xl text-foreground mt-3">
                Welcome back.
              </h2>
              <p className="text-sm text-muted-foreground mt-1.5">
                Sign in to enter your intelligence workspace.
              </p>

              <form onSubmit={handleSubmit} className="mt-7 space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="email" className="text-xs uppercase tracking-wider text-muted-foreground">
                    Email
                  </Label>
                  <div className="relative">
                    <Mail className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      autoComplete="email"
                      placeholder="you@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10 h-11 bg-card/70 border-border/70 focus-visible:ring-primary/40"
                      aria-invalid={touched && !emailValid}
                    />
                  </div>
                  {touched && !emailValid && (
                    <p className="text-xs text-destructive">Please enter a valid email.</p>
                  )}
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password" className="text-xs uppercase tracking-wider text-muted-foreground">
                      Password
                    </Label>
                    <button
                      type="button"
                      className="text-xs text-primary hover:underline underline-offset-4"
                    >
                      Forgot?
                    </button>
                  </div>
                  <div className="relative">
                    <Lock className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPwd ? "text" : "password"}
                      autoComplete="current-password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10 pr-10 h-11 bg-card/70 border-border/70 focus-visible:ring-primary/40"
                      aria-invalid={touched && !pwdValid}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPwd((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      aria-label={showPwd ? "Hide password" : "Show password"}
                    >
                      {showPwd ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  {touched && !pwdValid && (
                    <p className="text-xs text-destructive">Use at least 6 characters.</p>
                  )}
                </div>

                <Button
                  type="submit"
                  disabled={submitting}
                  className="w-full h-11 bg-gradient-gold text-primary-foreground hover:opacity-95 shadow-soft"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Signing in…
                    </>
                  ) : (
                    "Sign in"
                  )}
                </Button>

                <div className="relative py-2">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-border/60" />
                  </div>
                  <div className="relative flex justify-center">
                    <span className="bg-card/0 px-3 text-[11px] uppercase tracking-wider text-muted-foreground">
                      or
                    </span>
                  </div>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  className="w-full h-11 bg-card/70 border-border/70"
                  onClick={() => {
                    setSubmitting(true);
                    window.setTimeout(() => onSuccess(), 700);
                  }}
                >
                  Continue with Google
                </Button>
              </form>

              <p className="text-center text-xs text-muted-foreground mt-6">
                By continuing you agree to Finvexis' terms and privacy policy.
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default LoginOverlay;
