"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { historyAPI, casesAPI, contractsAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import {
  History, TrendingUp, FileSearch, Clock,
  Loader2, ArrowRight, Trash2, Scale,
  FileText, Map, PenLine, Filter
} from "lucide-react";

// ── Type config ───────────────────────────────────────────────
const TYPE_CONFIG: Record<string, {
  icon:  any;
  label: string;
  bg:    string;
  text:  string;
  border:string;
}> = {
  case: {
    icon:   Scale,
    label:  "Case",
    bg:     "bg-coral-50",
    text:   "text-coral-600",
    border: "border-coral-200",
  },
  contract: {
    icon:   FileText,
    label:  "Contract",
    bg:     "bg-blue-50",
    text:   "text-blue-600",
    border: "border-blue-200",
  },
  roadmap: {
    icon:   Map,
    label:  "Roadmap",
    bg:     "bg-teal-50",
    text:   "text-teal-600",
    border: "border-teal-200",
  },
  notice: {
    icon:   PenLine,
    label:  "Notice",
    bg:     "bg-purple-50",
    text:   "text-purple-600",
    border: "border-purple-200",
  },
};

const BADGE_COLORS: Record<string, string> = {
  teal:   "bg-teal-100 text-teal-700 border-teal-200",
  coral:  "bg-coral-100 text-coral-700 border-coral-200",
  amber:  "bg-amber-100 text-amber-700 border-amber-200",
  blue:   "bg-blue-100 text-blue-700 border-blue-200",
  purple: "bg-purple-100 text-purple-700 border-purple-200",
};

interface HistoryItem {
  _id:         string;
  type:        "case" | "contract" | "roadmap" | "notice";
  title:       string;
  subtitle:    string;
  badge:       string;
  badge_color: string;
  route:       string;
  result_id:   string;
  created_at:  string;
}

