import { AnimatePresence, motion } from "framer-motion";
import TopNavbar, { type AppSection } from "./TopNavbar";
import AboutSection from "./AboutSection";
import DepartmentWorkspace from "./DepartmentWorkspace";
import { getDepartment } from "@/lib/departments";

interface AppShellProps {
  section: AppSection;
  onChangeSection: (s: AppSection) => void;
  onLogout: () => void;
}

const AppShell = ({ section, onChangeSection, onLogout }: AppShellProps) => {
  return (
    <div className="min-h-screen bg-background relative">
      {}
      <div className="pointer-events-none fixed inset-0">
        <div className="absolute inset-0 bg-gradient-warm opacity-70" />
        <div
          className="absolute -top-40 right-0 h-[28rem] w-[28rem] rounded-full opacity-40"
          style={{
            background: "radial-gradient(circle, hsl(40 70% 80% / 0.5), transparent 60%)",
            filter: "blur(50px)",
          }}
        />
      </div>

      <div className="relative">
        <TopNavbar active={section} onChange={onChangeSection} onLogout={onLogout} />

        <main className="container py-4 md:py-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={section}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            >
              {section === "about" && (
                <AboutSection onOpenDepartment={(id) => onChangeSection(id)} />
              )}
              {section === "finance" && (
                <DepartmentWorkspace dept={getDepartment("finance")} />
              )}
              {section === "bi" && (
                <DepartmentWorkspace dept={getDepartment("bi")} rich />
              )}
              {section === "sales-hr" && (
                <DepartmentWorkspace dept={getDepartment("sales-hr")} />
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

export default AppShell;
