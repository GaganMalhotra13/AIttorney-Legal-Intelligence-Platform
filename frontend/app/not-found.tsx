"use client";
import { motion, useAnimation, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, Home, Scale } from "lucide-react";

// ── Animated Balance Scale SVG ────────────────────────────────
function BalanceScale() {
  return (
    <motion.svg
      viewBox="0 0 120 100"
      className="w-28 h-24"
      initial="idle"
      animate="idle"
    >
      {/* Central pole */}
      <motion.line
        x1="60" y1="10" x2="60" y2="85"
        stroke="#C4472A" strokeWidth="2.5" strokeLinecap="round"
      />
      {/* Base */}
      <motion.rect x="42" y="85" width="36" height="5" rx="2.5"
        fill="#C4472A" opacity="0.3" />
      <motion.rect x="48" y="90" width="24" height="4" rx="2"
        fill="#C4472A" opacity="0.2" />

      {/* Top pivot */}
      <motion.circle cx="60" cy="12" r="3.5" fill="#C4472A" />

      {/* Beam — rocks left/right */}
      <motion.g
        style={{ originX: "60px", originY: "12px" }}
        animate={{ rotate: [0, -14, 8, -10, 5, -3, 0] }}
        transition={{
          duration: 3.5,
          ease: "easeInOut",
          repeat: Infinity,
          repeatDelay: 1.5,
        }}
      >
        {/* Horizontal beam */}
        <line x1="18" y1="12" x2="102" y2="12"
          stroke="#1B2236" strokeWidth="2" strokeLinecap="round" />

        {/* Left chain */}
        <line x1="22" y1="12" x2="22" y2="45"
          stroke="#1B2236" strokeWidth="1.5" strokeDasharray="3 2"
          strokeLinecap="round" />
        {/* Left pan */}
        <ellipse cx="22" cy="47" rx="13" ry="4" fill="#C4472A" opacity="0.15"
          stroke="#C4472A" strokeWidth="1.5" />
        <path d="M9 47 Q22 57 35 47" fill="#C4472A" opacity="0.08"
          stroke="#C4472A" strokeWidth="1" />
        {/* Left pan contents — document */}
        <rect x="16" y="38" width="12" height="9" rx="1.5"
          fill="#1B2236" opacity="0.15" />
        <line x1="18" y1="41" x2="26" y2="41"
          stroke="white" strokeWidth="0.8" opacity="0.6" />
        <line x1="18" y1="43" x2="24" y2="43"
          stroke="white" strokeWidth="0.8" opacity="0.6" />

        {/* Right chain */}
        <line x1="98" y1="12" x2="98" y2="38"
          stroke="#1B2236" strokeWidth="1.5" strokeDasharray="3 2"
          strokeLinecap="round" />
        {/* Right pan — higher (lighter side) */}
        <ellipse cx="98" cy="40" rx="13" ry="4" fill="#0F6E56" opacity="0.15"
          stroke="#0F6E56" strokeWidth="1.5" />
        <path d="M85 40 Q98 50 111 40" fill="#0F6E56" opacity="0.08"
          stroke="#0F6E56" strokeWidth="1" />
        {/* Right pan contents — gavel */}
        <rect x="93" y="31" width="9" height="5" rx="1.5"
          fill="#0F6E56" opacity="0.3" />
        <line x1="97.5" y1="36" x2="97.5" y2="39"
          stroke="#0F6E56" strokeWidth="1.2" opacity="0.5" />
      </motion.g>
    </motion.svg>
  );
}

// ── Floating legal symbols ────────────────────────────────────
const FLOATERS = [
  { symbol: "§",  x: "8%",  y: "15%", size: "text-4xl", delay: 0,    dur: 5    },
  { symbol: "⚖",  x: "85%", y: "20%", size: "text-3xl", delay: 0.5,  dur: 6    },
  { symbol: "§",  x: "75%", y: "70%", size: "text-5xl", delay: 1,    dur: 7    },
  { symbol: "¶",  x: "12%", y: "75%", size: "text-3xl", delay: 1.5,  dur: 5.5  },
  { symbol: "©",  x: "90%", y: "50%", size: "text-2xl", delay: 0.8,  dur: 6.5  },
  { symbol: "§",  x: "50%", y: "8%",  size: "text-2xl", delay: 2,    dur: 4.5  },
  { symbol: "⚖",  x: "5%",  y: "45%", size: "text-2xl", delay: 1.2,  dur: 5.8  },
];

