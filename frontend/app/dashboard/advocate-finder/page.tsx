"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { Users, Loader2, MapPin, Scale, ExternalLink, Search } from "lucide-react";

const CASE_TYPES = [
  "Consumer Dispute",
  "Cheque Bounce / NI Act §138",
  "Property / Real Estate",
  "Employment / Labour",
  "Family / Matrimonial",
  "Criminal Defense",
  "Cyber Crime",
  "Motor Accident",
  "Rent / Tenancy",
  "Medical Negligence",
];

const LOCATIONS = [
  "Delhi NCR",
  "Mumbai",
  "Bangalore",
  "Chennai",
  "Kolkata",
  "Hyderabad",
  "Pune",
  "Ahmedabad",
  "Jaipur",
  "India (General)",
];

interface RawResult {
  title:   string;
  href:    string;
  snippet: string;
}

export default function AdvocateFinderPage() {
  const [caseType,  setCaseType]  = useState("Consumer Dispute");
  const [location,  setLocation]  = useState("Delhi NCR");
  const [summary,   setSummary]   = useState("");
  const [results,   setResults]   = useState<RawResult[]>([]);
  const [loading,   setLoading]   = useState(false);

  const search = async () => {
    setLoading(true);
    setSummary("");
    setResults([]);
    try {
      const { data } = await api.get("/api/lawyers/find", {
        params: { case_type: caseType, location },
      });
      setSummary(data.summary || "");
      setResults(data.raw_results || []);
      toast.success("Advocates found!");
    } catch {
      toast.error("Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div>
        <div className="eyebrow mb-3">AI-Powered · India Specific</div>
<h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Find an <em className="not-italic text-coral-600">Advocate</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Get AI-curated recommendations for advocates specializing in your case type and location.
        </p>
      </div>

      {/* Search Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div className="card p-6 space-y-4">
          <p className="font-semibold text-navy-800 text-sm">Search Criteria</p>

          <div>
            <label className="label">Case Type</label>
            <select
              value={caseType}
              onChange={(e) => setCaseType(e.target.value)}
              className="input"
            >
              {CASE_TYPES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <label className="label">Location</label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="input"
            >
              {LOCATIONS.map((l) => <option key={l}>{l}</option>)}
            </select>
          </div>

          <motion.button
            onClick={search}
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="btn-primary w-full disabled:opacity-60"
          >
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Searching…
                </span>
              : <span className="flex items-center justify-center gap-2">
                  <Search className="w-4 h-4" /> Find Advocates
                </span>
            }
          </motion.button>

          {/* Disclaimer */}
          <p className="text-xs text-slate-400 leading-relaxed">
            Results are AI-generated from public sources. Always verify credentials
            with the Bar Council of India before engaging an advocate.
          </p>
        </div>

        {/* Results */}
<div className="lg:col-span-2 space-y-4">

          {/* Empty state */}
          {!loading && !summary && (
            <div className="card p-12 flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-slate-300" />
              </div>
              <p className="font-semibold text-slate-400 text-sm">
                Select case type and location to find advocates
              </p>
              <p className="text-slate-300 text-xs mt-1">
                AI searches 18 Indian legal sources for relevant advocates
              </p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="card p-12 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 text-coral-400 animate-spin mb-3" />
              <p className="text-slate-400 text-sm">Searching legal directories…</p>
            </div>
          )}

          <AnimatePresence>
            {summary && !loading && (
              <>
                {/* AI Summary */}
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card p-6"
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Scale className="w-4 h-4 text-coral-500" />
                    <p className="label">
                      AI Recommendations · {caseType} · {location}
                    </p>
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
                    {summary}
                  </p>
                </motion.div>

                {/* Raw search results */}
                {results.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="card p-5"
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <MapPin className="w-4 h-4 text-teal-500" />
                      <p className="label">Source Results</p>
                    </div>
                    <div className="space-y-3">
                      {results.map((r, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: 12 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.06 }}
                          className="p-3 rounded-xl bg-bg2 border border-slate-100
                                     hover:border-slate-200 transition-all"
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1 min-w-0">
                              <p className="font-semibold text-sm text-navy-800 truncate mb-1">
                                {r.title}
                              </p>
                              <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
                                {r.snippet}
                              </p>
                            </div>
                            {r.href && (
                              <a
                                href={r.href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex-shrink-0 p-1.5 rounded-lg text-slate-400
                                           hover:text-coral-600 hover:bg-coral-50 transition-all"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Bar Council note */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="bg-amber-50 border border-amber-100 rounded-2xl p-4"
                >
                  <p className="text-xs text-amber-700 leading-relaxed">
                    <strong>Verification Required:</strong> Always verify an advocate's
                    enrollment number and standing with the Bar Council of India at{" "}
                    <a
                      href="https://www.barcouncilofindia.org"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:text-amber-900"
                    >
                      barcouncilofindia.org
                    </a>{" "}
                    before engaging their services.
                  </p>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}