export default function HistoryPage() {
  const router = useRouter();
  const {
    setCaseResult, setLiveContext, setCaseQuery,
    setContract, setRoadmap,
  } = useStore();

  const [items,      setItems]      = useState<HistoryItem[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [limit,      setLimit]      = useState(10);
  const [filter,     setFilter]     = useState<string>("all");
  const [openingId,  setOpeningId]  = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const load = (l = limit) => {
    setLoading(true);
    historyAPI.all(l)
      .then((r) => setItems(r.data.items || []))
      .catch(() => toast.error("Failed to load history"))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(limit); }, [limit]);

  // ── Navigate to result ────────────────────────────────────
  const openItem = async (item: HistoryItem) => {
    setOpeningId(item._id);
    try {
      if (item.type === "case") {
        try {
          const { data } = await casesAPI.getById(item.result_id);
          setCaseResult(data);
          setLiveContext(data.analysis || "");
          setCaseQuery(data.query || item.title);
        } catch {
          setCaseQuery(item.title);
        }
        router.push("/dashboard/case-mirror");

      } else if (item.type === "contract") {
        try {
          const { data } = await contractsAPI.getById(item.result_id);
          setContract({
            score:    data.score,
            analysis: data.analysis,
            role:     data.role || "Employee",
          });
        } catch {
          // navigate anyway — user can re-upload
        }
        router.push("/dashboard/contract-audit");

      } else if (item.type === "roadmap") {
        try {
          const { data } = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/roadmap/${item.result_id}`,
            { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
          ).then(r => r.json()).then(d => ({ data: d }));
          if (data.steps) {
            setRoadmap({ query: data.situation, steps: parseSteps(data.steps) });
          }
        } catch {
          setRoadmap({ query: item.title });
        }
        router.push("/dashboard/roadmap");

      } else if (item.type === "notice") {
        router.push("/dashboard/notice-drafter");
      }
    } finally {
      setOpeningId(null);
    }
  };

  // Simple step parser (same as roadmap page)
  const parseSteps = (raw: string) => {
    const steps: any[] = [];
    const blocks = raw.split("STEP ").filter(Boolean);
    for (const block of blocks) {
      const lines = block.trim().split("\n").map(l => l.trim()).filter(Boolean);
      const title    = lines[0]?.replace(/^\d+[.:]\s*/, "") || "";
      const action   = lines.find(l => l.startsWith("Action:"))?.replace("Action:", "").trim() || "";
      const law      = lines.find(l => l.startsWith("Law:"))?.replace("Law:", "").trim() || "";
      const timeline = lines.find(l => l.startsWith("Timeline:"))?.replace("Timeline:", "").trim() || "";
      if (title) steps.push({ title, action, law, timeline });
    }
    return steps;
  };

  // ── Delete item ───────────────────────────────────────────
  const deleteItem = async (e: React.MouseEvent, item: HistoryItem) => {
    e.stopPropagation();
    setDeletingId(item._id);
    try {
await historyAPI.delete(item.type, item._id);
      setItems(prev => prev.filter(i => i._id !== item._id));
      toast.success("Deleted");
    } catch {
      toast.error("Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  const filtered = filter === "all"
    ? items
    : items.filter(i => i.type === filter);

  const counts = {
    all:      items.length,
    case:     items.filter(i => i.type === "case").length,
    contract: items.filter(i => i.type === "contract").length,
    roadmap:  items.filter(i => i.type === "roadmap").length,
    notice:   items.filter(i => i.type === "notice").length,
  };

  return (
    <div className="space-y-8 page-enter">

      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="eyebrow mb-3">Persistent Storage </div>
          <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold
                         text-navy-900 tracking-tight mb-3">
            Your <em className="not-italic text-coral-600">Activity History</em>
          </h1>
          <p className="text-slate-500 text-sm">
            All your cases, contracts, roadmaps, and notices — click any to view instantly.
          </p>
        </div>

        {/* Limit picker */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Show</span>
          <select
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            className="input text-xs w-24 py-1.5"
          >
            {[10, 20, 30, 50].map(n => (
              <option key={n} value={n}>Last {n}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { key: "case",     label: "Cases",     icon: Scale,    color: "text-coral-600"  },
          { key: "contract", label: "Contracts",  icon: FileText, color: "text-blue-600"   },
          { key: "roadmap",  label: "Roadmaps",   icon: Map,      color: "text-teal-600"   },
          { key: "notice",   label: "Notices",    icon: PenLine,  color: "text-purple-600" },
        ].map(({ key, label, icon: Icon, color }) => (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <Icon className={`w-4 h-4 ${color}`} />
              <p className="label text-xs">{label}</p>
            </div>
            <p className={`font-display text-3xl font-bold ${color}`}>
              {counts[key as keyof typeof counts]}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-3.5 h-3.5 text-slate-400" />
        {(["all", "case", "contract", "roadmap", "notice"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
              filter === f
                ? "bg-navy-900 text-white border-navy-900"
                : "bg-bg2 text-slate-500 border-slate-200 hover:border-slate-300"
            }`}
          >
            {f === "all" ? `All (${counts.all})` : (
              `${TYPE_CONFIG[f].label} (${counts[f as keyof typeof counts]})`
            )}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="card p-6">
        <p className="font-semibold text-navy-800 mb-5 flex items-center gap-2">
          <History className="w-4 h-4 text-coral-500" />
          Activity Timeline
        </p>

        {loading ? (
          <div className="space-y-3">
            {[1,2,3,4].map(i => (
              <div key={i} className="skeleton h-16 rounded-xl" />
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center
                            justify-center mx-auto mb-4">
              <FileSearch className="w-6 h-6 text-slate-300" />
            </div>
            <p className="text-slate-400 text-sm font-medium">
              {filter === "all" ? "No activity yet" : `No ${filter} history yet`}
            </p>
            <p className="text-slate-300 text-xs mt-1">
              Start using the platform to see your activity here
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <AnimatePresence>
              {filtered.map((item, i) => {
                const cfg       = TYPE_CONFIG[item.type];
                const TypeIcon  = cfg.icon;
                const badgeCls  = BADGE_COLORS[item.badge_color] || BADGE_COLORS.coral;
                const isOpening = openingId  === item._id;
                const isDeleting= deletingId === item._id;

                return (
                  <motion.div
                    key={item._id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ delay: i * 0.03 }}
                    onClick={() => !isOpening && !isDeleting && openItem(item)}
                    className="flex items-center gap-3 p-3 rounded-xl border border-slate-100
                               hover:border-coral-200 hover:bg-coral-50/20 transition-all
                               cursor-pointer group"
                  >
                    {/* Type icon */}
                    <div className={`w-9 h-9 rounded-lg ${cfg.bg} ${cfg.border} border
                                    flex items-center justify-center flex-shrink-0`}>
                      <TypeIcon className={`w-4 h-4 ${cfg.text}`} />
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-0.5">
                        <span className={`text-[9px] font-bold font-mono px-1.5 py-0.5
                                         rounded border uppercase tracking-wide
                                         ${cfg.bg} ${cfg.text} ${cfg.border}`}>
                          {cfg.label}
                        </span>
                        <p className="text-sm font-medium text-navy-800 truncate
                                     group-hover:text-coral-700 transition-colors">
                          {item.title}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-md border
                                         font-mono font-semibold ${badgeCls}`}>
                          {item.badge}
                        </span>
                        <span className="text-2xs text-slate-400 font-mono">
                          {item.subtitle}
                        </span>
                        <span className="text-2xs text-slate-300">·</span>
                        <span className="text-2xs text-slate-400 font-mono">
                          {new Date(item.created_at).toLocaleDateString("en-IN", {
                            day: "numeric", month: "short", year: "numeric",
                          })}
                        </span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {isOpening ? (
                        <Loader2 className="w-4 h-4 text-coral-400 animate-spin" />
                      ) : (
                        <ArrowRight className="w-4 h-4 text-slate-300
                                              group-hover:text-coral-500 transition-colors" />
                      )}
                      <button
                        onClick={(e) => deleteItem(e, item)}
                        disabled={isDeleting || isOpening}
                        className="p-1.5 rounded-lg text-slate-300 hover:text-red-500
                                   hover:bg-red-50 transition-all disabled:opacity-40"
                        title="Delete"
                      >
                        {isDeleting
                          ? <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                          : <Trash2  className="w-3.5 h-3.5" />
                        }
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
}