function FloatingSymbol({ symbol, x, y, size, delay, dur }: typeof FLOATERS[0]) {
  return (
    <motion.div
      className={`absolute ${size} text-slate-200 font-display select-none pointer-events-none`}
      style={{ left: x, top: y }}
      initial={{ opacity: 0, y: 0 }}
      animate={{
        opacity: [0, 0.6, 0.3, 0.6, 0],
        y: [0, -18, -8, -20, 0],
      }}
      transition={{
        duration: dur,
        delay,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    >
      {symbol}
    </motion.div>
  );
}

// ── Typewriter ────────────────────────────────────────────────
function Typewriter({ text }: { text: string }) {
  const [displayed, setDisplayed] = useState("");

  useEffect(() => {
    let i = 0;
    setDisplayed("");
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 55);
    return () => clearInterval(interval);
  }, [text]);

  return (
    <span>
      {displayed}
      <motion.span
        animate={{ opacity: [1, 0] }}
        transition={{ duration: 0.6, repeat: Infinity }}
        className="inline-block w-0.5 h-6 bg-coral-500 ml-0.5 align-middle"
      />
    </span>
  );
}

// ── Gavel animation ────────────────────────────────────────────
function Gavel() {
  return (
    <motion.svg
      viewBox="0 0 48 48"
      className="w-7 h-7"
      animate={{ rotate: [0, -30, 0, -20, 0] }}
      transition={{ duration: 1.2, delay: 0.8, repeat: Infinity, repeatDelay: 3 }}
      style={{ originX: "80%", originY: "80%" }}
    >
      {/* Handle */}
      <line x1="30" y1="30" x2="44" y2="44"
        stroke="#C4472A" strokeWidth="4" strokeLinecap="round" />
      {/* Head */}
      <rect x="8" y="12" width="22" height="12" rx="3"
        fill="#1B2236" transform="rotate(-45 19 18)" />
      {/* Strike plate */}
      <rect x="6" y="10" width="8" height="13" rx="2"
        fill="#C4472A" opacity="0.7" transform="rotate(-45 10 16)" />
    </motion.svg>
  );
}

// ── 404 digit with gavel strike ───────────────────────────────
function AnimatedFourOhFour() {
  return (
    <div className="relative flex items-center justify-center">
      {/* Big 404 */}
      <motion.p
        className="font-display font-black select-none leading-none"
style={{
  fontSize: "clamp(72px, 12vw, 110px)",
  color: "#D6D4CF",
}}        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      >
        404
      </motion.p>

      {/* Gavel strike overlay */}
      <motion.div
        className="absolute"
        style={{ top: "-10px", right: "-10px" }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        <Gavel />
      </motion.div>

      {/* Section symbol accent */}
      <motion.span
        className="absolute bottom-2 left-0 font-display text-2xl font-bold"
        style={{ color: "#C4472A", opacity: 0.25 }}
        animate={{ opacity: [0.15, 0.35, 0.15] }}
        transition={{ duration: 3, repeat: Infinity }}
      >
        §
      </motion.span>
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────
export default function NotFound() {
  const quickLinks = [
    { label: "Case Mirror",     href: "/dashboard/case-mirror"    },
    { label: "Contract Audit",  href: "/dashboard/contract-audit" },
    { label: "Notice Drafter",  href: "/dashboard/notice-drafter" },
    { label: "Legal Roadmap",   href: "/dashboard/roadmap"        },
    { label: "Analytics",       href: "/dashboard/analytics"      },
  ];

  return (
   <div
  className="relative w-screen h-[100dvh] bg-bg overflow-hidden
             flex flex-col items-center justify-center px-6"
>

      {/* ── Dot grid background ───────────────────────────── */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle, #1B2236 1px, transparent 1px)",
          backgroundSize: "28px 28px",
          opacity: 0.035,
        }}
      />

      {/* ── Floating legal symbols ────────────────────────── */}
      {FLOATERS.map((f, i) => <FloatingSymbol key={i} {...f} />)}

      {/* ── Coral glow top-right ──────────────────────────── */}
      <div
        className="absolute top-0 right-0 w-96 h-96 rounded-full
                   pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(196,71,42,0.08), transparent 70%)",
          transform: "translate(30%, -30%)",
        }}
      />
      {/* ── Teal glow bottom-left ─────────────────────────── */}
      <div
        className="absolute bottom-0 left-0 w-80 h-80 rounded-full
                   pointer-events-none"
        style={{
          background: "radial-gradient(circle, rgba(15,110,86,0.06), transparent 70%)",
          transform: "translate(-30%, 30%)",
        }}
      />

      {/* ── Content card ──────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 32 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 flex flex-col items-center text-center max-w-lg w-full"
      >

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
className="flex items-center gap-2.5 mb-5"        >
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{ background: "#C4472A" }}>
            <Scale className="w-4 h-4 text-white" />
          </div>
          <span className="font-display text-xl font-bold"
            style={{ color: "#1B2236" }}>
            AI<span style={{ color: "#C4472A" }}>ttorney</span>
          </span>
        </motion.div>

        {/* Balance scale */}
        <motion.div
          initial={{ opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="mb-1"
        >
          <BalanceScale />
        </motion.div>

        {/* 404 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mb-2"
        >
          <AnimatedFourOhFour />
        </motion.div>

        {/* Heading — typewriter */}
        <motion.h1
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
className="font-display text-xl sm:text-2xl font-bold mb-1"          style={{ color: "#1B2236" }}
        >
          <Typewriter text="Case Not Found" />
        </motion.h1>

        {/* Sub text */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
className="text-xs sm:text-sm leading-snug mb-0.5"          style={{ color: "#7A7872" }}
        >
          The page you're looking for doesn't exist or has been moved.
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
className="font-mono text-[10px] sm:text-xs mb-5"          style={{ color: "#B5B2AC" }}
        >
          Error 404 · Section not found in the legal registry
        </motion.p>

        {/* Divider */}
        <motion.div
          initial={{ opacity: 0, scaleX: 0 }}
          animate={{ opacity: 1, scaleX: 1 }}
          transition={{ delay: 2.1, duration: 0.5 }}
className="flex items-center gap-3 w-full mb-5"        >
          <div className="flex-1 h-px" style={{ background: "#EEECEA" }} />
          <span className="font-mono text-2xs uppercase tracking-widest"
            style={{ color: "#AAA7A0" }}>
            AIttorney by Gagan Malhotra
          </span>
          <div className="flex-1 h-px" style={{ background: "#EEECEA" }} />
        </motion.div>

        {/* CTA buttons */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2 }}
className="flex flex-col sm:flex-row gap-3 w-full justify-center mb-5"        >
          <Link href="/dashboard/home" className="flex-1 sm:flex-none">
            <motion.button
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
              className="w-full sm:w-auto flex items-center justify-center gap-2
                         px-6 py-2.5 rounded-xl text-sm font-semibold text-white
                         transition-all"
              style={{ background: "#C4472A" }}
            >
              <Home className="w-4 h-4" />
              Go to Dashboard
            </motion.button>
          </Link>

          <motion.button
            onClick={() => window.history.back()}
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1 sm:flex-none flex items-center justify-center gap-2
                       px-6 py-2.5 rounded-xl text-sm font-medium transition-all"
            style={{
              border: "1px solid #EEECEA",
              color: "#7A7872",
              background: "#FAFAF8",
            }}
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </motion.button>
        </motion.div>

        {/* Quick links */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.4 }}
className="w-full pt-3"          style={{ borderTop: "1px solid #EEECEA" }}
        >
          <p className="text-xs mb-2" style={{ color: "#B5B2AC" }}>
            Quick links
          </p>
          <div className="flex flex-wrap justify-center gap-x-4 gap-y-2">
            {quickLinks.map(({ label, href }, i) => (
              <motion.div
                key={href}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 2.5 + i * 0.07 }}
              >
                <Link href={href}>
                  <span
                    className="text-xs font-medium transition-colors hover:underline"
                    style={{ color: "#C4472A" }}
                  >
                    {label}
                  </span>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.div>

      {/* ── Bottom disclaimer ──────────────────────────────── */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2.8 }}
        className="absolute bottom-5 font-mono text-xs"
        style={{ color: "#D3D1C7" }}
      >
        Educational use only · Not legal advice
      </motion.p>
    </div>
  );
}