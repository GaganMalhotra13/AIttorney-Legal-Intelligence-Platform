"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { trackerAPI } from "@/lib/api";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Calendar, Plus, Loader2, Clock, Scale,
  CheckCircle2, XCircle, AlertCircle,
  ChevronDown, Trash2, X, ListChecks
} from "lucide-react";

const CASE_TYPES = [
  "Consumer Dispute", "Cheque Bounce (NI Act §138)", "Employment / Labour",
  "Property / Real Estate", "Landlord / Tenant", "Criminal / FIR",
  "Motor Accident", "Family / Matrimonial", "Other",
];

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: any }> = {
  upcoming:   { label: "Upcoming",   color: "bg-blue-50 text-blue-600 border-blue-200",   icon: Clock },
  completed:  { label: "Completed",  color: "bg-teal-50 text-teal-600 border-teal-200",   icon: CheckCircle2 },
  postponed:  { label: "Postponed",  color: "bg-amber-50 text-amber-600 border-amber-200", icon: AlertCircle },
  cancelled:  { label: "Cancelled",  color: "bg-red-50 text-red-600 border-red-200",       icon: XCircle },
};

interface CourtDate {
  _id:          string;
  case_title:   string;
  court_name:   string;
  hearing_date: string;
  hearing_time: string;
  case_type:    string;
  notes:        string;
  case_number:  string;
  status:       string;
  preparation:  string;
}

