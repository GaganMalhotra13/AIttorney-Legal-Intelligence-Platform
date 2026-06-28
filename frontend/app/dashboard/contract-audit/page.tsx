"use client";
import { useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { contractsAPI, api } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Upload, FileText, Loader2,
  CheckCircle2, MessageSquare, Send, Trash2
} from "lucide-react";

const ROLES = [
  "Employee", "Tenant", "Freelancer / Contractor",
  "Buyer", "Seller", "Service Provider", "Borrower", "Investor",
];

interface Flag {
  clause:      string;
  severity:    string;
  description: string;
  excerpt:     string;
  weight:      number;
}

export default function ContractAuditPage() {
  const { contract, setContract, clearContract } = useStore();
  const [loading,  setLoading]  = useState(false);
  const [question, setQuestion] = useState("");
  const [chatLoad, setChatLoad] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // ── File handler ──────────────────────────────────────────
  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setContract({ filename: file.name });

    if (file.name.toLowerCase().endsWith(".pdf")) {
      try {
        toast.loading("Extracting PDF...", { id: "pdf" });
        const formData = new FormData();
        formData.append("file", file);
        const { data } = await api.post("/api/contracts/extract-pdf", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setContract({ text: data.text || "" });
        toast.success(
          `${file.name} — ${(data.text || "").length.toLocaleString()} chars extracted`,
          { id: "pdf" }
        );
      } catch {
        toast.error("PDF extraction failed", { id: "pdf" });
      }
      return;
    }

    // .txt — read directly in browser
    const reader = new FileReader();
    reader.onload = (ev) => {
      const content = (ev.target?.result as string) || "";
      setContract({ text: content.slice(0, 15000) });
      toast.success(`${file.name} loaded — ${content.length.toLocaleString()} chars`);
    };
    reader.readAsText(file);
  };

  // ── Audit ─────────────────────────────────────────────────
  const audit = async () => {
    if (!contract.text.trim()) { toast.error("Upload a contract first"); return; }
    setLoading(true);
    setContract({ score: null, analysis: "", chat: [] });
    try {
      const { data } = await contractsAPI.audit(contract.text, contract.role);
      setContract({
        score:    data.score,
        analysis: data.analysis,
        docId:    data.doc_id || "",
      });
      toast.success("Audit complete!");
    } catch {
      toast.error("Audit failed");
    } finally {
      setLoading(false);
    }
  };

  // ── Chat ──────────────────────────────────────────────────
  const sendChat = async () => {
    if (!question.trim()) return;
    const q = question;
    setQuestion("");

    // Append user message
    const withUser = [...contract.chat, { role: "user" as const, content: q }];
    setContract({ chat: withUser });
    setChatLoad(true);

    try {
      const { data } = await contractsAPI.chat(q, contract.text, contract.docId);
      setContract({
        chat: [...withUser, { role: "ai" as const, content: data.answer }]
      });
    } catch {
      toast.error("Chat failed");
    } finally {
      setChatLoad(false);
    }
  };

  const riskColor =
    contract.score?.grade === "HIGH"     ? "text-coral-600" :
    contract.score?.grade === "MODERATE" ? "text-amber-600" : "text-teal-600";

  return (
    <div className="space-y-8 page-enter">

      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="eyebrow mb-3">Document Intelligence · NLP Scoring</div>
          <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold
                         text-navy-900 tracking-tight mb-3">
            Contract <em className="not-italic text-coral-600">Audit & Chat</em>
          </h1>
          <p className="text-slate-500 text-sm">
            Upload any contract, offer letter, or lease deed. Real clause detection scores your risk.
          </p>
        </div>
        {(contract.text || contract.score) && (
          <button
            onClick={() => { clearContract(); toast.success("Cleared"); }}
            className="btn-ghost text-xs text-coral-600 self-start sm:self-end"
          >
            ↺ Start Fresh
          </button>
        )}
      </div>

      {/* Upload + config */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <input
            ref={fileRef} type="file" accept=".pdf,.txt"
            className="hidden" onChange={handleFile}
          />
          <div
            onClick={() => fileRef.current?.click()}
            className={`card p-8 flex flex-col items-center justify-center text-center
                        cursor-pointer border-2 border-dashed min-h-[140px] transition-all
                        ${contract.filename
                          ? "border-teal-200 bg-teal-50"
                          : "border-slate-200 hover:border-coral-300 hover:bg-coral-50"}`}
          >
            {contract.filename ? (
              <>
                <CheckCircle2 className="w-8 h-8 text-teal-500 mb-2" />
                <p className="font-semibold text-teal-700 text-sm">{contract.filename}</p>
                <p className="text-teal-500 text-xs mt-1">
                  {contract.text.length.toLocaleString()} characters extracted
                </p>
                <p className="text-teal-400 text-xs mt-1">
                  Click to replace
                </p>
              </>
            ) : (
              <>
                <Upload className="w-8 h-8 text-slate-300 mb-2" />
                <p className="font-semibold text-slate-500 text-sm">Upload Contract PDF or TXT</p>
                <p className="text-slate-400 text-xs mt-1">Click to browse or drag & drop</p>
              </>
            )}
          </div>
        </div>

        <div className="card p-5">
          <p className="label mb-3">Audit Settings</p>
          <div className="mb-4">
            <label className="label">Your Role</label>
            <select
              value={contract.role}
              onChange={(e) => setContract({ role: e.target.value })}
              className="input"
            >
              {ROLES.map((r) => <option key={r}>{r}</option>)}
            </select>
          </div>
          <motion.button
            onClick={audit}
            disabled={loading || !contract.text}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="btn-primary w-full disabled:opacity-60"
          >
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Analyzing…
                </span>
              : <span className="flex items-center justify-center gap-2">
                  <FileText className="w-4 h-4" />
                  {contract.score ? "Re-run Audit" : "Run Audit"}
                </span>
            }
          </motion.button>
        </div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {contract.score && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Score + flags */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

              {/* Risk score */}
              <div className="card p-6 text-center">
                <p className="label mb-4">NLP Risk Score</p>
                <p className={`font-display text-4xl sm:text-6xl font-bold leading-none mb-1 ${riskColor}`}>
                  {contract.score.score}
                </p>
                <p className="font-mono text-2xs text-slate-400 uppercase tracking-widest mb-4">
                  / 95 · {contract.score.grade} RISK
                </p>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-3">
                  <motion.div
                    className={`h-full rounded-full ${
                      contract.score.grade === "HIGH"     ? "bg-coral-500" :
                      contract.score.grade === "MODERATE" ? "bg-amber-400" : "bg-teal-500"
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${contract.score.score}%` }}
                    transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
                <p className="text-xs text-slate-400">
                  {contract.score.flag_count} risk clauses ·{" "}
                  {contract.score.green_flags?.length || 0} protective
                </p>
                {contract.score.green_flags?.length > 0 && (
                  <div className="mt-3 text-left">
                    {contract.score.green_flags.map((gf: string) => (
                      <div key={gf} className="flex items-center gap-1.5 py-0.5">
                        <CheckCircle2 className="w-3 h-3 text-teal-500 flex-shrink-0" />
                        <span className="text-xs text-teal-600">{gf}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Flags */}
              <div className="md:col-span-2 card p-5">
                <p className="label mb-4">Risk Clauses Detected</p>
                {contract.score.flags?.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-8">
                    No risk clauses detected in this contract.
                  </p>
                )}
                <div className="space-y-3 max-h-72 overflow-y-auto">
                  {contract.score.flags?.slice(0, 6).map((flag: Flag, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="p-3 rounded-xl bg-bg2 border border-slate-100"
                    >
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`badge ${
                          flag.severity === "HIGH"   ? "badge-red"   :
                          flag.severity === "MEDIUM" ? "badge-amber" : "badge-slate"
                        }`}>
                          {flag.severity}
                        </span>
                        <span className="font-semibold text-sm text-navy-800">
                          {flag.clause}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mb-1.5">{flag.description}</p>
                      {flag.excerpt && (
                        <p className="font-mono text-2xs text-slate-400 bg-slate-50
                                       p-2 rounded-lg line-clamp-2">
                          {flag.excerpt}
                        </p>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            {/* AI Deep Analysis */}
            {contract.analysis && (
              <div className="card p-6">
                <p className="label mb-4">
                  AI Deep Analysis · {contract.role} Perspective
                </p>
                <div className="space-y-4">
                  {contract.analysis.split(/(?=SEVERITY:)/).filter(Boolean).map((block, i) => {
                    const severityMatch = block.match(/SEVERITY:\s*(HIGH|MEDIUM|LOW)/);
                    const clauseMatch   = block.match(/CLAUSE:\s*([^\n]+)/);
                    const problemMatch  = block.match(/PROBLEM:\s*([\s\S]+?)(?=EXCERPT:|FAIR|$)/);
                    const excerptMatch  = block.match(/EXCERPT:\s*([\s\S]+?)(?=FAIR|$)/);
                    const fairMatch     = block.match(/FAIR VERSION:\s*([\s\S]+?)(?=SEVERITY:|OVERALL|$)/);

                    if (!severityMatch) {
                      return (
                        <div key={i} className="p-4 rounded-xl bg-navy-50 border border-slate-200">
                          <div className="markdown-result">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {block.replace(/OVERALL VERDICT:|TOP PRIORITY TO NEGOTIATE:/g,
                                m => `\n**${m}**`).trim()}
                            </ReactMarkdown>
                          </div>
                        </div>
                      );
                    }

                    const severity = severityMatch[1];
                    const cardColor =
                      severity === "HIGH"   ? "bg-coral-50 border-coral-200"   :
                      severity === "MEDIUM" ? "bg-amber-50 border-amber-200"   :
                                              "bg-teal-50  border-teal-200";
                    const badgeColor =
                      severity === "HIGH"   ? "bg-coral-100 text-coral-700"   :
                      severity === "MEDIUM" ? "bg-amber-100 text-amber-700"   :
                                              "bg-teal-100  text-teal-700";

                    return (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                        className={`rounded-xl border p-4 ${cardColor}`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-md font-mono ${badgeColor}`}>
                            {severity}
                          </span>
                          <span className="font-semibold text-sm text-navy-800">
                            {clauseMatch?.[1]?.trim() || "Clause"}
                          </span>
                        </div>
                        {problemMatch && (
                          <p className="text-xs text-slate-700 leading-relaxed mb-2">
                            {problemMatch[1].trim()}
                          </p>
                        )}
                        {excerptMatch && (
                          <blockquote className="text-xs font-mono text-slate-500 bg-white/60
                                                 border-l-2 border-current pl-3 py-1 my-2 italic">
                            {excerptMatch[1].trim()}
                          </blockquote>
                        )}
                        {fairMatch && (
                          <div className="mt-2 pt-2 border-t border-current/20">
                            <p className="text-xs font-semibold mb-0.5">Fair Version:</p>
                            <p className="text-xs text-slate-600 leading-relaxed">
                              {fairMatch[1].trim()}
                            </p>
                          </div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Chat */}
            <div className="card p-5">
              <p className="label mb-4 flex items-center gap-1.5">
                <MessageSquare className="w-3 h-3" /> Interrogate This Contract
              </p>
              <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                {contract.chat.length === 0 && (
                  <p className="text-xs text-slate-400 text-center py-4">
                    Ask anything about this contract — clauses, rights, risks.
                  </p>
                )}
                {contract.chat.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm
                      ${msg.role === "user"
                        ? "bg-coral-600 text-white rounded-br-sm"
                        : "bg-bg2 text-slate-700 border border-slate-100 rounded-bl-sm markdown-result markdown-result-chat"}`}
                    >
                      {msg.role === "ai"
                        ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                        : msg.content
                      }
                    </div>
                  </div>
                ))}
                {chatLoad && (
                  <div className="flex justify-start">
                    <div className="bg-bg2 border border-slate-100 rounded-2xl rounded-bl-sm px-4 py-2.5">
                      <div className="flex gap-1">
                        {[0, 1, 2].map((i) => (
                          <div
                            key={i}
                            className="w-1.5 h-1.5 bg-slate-300 rounded-full animate-bounce"
                            style={{ animationDelay: `${i * 0.15}s` }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendChat()}
                  placeholder="Ask about any clause…"
                  className="input flex-1"
                />
                <button
                  onClick={sendChat}
                  disabled={chatLoad || !question.trim()}
                  className="btn-primary px-4 disabled:opacity-60"
                >
                  <Send className="w-4 h-4" />
                </button>
                {contract.chat.length > 0 && (
                  <button
                    onClick={() => setContract({ chat: [] })}
                    className="btn-ghost px-3"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}