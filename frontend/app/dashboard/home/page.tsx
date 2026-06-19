"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useStore } from "@/store/useStore";
import { analyticsAPI } from "@/lib/api";
import {
  Landmark, FileText, PenLine, Map, History,
  BarChart2, FolderOpen, Calendar, ArrowRight,
  TrendingUp, Scale, Clock, Zap, Award,
  AlertTriangle, CheckCircle2, ChevronRight
} from "lucide-react";

const FEATURES = [
  {
    href:    "/dashboard/case-mirror",
    icon:    Landmark,
    label:   "Case Mirror",
    desc:    "Describe your situation in plain language. Get win probability, applicable laws, landmark judgments, and 11 AI modules.",
    badge:   "Core Feature",
    badgeColor: "bg-coral-100 text-coral-700 border-coral-200",
    accent:  "coral",
    gradient:"from-coral-50 to-coral-50/30",
    border:  "border-coral-100 hover:border-coral-300",
  },
  {
    href:    "/dashboard/contract-audit",
    icon:    FileText,
    label:   "Contract Audit",
    desc:    "Upload any contract. Real NLP clause detection scores your risk with live excerpts. Chat with the document semantically.",
    badge:   "NLP Powered",
    badgeColor: "bg-teal-100 text-teal-700 border-teal-200",
    accent:  "teal",
    gradient:"from-teal-50 to-teal-50/30",
    border:  "border-teal-100 hover:border-teal-300",
  },
  {
    href:    "/dashboard/notice-drafter",
    icon:    PenLine,
    label:   "Notice Drafter",
    desc:    "Generate formally structured legal notices in three tones. Download as PDF. Saved to history for re-use.",
    badge:   "PDF Export",
    badgeColor: "bg-amber-100 text-amber-700 border-amber-200",
    accent:  "amber",
    gradient:"from-amber-50 to-amber-50/30",
    border:  "border-amber-100 hover:border-amber-300",
  },
  {
    href:    "/dashboard/roadmap",
    icon:    Map,
    label:   "Legal Roadmap",
    desc:    "4-step procedural action plan with exact laws, timelines, and jurisdiction-specific guidance for your situation.",
    badge:   "India-Specific",
    badgeColor: "bg-blue-100 text-blue-700 border-blue-200",
    accent:  "blue",
    gradient:"from-blue-50 to-blue-50/30",
    border:  "border-blue-100 hover:border-blue-300",
  },
  {
    href:    "/dashboard/document-vault",
    icon:    FolderOpen,
    label:   "Document Vault",
    desc:    "Upload FIRs, court orders, contracts. AI extracts parties, dates, and case numbers. Search across all your documents.",
    badge:   "AI Tagging",
    badgeColor: "bg-purple-100 text-purple-700 border-purple-200",
    accent:  "purple",
    gradient:"from-purple-50 to-purple-50/30",
    border:  "border-purple-100 hover:border-purple-300",
  },
  {
    href:    "/dashboard/case-tracker",
    icon:    Calendar,
    label:   "Case Tracker",
    desc:    "Track court dates, hearing schedules, and case status. AI generates preparation checklists for each hearing.",
    badge:   "Reminders",
    badgeColor: "bg-green-100 text-green-700 border-green-200",
    accent:  "green",
    gradient:"from-green-50 to-green-50/30",
    border:  "border-green-100 hover:border-green-300",
  },
  {
    href:    "/dashboard/analytics",
    icon:    BarChart2,
    label:   "Analytics",
    desc:    "Your legal activity at a glance. Win probability trends, case type breakdown, weekly usage charts.",
    badge:   "Dashboard",
    badgeColor: "bg-slate-100 text-slate-600 border-slate-200",
    accent:  "slate",
    gradient:"from-slate-50 to-slate-50/30",
    border:  "border-slate-100 hover:border-slate-300",
  },
  {
    href:    "/dashboard/history",
    icon:    History,
    label:   "My History",
    desc:    "All your past case searches, audits, and drafted notices — persistent across sessions via MongoDB.",
    badge:   "Persistent",
    badgeColor: "bg-slate-100 text-slate-600 border-slate-200",
    accent:  "slate",
    gradient:"from-slate-50 to-slate-50/30",
    border:  "border-slate-100 hover:border-slate-300",
  },
];