function daysUntil(dateStr: string): number {
  const parts = dateStr.split("/");
  if (parts.length !== 3) return 999;
  const d = new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return Math.ceil((d.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function UrgencyBadge({ dateStr }: { dateStr: string }) {
  const days = daysUntil(dateStr);
  if (days < 0)  return <span className="badge badge-red">Passed</span>;
  if (days === 0) return <span className="badge badge-red">Today</span>;
  if (days <= 3)  return <span className="badge badge-red">{days}d left</span>;
  if (days <= 7)  return <span className="badge badge-amber">{days}d left</span>;
  return <span className="badge badge-slate">{days}d away</span>;
}

export default function CaseTrackerPage() {
  const [dates,     setDates]     = useState<CourtDate[]>([]);
  const [loading,   setLoading]   = useState(true);
  const [adding,    setAdding]    = useState(false);
  const [showForm,  setShowForm]  = useState(false);
  const [expanded,  setExpanded]  = useState<string | null>(null);
  const [form, setForm] = useState({
    case_title: "", court_name: "", hearing_date: "",
    hearing_time: "", case_type: "Consumer Dispute",
    notes: "", case_number: "",
  });

  const load = () =>
    trackerAPI.list()
      .then((r) => setDates(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!form.case_title || !form.court_name || !form.hearing_date) {
      toast.error("Case title, court, and date are required");
      return;
    }
    setAdding(true);
    try {
      await trackerAPI.add(form);
      toast.success("Court date added — AI preparation checklist generated");
      setShowForm(false);
      setForm({
        case_title: "", court_name: "", hearing_date: "",
        hearing_time: "", case_type: "Consumer Dispute",
        notes: "", case_number: "",
      });
      load();
    } catch { toast.error("Failed to add"); }
    finally  { setAdding(false); }
  };

  const handleStatus = async (id: string, status: string) => {
    try {
      await trackerAPI.updateStatus(id, status);
      setDates((prev) => prev.map((d) => d._id === id ? { ...d, status } : d));
      toast.success(`Status updated to ${status}`);
    } catch { toast.error("Update failed"); }
  };

  const handleDelete = async (id: string) => {
    try {
      await trackerAPI.delete(id);
      setDates((prev) => prev.filter((d) => d._id !== id));
      toast.success("Deleted");
    } catch { toast.error("Delete failed"); }
  };

  const upcoming  = dates.filter((d) => d.status === "upcoming");
  const completed = dates.filter((d) => d.status !== "upcoming");

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
<div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <div className="eyebrow mb-3">Court Date Tracker · Checklist Preparation</div>
<h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
            Case <em className="not-italic text-coral-600">Tracker</em>
          </h1>
          <p className="text-slate-500 text-sm">
            Track hearing dates, get propergenerated preparation checklists, and never miss a court date.
          </p>
        </div>
        <motion.button
          onClick={() => setShowForm(!showForm)}
          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
className="btn-primary flex items-center gap-2 w-full sm:w-auto justify-center"
        >
          <Plus className="w-4 h-4" />
          Add Court Date
        </motion.button>
      </div>

      {/* Add form */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="card p-6">
              <div className="flex items-center justify-between mb-5">
                <p className="font-semibold text-navy-800 text-sm flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-coral-500" />
                  New Court Date
                </p>
                <button onClick={() => setShowForm(false)}
                  className="text-slate-400 hover:text-slate-600 transition-colors">
                  <X className="w-4 h-4" />
                </button>
              </div>

<div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="label">Case Title *</label>
                  <input
                    value={form.case_title}
                    onChange={(e) => setForm({ ...form, case_title: e.target.value })}
                    placeholder="e.g. Sharma vs. ABC Builder"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Court / Forum *</label>
                  <input
                    value={form.court_name}
                    onChange={(e) => setForm({ ...form, court_name: e.target.value })}
                    placeholder="e.g. Delhi District Consumer Forum"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Hearing Date * (DD/MM/YYYY)</label>
                  <input
                    value={form.hearing_date}
                    onChange={(e) => setForm({ ...form, hearing_date: e.target.value })}
                    placeholder="15/06/2025"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Time</label>
                  <input
                    value={form.hearing_time}
                    onChange={(e) => setForm({ ...form, hearing_time: e.target.value })}
                    placeholder="10:30 AM"
                    className="input"
                  />
                </div>
                <div>
                  <label className="label">Case Type</label>
                  <select
                    value={form.case_type}
                    onChange={(e) => setForm({ ...form, case_type: e.target.value })}
                    className="input"
                  >
                    {CASE_TYPES.map((t) => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className="label">Case Number (optional)</label>
                  <input
                    value={form.case_number}
                    onChange={(e) => setForm({ ...form, case_number: e.target.value })}
                    placeholder="CC/123/2024"
                    className="input"
                  />
                </div>
              </div>

              <div className="mb-5">
                <label className="label">Notes / Context</label>
                <textarea
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Any specific details about this hearing — what's being argued, documents needed, etc."
                  rows={2}
                  className="input resize-none"
                />
              </div>

<div className="flex flex-col sm:flex-row gap-3">
                <motion.button
                  onClick={handleAdd} disabled={adding}
                  whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                  className="btn-primary disabled:opacity-60 flex items-center gap-2"
                >
                  {adding ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> AI generating checklist…</>
                  ) : (
                    <><Plus className="w-4 h-4" /> Add & Generate Preparation</>
                  )}
                </motion.button>
                <button onClick={() => setShowForm(false)} className="btn-ghost">
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats row */}
<div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: "Upcoming Hearings", value: upcoming.length,  color: "text-coral-600",  bg: "bg-coral-50" },
          { label: "Completed",         value: completed.filter((d) => d.status === "completed").length, color: "text-teal-600", bg: "bg-teal-50" },
          { label: "Total Tracked",     value: dates.length,     color: "text-navy-800",   bg: "bg-slate-50" },
        ].map(({ label, value, color, bg }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className={`card p-5 ${bg} border-0`}
          >
            <p className="label mb-2">{label}</p>
            <p className={`font-display text-4xl font-bold ${color} leading-none`}>{value}</p>
          </motion.div>
        ))}
      </div>

      {/* Date list */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-28 rounded-2xl" />
          ))}
        </div>
      ) : dates.length === 0 ? (
        <div className="card p-16 text-center">
          <Calendar className="w-12 h-12 text-slate-200 mx-auto mb-4" />
          <p className="font-semibold text-slate-400 text-sm">No court dates tracked yet</p>
          <p className="text-slate-300 text-xs mt-1 mb-6">
            Add your first hearing date to get an AI preparation checklist
          </p>
          <button
            onClick={() => setShowForm(true)}
            className="btn-primary mx-auto"
          >
            <Plus className="w-4 h-4" /> Add First Hearing
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Upcoming first */}
          {upcoming.length > 0 && (
            <>
              <p className="label flex items-center gap-1.5">
                <Clock className="w-3 h-3 text-coral-500" /> Upcoming Hearings
              </p>
              {upcoming.map((d, i) => (
                <DateCard
                  key={d._id} date={d} index={i}
                  expanded={expanded === d._id}
                  onToggle={() => setExpanded(expanded === d._id ? null : d._id)}
                  onStatus={handleStatus}
                  onDelete={handleDelete}
                />
              ))}
            </>
          )}

          {/* Past / completed */}
          {completed.length > 0 && (
            <>
              <p className="label mt-6 flex items-center gap-1.5">
                <CheckCircle2 className="w-3 h-3 text-teal-500" /> Past Hearings
              </p>
              {completed.map((d, i) => (
                <DateCard
                  key={d._id} date={d} index={i}
                  expanded={expanded === d._id}
                  onToggle={() => setExpanded(expanded === d._id ? null : d._id)}
                  onStatus={handleStatus}
                  onDelete={handleDelete}
                />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function DateCard({
  date, index, expanded, onToggle, onStatus, onDelete
}: {
  date: CourtDate; index: number; expanded: boolean;
  onToggle: () => void;
  onStatus: (id: string, status: string) => void;
  onDelete: (id: string) => void;
}) {
  const cfg = STATUS_CONFIG[date.status] || STATUS_CONFIG.upcoming;
  const StatusIcon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="card overflow-hidden"
    >
      {/* Main row */}
      <div
        className="p-5 flex items-start gap-4 cursor-pointer"
        onClick={onToggle}
      >
        {/* Date block */}
        <div className="text-center bg-coral-50 border border-coral-100
                        rounded-xl p-3 flex-shrink-0 min-w-[56px]">
          {(() => {
            const parts = date.hearing_date?.split("/") || [];
            return (
              <>
                <p className="font-display text-2xl font-bold text-coral-600 leading-none">
                  {parts[0] || "—"}
                </p>
                <p className="font-mono text-[9px] text-coral-400 uppercase tracking-widest mt-0.5">
                  {parts[1]
                    ? new Date(`2024-${parts[1]}-01`).toLocaleString("en", { month: "short" })
                    : "—"}
                </p>
              </>
            );
          })()}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <p className="font-semibold text-navy-800 text-sm">{date.case_title}</p>
            <span className={`badge text-[9px] px-1.5 py-0.5 rounded-md border ${cfg.color}`}>
              <StatusIcon className="w-2.5 h-2.5 inline mr-0.5" />
              {cfg.label}
            </span>
            <UrgencyBadge dateStr={date.hearing_date} />
          </div>
          <p className="text-xs text-slate-500 mb-1">
            {date.court_name}
            {date.hearing_time && ` · ${date.hearing_time}`}
            {date.case_number  && ` · ${date.case_number}`}
          </p>
          <p className="font-mono text-2xs text-slate-400 uppercase tracking-wide">
            {date.case_type}
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(date._id); }}
            className="p-1.5 rounded-lg text-slate-300 hover:text-red-500
                       hover:bg-red-50 transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
          <ChevronDown
            className={`w-4 h-4 text-slate-300 transition-transform ${expanded ? "rotate-180" : ""}`}
          />
        </div>
      </div>

      {/* Expanded */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-t border-slate-100"
          >
<div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Preparation checklist */}
              {date.preparation && (
                <div>
                  <p className="label mb-3 flex items-center gap-1.5">
                    <ListChecks className="w-3 h-3" />  Preparation Checklist
                  </p>
                  <div className="bg-bg2 rounded-xl p-4 markdown-result">
  <ReactMarkdown remarkPlugins={[remarkGfm]}>
    {date.preparation}
  </ReactMarkdown>
</div>
                </div>
              )}

              {/* Status update + notes */}
              <div className="space-y-4">
                {date.notes && (
                  <div>
                    <p className="label mb-2">Notes</p>
                    <p className="text-xs text-slate-600 leading-relaxed">{date.notes}</p>
                  </div>
                )}
                <div>
                  <p className="label mb-2">Update Status</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(STATUS_CONFIG).map(([key, cfg]) => {
                      const Icon = cfg.icon;
                      return (
                        <button
                          key={key}
                          onClick={() => onStatus(date._id, key)}
                          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg
                                      text-xs font-medium border transition-all
                                      ${date.status === key
                                        ? cfg.color + " shadow-sm"
                                        : "bg-slate-50 text-slate-500 border-slate-100 hover:border-slate-200"
                                      }`}
                        >
                          <Icon className="w-3 h-3" />
                          {cfg.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}