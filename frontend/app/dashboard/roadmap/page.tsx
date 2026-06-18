"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { Map, Loader2, Clock, Scale, ChevronRight } from "lucide-react";

const JURISDICTIONS = [
  "India (General)", "Delhi NCR", "Maharashtra",
  "Karnataka", "Tamil Nadu", "West Bengal",
  "Gujarat", "Rajasthan", "Other State / UT",
];

const QUICK_REF = [
  { label: "Consumer Forum",  time: "0 – 3 months" },
  { label: "Civil Court",     time: "6 – 18 months" },
  { label: "NI Act §138",     time: "3 – 12 months" },
  { label: "Labour Tribunal", time: "3 – 6 months" },
  { label: "High Court Writ", time: "6 – 24 months" },
  { label: "Lok Adalat",      time: "1 – 2 hearings" },
];

function parseSteps(raw: string) {
  const steps: any[] = [];
  const blocks = raw.split("STEP ").filter(Boolean);
  for (const block of blocks) {
    const lines = block.trim().split("\n").map((l) => l.trim()).filter(Boolean);
    const title    = lines[0]?.replace(/^\d+[.:]\s*/, "") || "";
    const action   = lines.find((l) => l.startsWith("Action:"))?.replace("Action:", "").trim() || "";
    const law      = lines.find((l) => l.startsWith("Law:"))?.replace("Law:", "").trim() || "";
    const timeline = lines.find((l) => l.startsWith("Timeline:"))?.replace("Timeline:", "").trim() || "";
    if (title) steps.push({ title, action, law, timeline });
  }
  return steps;
}

export default function RoadmapPage() {
  const [query,        setQuery]        = useState("");
  const [jurisdiction, setJurisdiction] = useState("India (General)");
  const [steps,        setSteps]        = useState<any[]>([]);
  const [loading,      setLoading]      = useState(false);

  const generate = async () => {
    if (!query.trim()) { toast.error("Describe your situation"); return; }
    setLoading(true);
    setSteps([]);
    try {
      const { data } = await api.post("/api/roadmap/generate", { situation: query, jurisdiction });
      setSteps(parseSteps(data.steps || ""));
      toast.success("Roadmap generated!");
    } catch { toast.error("Generation failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-8 page-enter">
      <div>
        <div className="eyebrow mb-3">Procedural Intelligence · India-Specific</div>
        <h1 className="font-display text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Legal <em className="not-italic text-coral-600">Roadmap</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Get an exact 4-step procedural action plan with applicable laws and timelines.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Input */}
        <div className="space-y-4">
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4">Your Situation</p>
            <textarea value={query} onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. 'Bounced cheque of ₹2 lakhs from business partner…'"
              rows={5} className="input resize-none mb-4" />
            <div className="mb-4">
              <label className="label">Jurisdiction</label>
              <select value={jurisdiction} onChange={(e) => setJurisdiction(e.target.value)}
                className="input">
                {JURISDICTIONS.map((j) => <option key={j}>{j}</option>)}
              </select>
            </div>
            <motion.button onClick={generate} disabled={loading}
              whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
              className="btn-primary w-full disabled:opacity-60">
              {loading
                ? <span className="flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Generating…</span>
                : <span className="flex items-center justify-center gap-2"><Map className="w-4 h-4" /> Generate Roadmap</span>
              }
            </motion.button>
          </div>

          {/* Quick reference */}
          <div className="card p-5">
            <p className="label mb-3 flex items-center gap-1.5"><Clock className="w-3 h-3" /> Typical Timelines</p>
            <div className="space-y-2">
              {QUICK_REF.map(({ label, time }) => (
                <div key={label} className="flex justify-between items-center py-1.5 border-b border-slate-50 last:border-0">
                  <span className="text-xs text-slate-600">{label}</span>
                  <span className="font-mono text-2xs text-coral-500">{time}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Roadmap */}
        <div className="col-span-2">
          <div className="card p-6 h-full">
            <p className="label mb-5 flex items-center gap-1.5"><Map className="w-3 h-3" /> Your 4-Step Action Plan</p>

            {loading && (
              <div className="flex flex-col items-center justify-center py-16">
                <Loader2 className="w-8 h-8 text-coral-400 animate-spin mb-3" />
                <p className="text-slate-400 text-sm">Mapping legal procedures…</p>
              </div>
            )}

            {!loading && steps.length === 0 && (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                  <Map className="w-5 h-5 text-slate-300" />
                </div>
                <p className="text-slate-400 text-sm">Describe your situation and generate a roadmap</p>
              </div>
            )}

            <AnimatePresence>
              {steps.length > 0 && (
                <div className="relative">
                  {/* Vertical line */}
                  <div className="absolute left-5 top-8 bottom-8 w-0.5 bg-gradient-to-b from-coral-200 via-amber-200 to-teal-200" />

                  <div className="space-y-4">
                    {steps.map((step, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.12, ease: [0.16, 1, 0.3, 1] }}
                        className="flex gap-4"
                      >
                        {/* Step number */}
                        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-surface border-2 border-coral-200
                                        flex items-center justify-center z-10 shadow-sm">
                          <span className="font-display font-bold text-coral-600 text-sm">{i + 1}</span>
                        </div>

                        {/* Content */}
                        <div className="flex-1 bg-bg2 rounded-2xl p-4 border border-slate-100 hover:border-slate-200 transition-all">
                          <p className="font-semibold text-navy-800 text-sm mb-2">Step {i + 1}: {step.title}</p>
                          <p className="text-sm text-slate-600 leading-relaxed mb-3">{step.action}</p>
                          <div className="flex flex-wrap gap-2">
                            {step.law && step.law !== "N/A" && (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg
                                             bg-coral-50 border border-coral-100 text-xs text-coral-600 font-mono">
                                <Scale className="w-3 h-3" /> {step.law}
                              </span>
                            )}
                            {step.timeline && (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg
                                             bg-amber-50 border border-amber-100 text-xs text-amber-600 font-mono">
                                <Clock className="w-3 h-3" /> {step.timeline}
                              </span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}