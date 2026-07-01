"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { historyAPI, casesAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import {
  History, TrendingUp, FileSearch, Clock,
  Loader2, ArrowRight, Trash2
} from "lucide-react";

export default function HistoryPage() {
  const router = useRouter();
  const { setCaseResult, setLiveContext, setCaseQuery } = useStore();
  const [cases,     setCases]     = useState<any[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [openingId, setOpeningId] = useState<string | null>(null);
  const [deletingId,setDeletingId]= useState<string | null>(null);

  useEffect(() => {
    historyAPI.cases()
      .then((r) => {
        // Handle both {cases: [...]} and direct array response
        const data = r.data;
        setCases(Array.isArray(data) ? data : data.cases || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Click case → try to load saved result, fallback to re-analyze
  const openCase = async (item: any) => {
    setOpeningId(item._id);
    try {
      if (item._id) {
        const { data } = await casesAPI.getById(item._id);
        setCaseResult(data);
        setLiveContext(data.analysis || "");
        setCaseQuery(data.query || item.query || "");
        router.push("/dashboard/case-mirror");
      } else {
        throw new Error("No ID");
      }
    } catch {
      // Fallback — just navigate with query pre-filled for re-analysis
      setCaseQuery(item.query || "");
      router.push("/dashboard/case-mirror");
      toast("Case loaded for re-analysis", { icon: "🔄" });
    } finally {
      setOpeningId(null);
    }
  };

  // Delete a case
  const deleteCase = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // prevent row click
    if (!id) return;
    setDeletingId(id);
    try {
      await casesAPI.delete(id);
      setCases((prev) => prev.filter((c) => c._id !== id));
      toast.success("Case deleted");
    } catch {
      toast.error("Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  const stats = {
    total:   cases.length,
    avgProb: cases.length
      ? Math.round(cases.reduce((a, c) => a + (c.win_prob || 0), 0) / cases.length)
      : 0,
    strong:  cases.filter((c) => c.grade === "Strong").length,
  };

  return (
    <div className="space-y-8 page-enter">
      <div>
        <div className="eyebrow mb-3">Persistent Storage · MongoDB</div>
        <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold
                       text-navy-900 tracking-tight mb-3">
          Your <em className="not-italic text-coral-600">History</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Click any case to view saved results instantly. If result isn't available,
          it will open for re-analysis.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { icon: FileSearch, label: "Cases Analyzed",  value: stats.total,   unit: ""  },
          { icon: TrendingUp, label: "Avg. Win Prob.",  value: stats.avgProb, unit: "%" },
          { icon: Clock,      label: "Strong Cases",    value: stats.strong,  unit: ""  },
        ].map(({ icon: Icon, label, value, unit }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="card p-5"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg bg-coral-50 flex items-center justify-center">
                <Icon className="w-4 h-4 text-coral-500" />
              </div>
              <p className="label">{label}</p>
            </div>
            <p className="font-display text-4xl font-bold text-navy-900">
              {value}{unit}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Cases list */}
      <div className="card p-6">
        <p className="font-semibold text-navy-800 mb-4 flex items-center gap-2">
          <History className="w-4 h-4 text-coral-500" />
          Case Search History
        </p>

        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton h-16 rounded-xl" />
            ))}
          </div>
        ) : cases.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center
                            justify-center mx-auto mb-3">
              <FileSearch className="w-5 h-5 text-slate-400" />
            </div>
            <p className="text-slate-400 text-sm">No case analyses yet.</p>
            <p className="text-slate-300 text-xs mt-1">
              Run a Case Mirror analysis to see history here.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {cases.map((item, i) => {
              const gc =
                item.grade === "Strong"   ? "text-teal-600"  :
                item.grade === "Moderate" ? "text-amber-600" : "text-coral-600";
              const isOpening  = openingId  === item._id;
              const isDeleting = deletingId === item._id;

              return (
                <motion.div
                  key={item._id || i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => !isOpening && !isDeleting && openCase(item)}
                  className="flex flex-col sm:flex-row sm:items-center justify-between
                             p-4 rounded-xl bg-bg2 border border-slate-100
                             hover:border-coral-200 hover:bg-coral-50/20
                             transition-all cursor-pointer group gap-2 sm:gap-0"
                >
                  {/* Left — query + date */}
                  <div className="flex-1 min-w-0 sm:mr-4">
                    <p className="text-sm font-medium text-navy-800 line-clamp-1 mb-1
                                   group-hover:text-coral-700 transition-colors">
                      {item.query}
                    </p>
                    <p className="font-mono text-2xs text-slate-400">
                      {item.created_at
                        ? new Date(item.created_at).toLocaleDateString("en-IN", {
                            day: "numeric", month: "short", year: "numeric",
                          })
                        : "—"}
                      {item.case_type && (
                        <span className="ml-2 text-slate-300">· {item.case_type}</span>
                      )}
                    </p>
                  </div>

                  {/* Right — score + actions */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    {/* Win probability */}
                    <div className="text-right">
                      <p className={`font-display text-2xl font-bold leading-none ${gc}`}>
                        {item.win_prob}%
                      </p>
                      <p className="font-mono text-2xs text-slate-400 mt-0.5 uppercase">
                        {item.grade}
                      </p>
                    </div>

                    {/* View button */}
                    {isOpening ? (
                      <Loader2 className="w-4 h-4 text-coral-400 animate-spin" />
                    ) : (
                      <div className="flex items-center gap-1 text-xs text-coral-400
                                      group-hover:text-coral-600 transition-colors">
                        <ArrowRight className="w-4 h-4" />
                      </div>
                    )}

                    {/* Delete button */}
                    <button
                      onClick={(e) => deleteCase(e, item._id)}
                      disabled={isDeleting || isOpening}
                      className="p-1.5 rounded-lg text-slate-300 hover:text-red-500
                                 hover:bg-red-50 transition-all disabled:opacity-40
                                 flex-shrink-0"
                      title="Delete this case"
                    >
                      {isDeleting
                        ? <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" />
                        : <Trash2 className="w-3.5 h-3.5" />
                      }
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}