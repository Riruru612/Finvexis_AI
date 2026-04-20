import { motion } from "framer-motion";

const BackgroundPaths = () => {
  const paths = Array.from({ length: 20 }, (_, i) => i);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {}
      <div className="absolute inset-0 bg-gradient-warm" />

      {}
      <div
        className="absolute -top-40 -right-32 h-[48rem] w-[48rem] rounded-full opacity-65 animate-float-slow"
        style={{
          background:
            "radial-gradient(circle, hsl(40 75% 82% / 0.6), transparent 60%)",
          filter: "blur(40px)",
        }}
      />
      <div
        className="absolute top-1/4 -left-40 h-[42rem] w-[42rem] rounded-full opacity-60 animate-float-slow"
        style={{
          background:
            "radial-gradient(circle, hsl(26 70% 75% / 0.5), transparent 60%)",
          filter: "blur(50px)",
          animationDelay: "-4s",
        }}
      />
      <div
        className="absolute bottom-0 right-1/4 h-[38rem] w-[38rem] rounded-full opacity-55 animate-float-slow"
        style={{
          background:
            "radial-gradient(circle, hsl(60 35% 75% / 0.45), transparent 60%)",
          filter: "blur(60px)",
          animationDelay: "-2s",
        }}
      />

      {}
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 1440 900"
        fill="none"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden
      >
        <defs>
          <linearGradient id="pathGold" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="hsl(40 70% 68%)" stopOpacity="0" />
            <stop offset="50%" stopColor="hsl(40 60% 58%)" stopOpacity="0.65" />
            <stop offset="100%" stopColor="hsl(26 64% 54%)" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="pathOlive" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="hsl(60 25% 55%)" stopOpacity="0" />
            <stop offset="50%" stopColor="hsl(60 25% 50%)" stopOpacity="0.45" />
            <stop offset="100%" stopColor="hsl(60 25% 55%)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {paths.map((i) => {
          const offset = i * 15;
          return (
            <motion.path
              key={i}
              d={`M-100 ${50 + offset} C 300 ${20 + offset}, 580 ${280 + offset}, 840 ${180 + offset} S 1300 ${
                340 + offset
              }, 1600 ${240 + offset}`}
              stroke={i % 2 === 0 ? "url(#pathGold)" : "url(#pathOlive)"}
              strokeWidth={0.8 + i * 0.12}
              fill="none"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.9 }}
              transition={{
                duration: 2.5,
                delay: 0,
                ease: "easeInOut",
                repeat: Infinity,
                repeatType: "reverse",
              }}
            />
          );
        })}

        {paths.map((i) => {
          const offset = i * 22;
          return (
            <motion.path
              key={`b-${i}`}
              d={`M-100 ${300 + offset} C 340 ${480 + offset}, 660 ${260 + offset}, 980 ${440 + offset} S 1380 ${
                560 + offset
              }, 1640 ${400 + offset}`}
              stroke={i % 2 === 0 ? "url(#pathOlive)" : "url(#pathGold)"}
              strokeWidth={0.6 + i * 0.1}
              fill="none"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.7 }}
              transition={{
                duration: 3,
                delay: 0,
                ease: "easeInOut",
                repeat: Infinity,
                repeatType: "reverse",
              }}
            />
          );
        })}
      </svg>

      {}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 40%, hsl(38 40% 90% / 0.5) 100%)",
        }}
      />
    </div>
  );
};

export default BackgroundPaths;
