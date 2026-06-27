"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { brainAPI, ScoreData } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Loader2 } from "lucide-react";
import {
  Sword, ListChecks, DollarSign, Navigation2,
  BarChart2, BookOpen, Siren, Handshake, Timer, GitCompare
} from "lucide-react";

export const MODULES = [
  { key: "opponent",     icon: Sword,       label: "Opponent Analysis",   desc: "What the other side will argue" },
  { key: "evidence",     icon: ListChecks,  label: "Evidence Checklist",  desc: "Exact documents to gather" },
  { key: "settlement",   icon: DollarSign,  label: "Settlement Estimate", desc: "Realistic range" },
  { key: "jurisdiction", icon: Navigation2, label: "Jurisdiction Guide",  desc: "Which court to file in" },
  { key: "timeline",     icon: BarChart2,   label: "Case Timeline",       desc: "Strength at each stage" },
  { key: "brief",        icon: BookOpen,    label: "Legal Brief",         desc: "Structured advocate draft" },
  { key: "fir",          icon: Siren,       label: "FIR Draft",           desc: "Police complaint + IPC sections" },
  { key: "mediation",    icon: Handshake,   label: "Mediation Script",    desc: "Pre-litigation negotiation" },
  { key: "limitation",   icon: Timer,       label: "Limitation Check",    desc: "Filing deadline math" },
  { key: "compare",      icon: GitCompare,  label: "Case Comparator",     desc: "Your facts vs. precedents" },
];

interface ModulePanelProps {
  moduleKey:   string;
  query:       string;
  caseType:    string;
  claimAmt:    number;
  liveContext: string;
  scoreData:   ScoreData | null;
}

export default function ModulePanel({
  moduleKey, query, caseType, claimAmt, liveContext, scoreData
}: ModulePanelProps) {
  const [loading, setLoading] = useState(false);
  const { moduleResults, setModule } = useStore();
  const result = moduleResults[moduleKey];
  const mod    = MODULES.find((m) => m.key === moduleKey)!;

  const run = async () => {
    setLoading(true);
    try {
      let res: any;
      switch (moduleKey) {
        case "opponent":
          res = await brainAPI.opponent(query, liveContext);
          break;
        case "evidence":
          res = await brainAPI.evidence(query, caseType);
          break;
        case "settlement":
          res = await brainAPI.settlement(query, claimAmt, caseType, liveContext);
          break;
        case "jurisdiction":
          res = await brainAPI.jurisdiction(query, "India");
          break;
        case "timeline":
          res = await brainAPI.timeline(query, scoreData!, caseType);
          break;
        case "brief":
          res = await brainAPI.brief({
            query,
            live_context:  liveContext,
            score_data:    scoreData!,
            laws_text:     "",
            party_name:    "Complainant",
          });
          break;
        case "fir":
          res = await brainAPI.fir({ query, location: "India" });
          break;
        case "mediation":
          res = await brainAPI.mediation({ query });
          break;
        case "limitation":
          res = await brainAPI.limitation({
            case_type:     caseType,
            incident_date: "Not provided",
            query,
          });
          break;
        case "compare":
          res = await brainAPI.compare(query, liveContext, caseType);
          break;
      }
      setModule(moduleKey, res.data.result);
    } catch {
      toast.error(`${mod.label} failed`);
    } finally {
      setLoading(false);
    }
  };

  // ── Empty state ───────────────────────────────────────────
  if (!result && !loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center py-12 text-center">
        <div className="w-12 h-12 rounded-2xl bg-coral-50 border border-coral-100
                        flex items-center justify-center mb-4">
          <mod.icon className="w-5 h-5 text-coral-500" />
        </div>
        <p className="font-semibold text-navy-800 text-sm mb-1">{mod.label}</p>
        <p className="text-slate-400 text-xs mb-6 max-w-xs">{mod.desc}</p>
        <button onClick={run} className="btn-primary text-sm px-6">
          Generate {mod.label} →
        </button>
      </div>
    );
  }

  // ── Loading state ─────────────────────────────────────────
  if (loading) {
    return (
      <div className="h-full flex flex-col items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-coral-500 animate-spin mb-4" />
        <p className="text-slate-400 text-sm">Generating {mod.label}…</p>
        <div className="mt-4 w-48 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-coral-400 to-coral-600
                          rounded-full animate-shimmer"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      </div>
    );
  }

  // ── Result ────────────────────────────────────────────────
  // ── Result ────────────────────────────────────────────────
return (
  <motion.div
    initial={{ opacity: 0, y: 12 }}
    animate={{ opacity: 1, y: 0 }}
    className="h-full flex flex-col"
  >
    {/* Module header */}
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-coral-50 border border-coral-100
                        flex items-center justify-center">
          <mod.icon className="w-3.5 h-3.5 text-coral-500" />
        </div>
        <p className="font-semibold text-navy-800 text-sm">{mod.label}</p>
      </div>
      <button
        onClick={run}
        className="text-xs text-slate-400 hover:text-coral-600 transition-colors
                   flex items-center gap-1"
      >
        ↺ Regenerate
      </button>
    </div>

    {/* Result — single clean markdown render */}
    <div className="flex-1 overflow-y-auto">
      <div className="p-5 bg-bg2 rounded-xl border border-slate-100 markdown-result">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            li: ({ node, checked, children, ...props }: any) => {
              if (checked !== null && checked !== undefined) {
                return (
                  <li className="flex items-start gap-2 mb-1.5 list-none" {...props}>
                    <span className={`mt-0.5 w-4 h-4 rounded border flex-shrink-0
                                     flex items-center justify-center text-xs
                                     ${checked
                                       ? "bg-teal-500 border-teal-500 text-white"
                                       : "border-slate-300 bg-white"}`}>
                      {checked ? "✓" : ""}
                    </span>
                    <span className="text-sm text-slate-700 leading-relaxed">{children}</span>
                  </li>
                );
              }
              return <li className="mb-1 text-sm text-slate-700" {...props}>{children}</li>;
            },
            h3: ({ children, ...props }: any) => (
              <h3 className="font-bold text-navy-800 text-sm mt-4 mb-2 pb-1
                             border-b border-slate-200 flex items-center gap-1.5" {...props}>
                {children}
              </h3>
            ),
            h2: ({ children, ...props }: any) => (
              <h2 className="font-bold text-navy-900 text-base mt-5 mb-2 pb-1
                             border-b-2 border-coral-200" {...props}>
                {children}
              </h2>
            ),
            strong: ({ children, ...props }: any) => (
              <strong className="font-semibold text-navy-800" {...props}>{children}</strong>
            ),
            p: ({ children, ...props }: any) => (
              <p className="text-sm text-slate-700 leading-relaxed mb-2" {...props}>{children}</p>
            ),
            table: ({ children, ...props }: any) => (
              <div className="overflow-x-auto my-3">
                <table className="w-full text-xs border-collapse rounded-lg overflow-hidden" {...props}>
                  {children}
                </table>
              </div>
            ),
            th: ({ children, ...props }: any) => (
              <th className="bg-navy-900 text-white text-left px-3 py-2 font-semibold text-xs" {...props}>
                {children}
              </th>
            ),
            td: ({ children, ...props }: any) => (
              <td className="border-t border-slate-100 px-3 py-2 text-slate-600" {...props}>
                {children}
              </td>
            ),
          }}
        >
          {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
        </ReactMarkdown>
      </div>
    </div>
  </motion.div>
);
}