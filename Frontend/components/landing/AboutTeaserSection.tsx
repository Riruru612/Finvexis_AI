import { motion } from "framer-motion";

const AboutTeaserSection = () => {
  return (
    <section className="relative py-8 md:py-10">
      <div className="container relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-5">
            <p className="editorial-rule text-xs uppercase tracking-[0.22em] text-primary mb-4">
              About Finvexis
            </p>
            <h2 className="font-serif text-4xl md:text-5xl text-foreground text-balance">
              A quieter, smarter way to{" "}
              <span className="italic text-gradient-amber">run a business.</span>
            </h2>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7 }}
            className="lg:col-span-7 space-y-5 text-lg text-muted-foreground leading-relaxed text-pretty"
          >
            <p>
              Finvexis AI is a multi-agent business intelligence platform with
              three coordinated departments — Finance, Business Intelligence,
              and Sales &amp; HR. Each agent is built around a specific business
              question, and they share the same understanding of your data.
            </p>
            <p>
              The result is something that feels less like a tool and more like
              a small, senior analytics team you can call on whenever you need
              clarity, a forecast, or a second opinion.
            </p>
            <p className="text-sm pt-2 text-secondary/80">
              This is the prototype frontend. The production system, with full
              agent integration, is being merged separately.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default AboutTeaserSection;
