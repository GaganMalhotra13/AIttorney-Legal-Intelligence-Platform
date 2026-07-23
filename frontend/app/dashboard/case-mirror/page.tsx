"use client";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion, AnimatePresence } from "framer-motion";
import { casesAPI, brainAPI, CaseRequest } from "@/lib/api";
import { useStore } from "@/store/useStore";
import ModulePanel, { MODULES } from "@/components/features/ModulePanel";
import toast from "react-hot-toast";
import {
  Search, Zap, Scale, Clock, TrendingUp, ExternalLink,
  ChevronDown, ChevronUp, Loader2, CheckCircle2,
  AlertTriangle, Shield, FileText, Users, MapPin,
  DollarSign, Sword, ListChecks, Gavel, Navigation2,
  BarChart2, BookOpen, Siren, Handshake, Timer, GitCompare
} from "lucide-react";

const CASE_TYPES = [
  "Consumer Dispute", "Cheque Bounce (NI Act §138)", "Employment / Labour",
  "Property / Real Estate", "Landlord / Tenant", "Family / Matrimonial",
  "Motor Accident", "Cyber Crime / Online Fraud", "Criminal / FIR",
  "Medical Negligence", "Contract Breach", "Other",
];

const EXAMPLES = [
  "Landlord won't return ₹80,000 deposit after 4 months",
  "Fired the day after filing a harassment complaint",
  "Received a bounced cheque of ₹3.5 lakhs from supplier",
  "Builder 2 years late on flat, now demanding more money",
  "Online store sent fake product, ignoring refund requests",
  "UPI fraud — ₹45,000 transferred to scammer",
];

const MODULES_LIST = [
  { key: "opponent",     icon: Sword,       label: "Opponent Analysis",   desc: "What the other side will argue" },
  { key: "evidence",     icon: ListChecks,  label: "Evidence Checklist",  desc: "Exact documents to gather" },
  { key: "settlement",   icon: DollarSign,  label: "Settlement Estimate", desc: "Realistic ₹ range" },
  { key: "jurisdiction", icon: Navigation2, label: "Jurisdiction Guide",  desc: "Which court to file in" },
  { key: "timeline",     icon: BarChart2,   label: "Case Timeline",       desc: "Strength at each stage" },
  { key: "brief",        icon: BookOpen,    label: "Legal Brief",         desc: "Structured advocate draft" },
  { key: "fir",          icon: Siren,       label: "FIR Draft",           desc: "Police complaint + IPC sections" },
  { key: "mediation",    icon: Handshake,   label: "Mediation Script",    desc: "Pre-litigation negotiation" },
  { key: "limitation",   icon: Timer,       label: "Limitation Check",    desc: "Filing deadline math" },
  { key: "compare",      icon: GitCompare,  label: "Case Comparator",     desc: "Your facts vs. precedents" },
];

function ScoreGauge({ prob, grade }: { prob: number; grade: string }) {
  const color = grade === "Strong" ? "#0FBFAA" : grade === "Moderate" ? "#F59E0B" : "#E8523A";
  const fill  = (prob / 100) * 163;
  return (
    <div className="flex flex-col items-center">
      <svg width="130" height="76" viewBox="0 0 130 76" style={{ overflow: "visible" }}>
        <path d="M 10 72 A 55 55 0 0 1 120 72" fill="none" stroke="#EEECEA" strokeWidth="10" strokeLinecap="round" />
        <motion.path
          d="M 10 72 A 55 55 0 0 1 120 72" fill="none" stroke={color} strokeWidth="10"
          strokeLinecap="round" strokeDasharray={`${fill} 163`}
          initial={{ strokeDasharray: "0 163" }}
          animate={{ strokeDasharray: `${fill} 163` }}
          transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
        />
        <text x="65" y="66" textAnchor="middle" fontFamily="Bricolage Grotesque, sans-serif"
          fontSize="26" fontWeight="800" fill={color}>{prob}%</text>
        <text x="65" y="78" textAnchor="middle" fontFamily="JetBrains Mono, monospace"
          fontSize="8" fill="#948E84" letterSpacing="2">{grade.toUpperCase()}</text>
      </svg>
    </div>
  );
}