const QUICK_ACTIONS = [
  { href: "/dashboard/case-mirror",   icon: Landmark, label: "Analyze a Case",    color: "text-coral-600 bg-coral-50 border-coral-100" },
  { href: "/dashboard/contract-audit",icon: FileText,  label: "Audit a Contract",  color: "text-teal-600 bg-teal-50 border-teal-100"   },
  { href: "/dashboard/notice-drafter",icon: PenLine,   label: "Draft a Notice",    color: "text-amber-600 bg-amber-50 border-amber-100" },
  { href: "/dashboard/case-tracker",  icon: Calendar,  label: "Add Court Date",    color: "text-green-600 bg-green-50 border-green-100" },
];

interface Stats {
  totals: {
    cases: number;
    audits: number;
    notices: number;
    upcoming_dates: number;
    avg_win_prob: number;
  };
  grades: Record<string, number>;
  recent_cases: any[];
  weekly_trend: { label: string; count: number }[];
}

export default function HomeDashboard() {
  const { user } = useStore();
  const [stats,   setStats]   = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" :
    hour < 17 ? "Good afternoon" : "Good evening";

  useEffect(() => {
    analyticsAPI.overview()
      .then((r) => setStats(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const firstName = user?.name?.split(" ")[0] || "there";

  return (
    <div className="space-y-10 page-enter">

      {/* ── HERO GREETING ──────────────────────────────────── */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ ease: [0.16, 1, 0.3, 1] }}
      className="relative overflow-hidden rounded-3xl p-8 text-white"
      style={{
        background: "linear-gradient(135deg, #5f5a80 0%, #393281 100%)",
      }}      >
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle, #ffffff 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        />
        {/* Ambient glow */}
        <div className="absolute top-0 right-0 w-80 h-80 bg-coral-500
                        rounded-full filter blur-3xl opacity-10
                        translate-x-1/3 -translate-y-1/3 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-teal-500
                        rounded-full filter blur-3xl opacity-6
                        -translate-x-1/3 translate-y-1/3 pointer-events-none" />

        <div className="relative z-10 flex items-start justify-between flex-wrap gap-6">
          <div>
            <p className="font-mono text-2xs tracking-widest uppercase text-white/40 mb-2">
              {greeting}
            </p>
            <h1 className="font-display text-4xl font-bold tracking-tight mb-3">
              {greeting}, {firstName} 👋
            </h1>
            <p className="text-white/60 text-sm leading-relaxed max-w-lg">
              Your legal intelligence workspace. Describe any situation in plain language
              and get win probability, landmark judgments, and actionable next steps.
            </p>
          </div>

          {/* Stat pills */}
          <div className="flex gap-3 flex-wrap">
            {[
              { label: "Cases Analyzed",  value: stats?.totals.cases         ?? "—", icon: Scale    },
              { label: "Avg Win Prob.",   value: stats?.totals.avg_win_prob  ? `${stats.totals.avg_win_prob}%` : "—", icon: TrendingUp },
              { label: "Court Dates",     value: stats?.totals.upcoming_dates ?? "—", icon: Calendar  },
            ].map(({ label, value, icon: Icon }) => (
              <div key={label}
                className="bg-white/[0.07] border border-white/[0.10]
                           backdrop-blur-sm rounded-2xl px-4 py-3 text-center min-w-[90px]">
                <Icon className="w-4 h-4 text-white/50 mx-auto mb-1.5" />
                <p className="font-display text-2xl font-bold text-white leading-none mb-0.5">
                  {loading ? "…" : value}
                </p>
                <p className="font-mono text-[9px] text-white/40 uppercase tracking-widest">
                  {label}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Quick actions */}
        <div className="relative z-10 mt-6 flex flex-wrap gap-2">
          {QUICK_ACTIONS.map(({ href, icon: Icon, label }) => (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ scale: 1.02, y: -1 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-2 px-4 py-2 rounded-xl
                           bg-white/[0.08] hover:bg-white/[0.14] border border-white/[0.10]
                           text-white text-sm font-medium transition-all cursor-pointer"
              >
                <Icon className="w-3.5 h-3.5 text-white/70" />
                {label}
                <ArrowRight className="w-3 h-3 text-white/40" />
              </motion.div>
            </Link>
          ))}
        </div>
      </motion.div>

      {/* ── RECENT ACTIVITY ────────────────────────────────── */}
      {stats?.recent_cases && stats.recent_cases.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="label flex items-center gap-1.5">
              <Clock className="w-3 h-3" /> Recent Case Analyses
            </p>
            <Link href="/dashboard/history"
              className="text-xs text-coral-500 hover:text-coral-700 flex items-center gap-1 transition-colors">
              View all <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
          <div className="grid grid-cols-3 gap-3">
            {stats.recent_cases.slice(0, 3).map((c, i) => {
              const gc =
                c.grade === "Strong"   ? "text-teal-600" :
                c.grade === "Moderate" ? "text-amber-600" : "text-coral-600";
              return (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="card p-4"
                >
                  <p className="text-sm font-medium text-navy-800 line-clamp-2 mb-3 leading-snug">
                    {c.query}
                  </p>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className={`font-display text-2xl font-bold leading-none ${gc}`}>
                        {c.win_prob}%
                      </p>
                      <p className="font-mono text-2xs text-slate-400 uppercase mt-0.5">
                        {c.grade}
                      </p>
                    </div>
                    <Link href="/dashboard/case-mirror"
                      className="text-xs text-coral-500 hover:text-coral-700
                                 flex items-center gap-0.5 transition-colors">
                      Re-analyze <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── FEATURES GRID ──────────────────────────────────── */}
      <div>
        <p className="label mb-5 flex items-center gap-1.5">
          <Zap className="w-3 h-3" /> All Features
        </p>
        <div className="grid grid-cols-4 gap-4">
          {FEATURES.map(({ href, icon: Icon, label, desc, badge, badgeColor, border, gradient }, i) => (
            <Link key={href} href={href}>
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 + i * 0.05, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ y: -3, transition: { duration: 0.2 } }}
                className={`h-full bg-gradient-to-br ${gradient} rounded-2xl
                            border ${border} p-5 cursor-pointer
                            transition-all duration-200 group`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-10 h-10 rounded-xl bg-white shadow-sm
                                  border border-white/80 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-slate-600" />
                  </div>
                  <span className={`badge text-[9px] px-2 py-0.5 rounded-lg border font-mono
                                   tracking-wide uppercase ${badgeColor}`}>
                    {badge}
                  </span>
                </div>
                <p className="font-semibold text-navy-800 text-sm mb-2 leading-snug">
                  {label}
                </p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {desc}
                </p>
                <div className="mt-4 flex items-center gap-1 text-xs font-medium
                               text-slate-400 group-hover:text-slate-600 transition-colors">
                  Open <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </motion.div>
            </Link>
          ))}
        </div>
      </div>

      {/* ── DISCLAIMER ─────────────────────────────────────── */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-50
                      border border-amber-100 text-amber-800">
        <AlertTriangle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
        <p className="text-xs leading-relaxed">
          <strong>Educational Use Only.</strong> AIttorney provides general legal information
          sourced from public Indian court databases. It is not a law firm and does not provide
          legal advice. Always consult a licensed advocate for your specific situation before
          taking any legal action.
        </p>
      </div>
    </div>
  );
}