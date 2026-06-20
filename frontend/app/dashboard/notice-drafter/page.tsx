"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { noticesAPI } from "@/lib/api";
import toast from "react-hot-toast";
import { PenLine, Download, Loader2, Copy, CheckCheck } from "lucide-react";

const TONES = [
  { key: "Professional",   label: "Professional",   desc: "Formal, measured, polite. Leaves room for goodwill." },
  { key: "Strict",         label: "Strict",          desc: "Assertive, firm. Hard 15-day deadline." },
  { key: "Final Warning",  label: "Final Warning",   desc: "Last chance. Imminent legal action. No ambiguity." },
];

export default function NoticeDrafterPage() {
  const [context,   setContext]   = useState("");
  const [sender,    setSender]    = useState("");
  const [recipient, setRecipient] = useState("");
  const [tone,      setTone]      = useState("Professional");
  const [output,    setOutput]    = useState("");
  const [loading,   setLoading]   = useState(false);
  const [copied,    setCopied]    = useState(false);

  const generate = async () => {
    if (!context.trim()) { toast.error("Describe the issue first"); return; }
    setLoading(true);
    try {
      const { data } = await noticesAPI.draft(context, sender, recipient, tone);
      setOutput(data.notice);
      toast.success("Notice drafted!");
    } catch { toast.error("Draft failed"); }
    finally { setLoading(false); }
  };

  const copy = async () => {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 page-enter">
      <div>
        <div className="eyebrow mb-3">Automated Drafting · PDF Output</div>
<h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Notice <em className="not-italic text-coral-600">Drafter</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Fill in the details below and get a formally structured legal notice. Not legal advice — always verify with an advocate.
        </p>
      </div>

<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input panel */}
        <div className="space-y-5">
          <div className="card p-6">
            <p className="font-semibold text-navy-800 text-sm mb-5">Notice Parameters</p>

            <div className="space-y-4">
              <div>
                <label className="label">Describe the Issue</label>
                <textarea value={context} onChange={(e) => setContext(e.target.value)}
                  placeholder="Describe the dispute in 2-3 sentences…"
                  rows={4} className="input resize-none" />
              </div>
<div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="label">Sender Name</label>
                  <input value={sender} onChange={(e) => setSender(e.target.value)}
                    placeholder="Your full name" className="input" />
                </div>
                <div>
                  <label className="label">Recipient Name</label>
                  <input value={recipient} onChange={(e) => setRecipient(e.target.value)}
                    placeholder="Other party name" className="input" />
                </div>
              </div>

              <div>
                <label className="label">Legal Tone</label>
                <div className="space-y-2">
                  {TONES.map(({ key, label, desc }) => (
                    <button key={key} onClick={() => setTone(key)}
                      className={`w-full text-left p-3 rounded-xl border transition-all
                                  ${tone === key
                                    ? "bg-coral-50 border-coral-200 text-coral-700"
                                    : "bg-bg2 border-slate-100 text-slate-600 hover:border-slate-200"}`}
                    >
                      <p className="font-semibold text-sm">{label}</p>
                      <p className="text-xs mt-0.5 opacity-70">{desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <motion.button
                onClick={generate} disabled={loading}
                whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
                className="btn-primary w-full py-3 disabled:opacity-60"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" /> Drafting…
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <PenLine className="w-4 h-4" /> Generate Notice
                  </span>
                )}
              </motion.button>
            </div>
          </div>
        </div>

        {/* Output panel */}
        <div className="card p-6 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <p className="font-semibold text-navy-800 text-sm">Generated Draft</p>
            {output && (
              <div className="flex gap-2">
                <button onClick={copy}
                  className="btn-ghost text-xs flex items-center gap-1.5">
                  {copied ? <CheckCheck className="w-3.5 h-3.5 text-teal-500" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? "Copied!" : "Copy"}
                </button>
                <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(output)}`}
                  download={`Notice_${tone}.txt`}
                  className="btn-ghost text-xs flex items-center gap-1.5">
                  <Download className="w-3.5 h-3.5" /> Download
                </a>
              </div>
            )}
          </div>

          {!output && !loading ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                <PenLine className="w-5 h-5 text-slate-300" />
              </div>
              <p className="text-slate-400 text-sm">Your notice will appear here</p>
            </div>
          ) : loading ? (
            <div className="flex-1 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 text-coral-400 animate-spin mb-3" />
              <p className="text-slate-400 text-sm">Drafting your notice…</p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="flex-1 overflow-y-auto"
            >
              <div className="bg-navy-900 rounded-xl p-6 border-l-4 border-coral-500 h-full">
                <pre className="font-mono text-xs text-white/70 whitespace-pre-wrap leading-relaxed">
                  {output}
                </pre>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}