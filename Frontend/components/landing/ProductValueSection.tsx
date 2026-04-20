import { motion } from "framer-motion";
import { Brain, LineChart, Compass, Lightbulb } from "lucide-react";

const items = [
  {
    icon: Brain,
    title: "Understand performance",
    body: "A single, calm view of how the business is actually doing — not a dashboard you have to decode.",
  },
  {
    icon: LineChart,
    title: "Analyze position",
    body: "Benchmark against your own history and the broader market to see where you really stand.",
  },
  {
    icon: Compass,
    title: "Forecast the next move",
    body: "Forward-looking signals on revenue, risk, hiring and customer health — not just lagging metrics.",
  },
  {
    icon: Lightbulb,
    title: "Recommend the action",
    body: "Specific, prioritized recommendations your team can run with this week, not next quarter.",
  },
];

const ProductValueSection = () => {
  return (
    <section className="relative py-8 md:py-10">
      <div className="w-full px-4 md:px-12 lg:px-20 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-end mb-14">
          <div className="lg:col-span-6">
            <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary mb-4">
              The value
            </p>
            <h2 className="font-serif text-4xl md:text-5xl text-foreground text-balance">
              Built to make business{" "}
              <span className="italic text-gradient-amber">readable</span>.
            </h2>
          </div>
          <div className="lg:col-span-5 lg:col-start-8">
            <p className="text-muted-foreground leading-relaxed text-pretty">
              Finvexis AI compresses the work of a small analyst team into a few
              minutes, while keeping the judgment a senior operator would expect.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-5">
          {items.map((it, i) => {
            const Icon = it.icon;
            
            const spans = [
              "lg:col-span-7",
              "lg:col-span-5",
              "lg:col-span-5",
              "lg:col-span-7",
            ];
            return (
              <motion.article
                key={it.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.6, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                className={`${spans[i]} group relative rounded-2xl glass p-7 shadow-card hover-lift overflow-hidden transition-all duration-500 hover:ring-1 hover:ring-primary/20`}
              >
                <div className="absolute -top-12 -right-12 h-40 w-40 rounded-full bg-primary/10 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                <div className="flex items-start gap-5 relative z-10">
                  <div className="flex-shrink-0 h-11 w-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-500 group-hover:rotate-6">
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-serif text-2xl text-foreground group-hover:text-primary transition-colors duration-300">{it.title}</h3>
                    <p className="text-muted-foreground leading-relaxed text-pretty group-hover:text-foreground/80 transition-colors duration-300">
                      {it.body}
                    </p>
                  </div>
                </div>
                <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-primary/10 via-primary/40 to-primary/10 group-hover:w-full transition-all duration-700 ease-in-out" />
              </motion.article>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default ProductValueSection;
