// components/features/LandmarkCard.tsx
// Shows scraped landmark judgments with citation counts
"use client";
import { motion } from "framer-motion";
import { ExternalLink, Award, Calendar, Scale } from "lucide-react";

interface Landmark {
  title:      string;
  url:        string;
  court:      string;
  date:       string;
  citations:  number;
  snippet:    string;
  full_text?: string;
}

interface Props {
  landmarks: Landmark[];
}

export default function LandmarkCard({ landmarks }: Props) {
  if (!landmarks?.length) return null;

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className="label flex items-center gap-1.5">
          <Award className="w-3 h-3 text-amber-500" />
          Landmark Judgments — Directly Scraped from IndianKanoon
        </span>
        <span className="badge-amber text-2xs px-2 py-0.5 rounded-md bg-amber-50
                         text-amber-600 border border-amber-200 font-mono text-[9px]
                         tracking-wide uppercase">
          Real Citations
        </span>
      </div>

      <div className="grid gap-3">
        {landmarks.map((lm, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="bg-surface rounded-xl border border-amber-100 p-4
                       hover:border-amber-200 hover:shadow-card transition-all"
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <a
                href={lm.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-sm text-navy-800 hover:text-coral-600
                           transition-colors flex items-start gap-1.5 group"
              >
                <span className="leading-tight">{lm.title}</span>
                <ExternalLink className="w-3 h-3 flex-shrink-0 mt-0.5
                                         opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
              {lm.citations > 0 && (
                <div className="flex-shrink-0 text-right">
                  <p className="font-display text-xl font-bold text-amber-600 leading-none">
                    {lm.citations}
                  </p>
                  <p className="font-mono text-[9px] text-amber-400 uppercase tracking-wide">
                    citations
                  </p>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 mb-2">
              {lm.court && (
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <Scale className="w-3 h-3" /> {lm.court}
                </span>
              )}
              {lm.date && (
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <Calendar className="w-3 h-3" /> {lm.date}
                </span>
              )}
            </div>

            {(lm.full_text || lm.snippet) && (
              <p className="text-xs text-slate-500 leading-relaxed line-clamp-3">
                {lm.full_text?.slice(0, 300) || lm.snippet?.slice(0, 300)}
                {((lm.full_text?.length || 0) > 300 ||
                  (lm.snippet?.length || 0) > 300) && "…"}
              </p>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}