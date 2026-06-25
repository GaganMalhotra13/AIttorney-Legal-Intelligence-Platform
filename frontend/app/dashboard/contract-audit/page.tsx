"use client";
import { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { contractsAPI, api } from "@/lib/api";
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

interface Flag { clause: string; severity: string; description: string; excerpt: string; weight: number; }
interface Chat  { role: "user" | "ai"; content: string; }

export default function ContractAuditPage() {
  const [text,     setText]     = useState("");
  const [filename, setFilename] = useState("");
  const [role,     setRole]     = useState("Employee");
  const [score,    setScore]    = useState<any>(null);
  const [analysis, setAnalysis] = useState("");
  const [docId,    setDocId]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const [chat,     setChat]     = useState<Chat[]>([]);
  const [question, setQuestion] = useState("");
  const [chatLoad, setChatLoad] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // ── File handler — PDF goes to backend, txt read locally ──
  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFilename(file.name);

    if (file.name.toLowerCase().endsWith(".pdf")) {
      try {
        toast.loading("Extracting PDF...", { id: "pdf" });
        const formData = new FormData();
        formData.append("file", file);
        const { data } = await api.post("/api/contracts/extract-pdf", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setText(data.text || "");
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
      setText(content.slice(0, 15000));
      toast.success(`${file.name} loaded — ${content.length.toLocaleString()} chars`);
    };
    reader.readAsText(file);
  };

  const audit = async () => {
    if (!text.trim()) { toast.error("Upload a contract first"); return; }
    setLoading(true);
    setScore(null); setAnalysis(""); setChat([]);
    try {
      const { data } = await contractsAPI.audit(text, role);
      setScore(data.score);
      setAnalysis(data.analysis);
      setDocId(data.doc_id || "");
      toast.success("Audit complete!");
    } catch { toast.error("Audit failed"); }
    finally { setLoading(false); }
  };

  const sendChat = async () => {
    if (!question.trim()) return;
    const q = question;
    setQuestion("");
    setChat((prev) => [...prev, { role: "user", content: q }]);
    setChatLoad(true);
    try {
      const { data } = await contractsAPI.chat(q, text, docId);
      setChat((prev) => [...prev, { role: "ai", content: data.answer }]);
    } catch { toast.error("Chat failed"); }
    finally { setChatLoad(false); }
  };

  const riskColor =
    score?.grade === "HIGH"     ? "text-coral-600" :
    score?.grade === "MODERATE" ? "text-amber-600" : "text-teal-600";

  return (
    <div className="space-y-8 page-enter">
      <div>
        <div className="eyebrow mb-3">Document Intelligence · NLP Scoring</div>
<h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Contract <em className="not-italic text-coral-600">Audit & Chat</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Upload any contract, offer letter, or lease deed. Real clause detection scores your risk.
        </p>
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
            className={`card p-8 flex flex-col items-center justify-center text-center cursor-pointer
                        border-2 border-dashed min-h-[140px] transition-all
                        ${filename
                          ? "border-teal-200 bg-teal-50"
                          : "border-slate-200 hover:border-coral-300 hover:bg-coral-50"}`}
          >
            {filename ? (
              <>
                <CheckCircle2 className="w-8 h-8 text-teal-500 mb-2" />
                <p className="font-semibold text-teal-700 text-sm">{filename}</p>
                <p className="text-teal-500 text-xs mt-1">
                  {text.length.toLocaleString()} characters extracted
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
            <select value={role} onChange={(e) => setRole(e.target.value)} className="input">
              {ROLES.map((r) => <option key={r}>{r}</option>)}
            </select>
          </div>
          <motion.button
            onClick={audit} disabled={loading || !text}
            whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
            className="btn-primary w-full disabled:opacity-60"
          >
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />Analyzing…
                </span>
              : <span className="flex items-center justify-center gap-2">
                  <FileText className="w-4 h-4" />Run Audit
                </span>
            }
          </motion.button>
        </div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {score && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Score + flags */}
           <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

  {/* Risk score */}
  <div className="card p-6 text-center">
                <p className="label mb-4">NLP Risk Score</p>
<p className={`font-display text-4xl sm:text-6xl font-bold leading-none mb-1 ${riskColor}`}>
                  {score.score}
                </p>
                <p className="font-mono text-2xs text-slate-400 uppercase tracking-widest mb-4">
                  / 95 · {score.grade} RISK
                </p>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden mb-3">
                  <motion.div
                    className={`h-full rounded-full ${
                      score.grade === "HIGH"     ? "bg-coral-500" :
                      score.grade === "MODERATE" ? "bg-amber-400" : "bg-teal-500"
                    }`}
                    initial={{ width: 0 }}
                    animate={{ width: `${score.score}%` }}
                    transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
                <p className="text-xs text-slate-400">
                  {score.flag_count} risk clauses · {score.green_flags?.length || 0} protective
                </p>
                {score.green_flags?.length > 0 && (
                  <div className="mt-3 text-left">
                    {score.green_flags.map((gf: string) => (
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
                {score.flags?.length === 0 && (
                  <p className="text-sm text-slate-400 text-center py-8">
                    No risk clauses detected in this contract.
                  </p>
                )}
                <div className="space-y-3 max-h-72 overflow-y-auto">
                  {score.flags?.slice(0, 6).map((flag: Flag, i: number) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="p-3 rounded-xl bg-bg2 border border-slate-100"
                    >
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className={`badge ${
                          flag.severity === "HIGH"   ? "badge-red" :
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
                        <p className="font-mono text-2xs text-slate-400 bg-slate-50 p-2 rounded-lg line-clamp-2">
                          {flag.excerpt}
                        </p>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>

            {/* Gemini analysis */}
           {analysis && (
  <div className="card p-6">
    <p className="label mb-4">AI Deep Analysis · {role} Perspective</p>
    <div className="markdown-result">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {analysis}
      </ReactMarkdown>
    </div>
  </div>
)}

            {/* Chat */}
            <div className="card p-5">
              <p className="label mb-4 flex items-center gap-1.5">
                <MessageSquare className="w-3 h-3" /> Interrogate This Contract
              </p>
              <div className="space-y-3 mb-4 max-h-64 overflow-y-auto">
                {chat.length === 0 && (
                  <p className="text-xs text-slate-400 text-center py-4">
                    Ask anything about this contract — clauses, rights, risks.
                  </p>
                )}
                {chat.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] px-4 py-2.5 rounded-2xl text-sm
  ${msg.role === "user"
    ? "bg-coral-600 text-white rounded-br-sm"
    : "bg-bg2 text-slate-700 border border-slate-100 rounded-bl-sm markdown-result markdown-result-chat"}`}>
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
                {chat.length > 0 && (
                  <button onClick={() => setChat([])} className="btn-ghost px-3">
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