"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { analyticsAPI } from "@/lib/api";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from "recharts";
import {
  TrendingUp, Scale, FileText, PenLine,
  Calendar, BarChart2, Award
} from "lucide-react";

const GRADE_COLORS: Record<string, string> = {
  Strong:   "#0FBFAA",
  Moderate: "#F59E0B",
  Weak:     "#E8523A",
};

const PIE_COLORS = ["#0FBFAA", "#F59E0B", "#E8523A", "#5B8DEF", "#A78BFA"];

function StatCard({
  icon: Icon, label, value, sub, color, delay
}: {
  icon: any; label: string; value: string | number;
  sub?: string; color: string; delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, ease: [0.16, 1, 0.3, 1] }}
      className="card p-5"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-4.5 h-4.5" />
        </div>
        <p className="label">{label}</p>
      </div>
      <p className="font-display text-4xl font-bold text-navy-900 leading-none mb-1">
        {value}
      </p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </motion.div>
  );
}

export default function AnalyticsPage() {
  const [data,    setData]    = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    analyticsAPI.overview()
      .then((r) => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const gradeData = data?.grades
    ? Object.entries(data.grades).map(([name, value]) => ({ name, value }))
    : [];

  const weeklyData = data?.weekly_trend || [];

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div>
        <div className="eyebrow mb-3">Personal Analytics · MongoDB Aggregation</div>
        <h1 className="font-display text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Your Legal <em className="not-italic text-coral-600">Analytics</em>
        </h1>
        <p className="text-slate-500 text-sm">
          All metrics computed from your actual usage data via MongoDB aggregation pipelines.
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-4 gap-4">
          {[1,2,3,4].map((i) => (
            <div key={i} className="skeleton h-32 rounded-2xl" />
          ))}
        </div>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-4 gap-4">
            <StatCard
              icon={Scale}       label="Cases Analyzed"
              value={data?.totals?.cases ?? 0}
              sub="Total searches"
              color="bg-coral-50 text-coral-600"
              delay={0.05}
            />
            <StatCard
              icon={TrendingUp}  label="Avg. Win Probability"
              value={`${data?.totals?.avg_win_prob ?? 0}%`}
              sub="Across all cases"
              color="bg-teal-50 text-teal-600"
              delay={0.10}
            />
            <StatCard
              icon={FileText}    label="Contracts Audited"
              value={data?.totals?.audits ?? 0}
              sub="NLP risk scored"
              color="bg-amber-50 text-amber-600"
              delay={0.15}
            />
            <StatCard
              icon={Calendar}    label="Upcoming Hearings"
              value={data?.totals?.upcoming_dates ?? 0}
              sub="Court dates tracked"
              color="bg-blue-50 text-blue-600"
              delay={0.20}
            />
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-3 gap-4">
            {/* Weekly activity */}
            <div className="col-span-2 card p-6">
              <p className="label mb-5 flex items-center gap-1.5">
                <BarChart2 className="w-3 h-3" /> Weekly Case Activity
              </p>
              {weeklyData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={weeklyData} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F4F3EF" />
                    <XAxis
                      dataKey="label"
                      tick={{ fontSize: 11, fontFamily: "JetBrains Mono", fill: "#948E84" }}
                      axisLine={false} tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fontFamily: "JetBrains Mono", fill: "#948E84" }}
                      axisLine={false} tickLine={false}
                      allowDecimals={false}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "#FFFFFF",
                        border: "1px solid #EEECEA",
                        borderRadius: "10px",
                        fontSize: "12px",
                        fontFamily: "Inter, sans-serif",
                        boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                      }}
                    />
                    <Bar dataKey="count" fill="#E8523A" radius={[4, 4, 0, 0]}
                      name="Cases" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[200px] flex items-center justify-center">
                  <p className="text-slate-400 text-sm">No data yet — analyze some cases first</p>
                </div>
              )}
            </div>

            {/* Grade distribution */}
            <div className="card p-6">
              <p className="label mb-5 flex items-center gap-1.5">
                <Award className="w-3 h-3" /> Case Strength
              </p>
              {gradeData.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={140}>
                    <PieChart>
                      <Pie
                        data={gradeData}
                        cx="50%" cy="50%"
                        innerRadius={40} outerRadius={65}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {gradeData.map((entry: any, i: number) => (
                          <Cell
                            key={i}
                            fill={GRADE_COLORS[entry.name] || PIE_COLORS[i % PIE_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: "#FFFFFF",
                          border: "1px solid #EEECEA",
                          borderRadius: "10px",
                          fontSize: "12px",
                          boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-2 mt-2">
                    {gradeData.map((g: any) => (
                      <div key={g.name} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2.5 h-2.5 rounded-full"
                            style={{ background: GRADE_COLORS[g.name] || "#94A3B8" }}
                          />
                          <span className="text-xs text-slate-600">{g.name}</span>
                        </div>
                        <span className="font-mono text-2xs text-slate-400 font-medium">
                          {g.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="h-[200px] flex items-center justify-center">
                  <p className="text-slate-400 text-sm text-center">
                    Analyze cases to see strength distribution
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Recent cases table */}
          {data?.recent_cases?.length > 0 && (
            <div className="card p-6">
              <p className="label mb-4 flex items-center gap-1.5">
                <Scale className="w-3 h-3" /> Recent Case Searches
              </p>
              <div className="space-y-2">
                {data.recent_cases.map((c: any, i: number) => {
                  const gc =
                    c.grade === "Strong"   ? "text-teal-600" :
                    c.grade === "Moderate" ? "text-amber-600" : "text-coral-600";
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.04 }}
                      className="flex items-center justify-between py-3
                                 border-b border-slate-50 last:border-0"
                    >
                      <div className="flex-1 min-w-0 mr-4">
                        <p className="text-sm text-navy-800 truncate font-medium">
                          {c.query}
                        </p>
                        <p className="font-mono text-2xs text-slate-400 mt-0.5">
                          {c.case_type || "General"} ·{" "}
                          {c.created_at
                            ? new Date(c.created_at).toLocaleDateString("en-IN", {
                                day: "numeric", month: "short", year: "numeric",
                              })
                            : "—"}
                        </p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className={`font-display text-xl font-bold leading-none ${gc}`}>
                          {c.win_prob}%
                        </p>
                        <p className="font-mono text-2xs text-slate-400 uppercase mt-0.5">
                          {c.grade}
                        </p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}