export default function CaseMirrorPage() {

const {
  caseResult, setCaseResult,
  setLiveContext, liveContext,
  clearModules,
  caseQuery,
  setCaseQuery,
  caseType, setCaseType,
  claimAmt, setClaimAmt,
  location, setLocation,
  activeModule, setActiveModule,
} = useStore();

const [localQuery, setLocalQuery] = useState(caseQuery);
const [incDate, setIncDate] = useState("");
const [loading, setLoading] = useState(false);
const [showBreakdown, setShowBreakdown] = useState(false);

// useEffect(() => {
//   setLocalQuery(caseQuery);
// }, [caseQuery]);

const analyze = async () => {
  const currentQuery = localQuery.trim();
  if (!currentQuery) { toast.error("Please describe your situation"); return; }
  setCaseQuery(localQuery); // sync to store before API call
  setLoading(true);
  setCaseResult(null);
  clearModules();
  try {
    const { data } = await casesAPI.analyze({
      query:         localQuery,  // use current typed value
      case_type:     caseType,
      claim_amt:     claimAmt,
      location,
      incident_date: incDate,
      language:      "English",
    });
    setCaseResult(data);
    setLiveContext(
      data.sources?.map((s: any) => `${s.title || ""}\n${s.body || ""}`).join("\n\n") || ""
    );
    toast.success("Analysis complete!");
  } catch (e: any) {
    toast.error(e.response?.data?.detail || "Analysis failed");
  } finally {
    setLoading(false);
  }
};

  const handleClear = () => {
    setLocalQuery("");
    setCaseQuery("");
    setCaseResult(null);
    clearModules();
    setIncDate("");
  };

  const prob  = caseResult?.win_prob  ?? 0;
  const grade = caseResult?.grade     ?? "Moderate";
  const pos   = caseResult?.score_data?.positive_factors ?? [];
  const neg   = caseResult?.score_data?.negative_factors ?? [];

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div className="min-w-0">
          <div className="eyebrow mb-3">Legal Research Terminal · 11 Distinct Modules · 18 Sources</div>
          <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight leading-tight mb-3">
            What's Your <em className="not-italic text-coral-600">Legal Situation?</em>
          </h1>
          <p className="text-slate-500 text-sm leading-relaxed max-w-2xl">
            Describe your problem in plain language. Get win probability, applicable laws,
            opponent analysis, evidence checklist, settlement range — all from 18 live Indian legal databases.
          </p>
        </div>
        {(localQuery.trim() || caseResult) && (
          <button
            type="button"
            onClick={handleClear}
            className="btn-ghost text-xs text-coral-600 self-start sm:self-end"
          >
            ↺ Start Fresh
          </button>
        )}
      </div>

      {/* Search Hero */}
      <motion.div
        initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
        className="bg-surface rounded-3xl border border-slate-200 shadow-card-md overflow-hidden"
      >
        {/* Gradient top stripe */}
        <div className="h-1 bg-gradient-to-r from-coral-500 via-amber-400 to-teal-500" />

        <div className="p-8">
          <div className="flex items-start justify-between gap-2 mb-4">
            <div className="flex items-center gap-2">
              <span className="font-mono text-2xs tracking-widest uppercase text-coral-500">
                Describe your situation in plain language
              </span>
              <div className="h-px w-12 bg-gradient-to-r from-coral-100 to-transparent" />
            </div>
           
            <span className="font-mono text-2xs text-teal-500 flex items-center gap-1.5">
              <Shield className="w-3 h-3" /> PII Auto-Redacted
            </span>
          </div>

          <textarea
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            onBlur={() => setCaseQuery(localQuery)}
            placeholder="e.g. 'My landlord refuses to return ₹50,000 deposit. I vacated with 30-day written notice 3 months ago. He won't respond to calls or WhatsApp.'"
            rows={3}

className="w-full bg-white border border-slate-100/70 rounded-xl px-4 py-3
           shadow-[0_1px_2px_rgba(15,23,42,0.03)]
           hover:border-slate-200/70
           focus:border-slate-200
           focus:shadow-[0_2px_10px_rgba(15,23,42,0.05)]
           outline-none focus:outline-none focus:ring-0
           resize-none text-navy-800 text-base leading-relaxed
           placeholder:text-slate-300 font-body
           transition-all duration-200"


            onKeyDown={(e) => { if (e.key === "Enter" && e.metaKey) analyze(); }}
          />

          {/* Quick examples */}
          <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-100">
{EXAMPLES.slice(0, 4).map((ex) => (
  <button
    key={ex}
    onClick={() => {
      setLocalQuery(ex);   // ← updates textarea display instantly
      setCaseQuery(ex);    // ← updates store
    }}
    className="px-3 py-1.5 rounded-full bg-bg text-slate-400 border border-slate-100
               text-xs hover:border-coral-200 hover:text-coral-600 hover:bg-coral-50
               transition-all font-body">
    {ex.slice(0, 40)}{ex.length > 40 ? "…" : ""}
  </button>
))}
          </div>
        </div>

        {/* Config bar */}
<div className="px-4 sm:px-8 py-4 bg-bg2 border-t border-slate-100 flex flex-col sm:flex-row flex-wrap gap-3 sm:items-end">
          <div className="flex-1 min-w-[160px]">
            <label className="label">Case Type</label>
            <select value={caseType} onChange={(e) => setCaseType(e.target.value)}
              className="input py-2 text-xs">
              {CASE_TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
          <div className="w-full sm:w-36">
  <label className="label">Claim (₹)</label>
            <input type="number" value={claimAmt || ""}
              onChange={(e) => setClaimAmt(Number(e.target.value))}
              placeholder="0"
              className="input py-2 text-xs" />
          </div>
          <div className="w-full sm:w-40">
  <label className="label">Incident Date</label>
<input
  type="date"
  value={incDate}
  onChange={(e) => setIncDate(e.target.value)}
  max={new Date().toISOString().split("T")[0]}   // ← today's date as max
  className="input py-2 text-xs"
/>          </div>
          <motion.button
            onClick={analyze} disabled={loading}
            whileHover={{ scale: 1.02, y: -1 }} whileTap={{ scale: 0.98 }}
className="btn-primary h-9 px-6 text-sm disabled:opacity-60 disabled:cursor-not-allowed w-full sm:w-auto"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Analyzing…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Search className="w-3.5 h-3.5" /> Analyze
              </span>
            )}
          </motion.button>
        </div>
      </motion.div>

      {/* Loading state */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="bg-surface rounded-2xl border border-slate-100 shadow-card p-8"
          >
            <div className="flex items-center gap-4 mb-6">
              <div className="w-10 h-10 rounded-xl bg-coral-50 flex items-center justify-center">
                <Loader2 className="w-5 h-5 text-coral-500 animate-spin" />
              </div>
              <div>
                <p className="font-semibold text-navy-800">Analyzing your case…</p>
                <p className="text-slate-400 text-sm">Querying 18 Indian legal databases</p>
              </div>
            </div>
            <div className="space-y-3">
              {[
                "Searching 18 Indian legal sources via 5 strategies…",
                "Running 28-signal scoring engine…",
                "Identifying applicable laws…",
                "Synthesizing full analysis…",
              ].map((step, i) => (
                <div key={step} className="flex items-center gap-3">
                  <motion.div
                    initial={{ scale: 0 }} animate={{ scale: 1 }}
                    transition={{ delay: i * 0.3, ease: [0.16, 1, 0.3, 1] }}
                    className="w-1.5 h-1.5 rounded-full bg-coral-400 flex-shrink-0"
                  />
                  <span className="text-sm text-slate-400">{step}</span>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results */}
      <AnimatePresence>
        {caseResult && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ ease: [0.16, 1, 0.3, 1] }}
            className="space-y-6"
          >
            {/* Scorecard */}
<div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
              {/* Win probability */}
              <motion.div
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="card p-5 text-center"
              >
                <p className="label text-center mb-3">Win Probability</p>
                <ScoreGauge prob={prob} grade={grade} />
                <p className="text-xs text-slate-400 mt-2 font-mono">
                  {caseResult.score_data?.confidence} Confidence
                  · {(pos.length + neg.length)} signals
                </p>
              </motion.div>

              {/* Resolution */}
              <motion.div
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.10 }}
                className="card p-5"
              >
                <p className="label mb-3 flex items-center gap-1.5">
                  <Clock className="w-3 h-3" /> Avg. Resolution
                </p>
                <p className="font-display text-4xl font-bold text-navy-900 leading-none mb-1">
                  ~{caseResult.score_data?.resolution_days}
                </p>
                <p className="font-mono text-2xs text-slate-400 uppercase tracking-widest mb-3">Days</p>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {caseResult.score_data?.resolution_label}
                </p>
                <div className="mt-4 h-1 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-amber-400 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, (caseResult.score_data?.resolution_days || 0) / 6)}%` }}
                    transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
                  />
                </div>
              </motion.div>

              {/* Legal Position */}
              <motion.div
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15 }}
                className="card p-5"
              >
                <p className="label mb-3 flex items-center gap-1.5">
                  <Scale className="w-3 h-3" /> Legal Position
                </p>
                <p className={`font-display text-3xl font-bold leading-none mb-2
                  ${grade === "Strong" ? "text-teal-600" : grade === "Moderate" ? "text-amber-600" : "text-coral-600"}`}>
                  {grade}
                </p>
                <p className="text-xs text-slate-400">
                  {pos.length} strengthening · {neg.length} weakening
                </p>
                <div className="mt-4 h-1 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full ${grade === "Strong" ? "bg-teal-400" : grade === "Moderate" ? "bg-amber-400" : "bg-coral-400"}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${prob}%` }}
                    transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.4 }}
                  />
                </div>
                <button
                  onClick={() => setShowBreakdown(!showBreakdown)}
                  className="mt-3 text-xs text-coral-500 hover:text-coral-700 flex items-center gap-1 transition-colors"
                >
                  {showBreakdown ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  {showBreakdown ? "Hide" : "Show"} breakdown
                </button>
              </motion.div>

              {/* Sources */}
              <motion.div
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.20 }}
                className="card p-5"
              >
                <p className="label mb-3 flex items-center gap-1.5">
                  <Zap className="w-3 h-3" /> Sources Retrieved
                </p>
                <p className="font-display text-4xl font-bold text-navy-900 leading-none mb-1">
                  {caseResult.sources?.length || 0}
                </p>
                <p className="text-xs text-slate-400 mb-3">Across 18 legal databases</p>
                <p className="font-mono text-2xs text-teal-500 uppercase tracking-wide">
                  {caseResult.score_data?.resolution_label?.split("—")[0] || "Live"}
                </p>
              </motion.div>
            </div>

            {/* Score breakdown */}
            <AnimatePresence>
              {showBreakdown && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="bg-surface rounded-2xl border border-slate-100 shadow-card p-6">
                    <p className="font-semibold text-navy-800 text-sm mb-4">
                      Transparent Scoring Breakdown — 28 Signal Heuristic Engine
                    </p>
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <p className="label mb-3 text-teal-500">Strengthening Factors</p>
                        {pos.length === 0
                          ? <p className="text-xs text-slate-400">No positive signals detected</p>
                          : pos.map((f: string, i: number) => {
                            const parts = f.split("  —  ");
                            return (
                              <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-50 last:border-0">
                                <span className="font-mono text-2xs text-teal-600 font-semibold min-w-[44px] pt-0.5">
                                  {parts[0]?.trim()}
                                </span>
                                <span className="text-xs text-slate-600 leading-relaxed">{parts[1]?.trim()}</span>
                              </div>
                            );
                          })
                        }
                      </div>
                      <div>
                        <p className="label mb-3 text-coral-500">Weakening Factors</p>
                        {neg.length === 0
                          ? <p className="text-xs text-slate-400">No negative signals detected</p>
                          : neg.map((f: string, i: number) => {
                            const parts = f.split("  —  ");
                            return (
                              <div key={i} className="flex items-start gap-3 py-2 border-b border-slate-50 last:border-0">
                                <span className="font-mono text-2xs text-coral-600 font-semibold min-w-[44px] pt-0.5">
                                  {parts[0]?.trim()}
                                </span>
                                <span className="text-xs text-slate-600 leading-relaxed">{parts[1]?.trim()}</span>
                              </div>
                            );
                          })
                        }
                      </div>
                    </div>
                    <p className="text-2xs text-slate-400 mt-4 font-mono">
                      Keyword-weighted heuristic based on typical Indian court outcomes. Not a statistical model.
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Laws + Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  <div className="card p-5">
  <p className="label mb-3 flex items-center gap-1.5">
    <Scale className="w-3 h-3" /> Applicable Laws
  </p>
  <div className="markdown-result">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {caseResult.laws}
    </ReactMarkdown>
  </div>
</div>
             <div className="col-span-2 card p-5">
  <p className="label mb-3 flex items-center gap-1.5">
    <Gavel className="w-3 h-3" /> Full Analysis · Live RAG
  </p>
  <div className="markdown-result">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {caseResult.analysis}
    </ReactMarkdown>
  </div>
</div>
            </div>

            {/* Sources grid */}
            {caseResult.sources?.length > 0 && (
              <div>
                <p className="label mb-3 flex items-center gap-1.5">
                  <ExternalLink className="w-3 h-3" />
                  {caseResult.sources.length} Live Sources — Authority-Ranked
                </p>
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {caseResult.sources.slice(0, 6).map((s: any, i: number) => {
                    const domain = s.href?.split("/")[2]?.replace("www.", "") || "source";
                    const weight = s._weight || 1;
                    return (
                      <motion.a
                        key={i} href={s.href || "#"} target="_blank" rel="noopener noreferrer"
                        whileHover={{ y: -2 }}
                        className="card p-4 block no-underline"
                      >
                        <div className="flex items-center gap-1.5 mb-1.5">
                          {weight === 3 && <span className="text-amber-400 text-xs">⭐</span>}
                          <span className="font-mono text-2xs text-coral-500 uppercase tracking-wide">
                            {domain}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                          {s.title || domain}
                        </p>
                      </motion.a>
                    );
                  })}
                </div>
              </div>
            )}

            {/* AI Modules */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="label">Advanced AI Modules — On Demand</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Each runs a separate focused AI call. Generate only what you need.
                  </p>
                </div>
              </div>

              <div className="bg-surface rounded-2xl border border-slate-100 shadow-card overflow-hidden">
                {/* Module tabs */}
                <div className="flex overflow-x-auto border-b border-slate-100 bg-bg2">
                  {MODULES_LIST.map(({ key, icon: Icon, label }) => (
                    <button
                      key={key}
                      onClick={() => setActiveModule(key)}
className={`flex items-center gap-2 px-3 sm:px-4 py-3 text-xs font-medium whitespace-nowrap
                                  border-b-2 transition-all flex-shrink-0
                                  ${activeModule === key
                                    ? "border-coral-500 text-coral-700 bg-surface"
                                    : "border-transparent text-slate-400 hover:text-slate-600 hover:bg-slate-50"
                                  }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      {label}
                    </button>
                  ))}
                </div>

                {/* Module content */}
                <div className="p-6 min-h-[280px]">
                   <AnimatePresence mode="wait">
    <motion.div
      key={activeModule}
      initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.2 }}
      className="h-full"
    >
      <ModulePanel
        moduleKey={activeModule}
        query={caseQuery}
        caseType={caseType}
        claimAmt={claimAmt}
        liveContext={liveContext}
        scoreData={caseResult?.score_data ?? null}
      />
    </motion.div>
  </AnimatePresence>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Idle state — module preview */}
      {!caseResult && !loading && (
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3"
        >
          {MODULES.map(({ key, icon: Icon, label, desc }, i) => (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
              className="card p-4 text-center"
            >
              <div className="w-9 h-9 rounded-xl bg-coral-50 border border-coral-100 flex items-center justify-center mx-auto mb-3">
                <Icon className="w-4 h-4 text-coral-500" />
              </div>
              <p className="font-mono text-2xs text-coral-500 uppercase tracking-wide mb-1">{label}</p>
              <p className="text-xs text-slate-400 leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </motion.div>
      )}
    </div>
  );
}