const LandingFooter = () => {
  return (
    <footer className="relative border-t border-border/60 mt-4">
      <div className="container py-4 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-3">
          <span className="font-serif text-foreground">Finvexis AI</span>
          <span className="h-1 w-1 rounded-full bg-primary/60" />
          <span>Business intelligence, refined.</span>
        </div>
        <p className="text-xs">© {new Date().getFullYear()} Finvexis · Prototype frontend</p>
      </div>
    </footer>
  );
};

export default LandingFooter;
