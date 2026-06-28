"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { noticesAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import {
  PenLine, Download, Loader2, Copy,
  CheckCheck, AlertTriangle, User, Building2,
  FileText, Scale
} from "lucide-react";

const TONES = [
  { key: "Professional", label: "Professional", desc: "Formal and measured. Leaves room for goodwill resolution.", color: "border-blue-200 bg-blue-50 text-blue-700" },
  { key: "Strict",       label: "Strict",       desc: "Firm and assertive. Hard deadline with legal consequences.", color: "border-amber-200 bg-amber-50 text-amber-700" },
  { key: "Final Warning",label: "Final Warning",desc: "Last chance before legal action. Unambiguous consequences.", color: "border-coral-200 bg-coral-50 text-coral-700" },
];

const NOTICE_TYPES = [
  "Security Deposit Refund","Cheque Bounce (NI Act §138)","Consumer Complaint",
  "Employment / Wrongful Termination","Property Dispute","Deficiency of Service",
  "Non-Payment of Dues","Breach of Contract","Medical Negligence",
  "Cyber Fraud / Online Scam","Landlord-Tenant Dispute","Builder Delay / RERA",
  "Motor Accident Claim","Other",
];

export default function NoticeDrafterPage() {
  const { notice, setNotice, clearNotice } = useStore();
  const [loading, setLoading] = useState(false);
  const [copied,  setCopied]  = useState(false);

  // ── Local state for all text inputs — prevents blink on keystroke ──
  const [lSenderName,       setLSenderName]       = useState(notice.senderName);
  const [lSenderAddress,    setLSenderAddress]    = useState(notice.senderAddress);
  const [lSenderPhone,      setLSenderPhone]      = useState(notice.senderPhone);
  const [lSenderEmail,      setLSenderEmail]      = useState(notice.senderEmail);
  const [lRecipientName,    setLRecipientName]    = useState(notice.recipientName);
  const [lRecipientAddress, setLRecipientAddress] = useState(notice.recipientAddress);
  const [lRecipientDesig,   setLRecipientDesig]   = useState(notice.recipientDesig);
  const [lDescription,      setLDescription]      = useState(notice.description);
  const [lReliefSought,     setLReliefSought]     = useState(notice.reliefSought);

  // Sync all local state to store (call before generate)
  const syncToStore = () => {
    setNotice({
      senderName:       lSenderName,
      senderAddress:    lSenderAddress,
      senderPhone:      lSenderPhone,
      senderEmail:      lSenderEmail,
      recipientName:    lRecipientName,
      recipientAddress: lRecipientAddress,
      recipientDesig:   lRecipientDesig,
      description:      lDescription,
      reliefSought:     lReliefSought,
    });
  };

  const validate = () => {
    if (!lSenderName.trim())    { toast.error("Sender name is required");       return false; }
    if (!lSenderAddress.trim()) { toast.error("Sender address is required");    return false; }
    if (!lRecipientName.trim()) { toast.error("Recipient name is required");    return false; }
    if (!lDescription.trim())   { toast.error("Issue description is required"); return false; }
    if (!lReliefSought.trim())  { toast.error("Relief sought is required");     return false; }
    return true;
  };

  const generate = async () => {
    if (!validate()) return;
    syncToStore(); // persist everything before API call
    setLoading(true);
    const context = `
NOTICE TYPE: ${notice.noticeType}
SENDER: ${lSenderName}, ${lSenderAddress}${lSenderPhone ? `, Phone: ${lSenderPhone}` : ""}${lSenderEmail ? `, Email: ${lSenderEmail}` : ""}
RECIPIENT: ${lRecipientName}${lRecipientDesig ? ` (${lRecipientDesig})` : ""}, ${lRecipientAddress || "__________"}
INCIDENT DATE: ${notice.issueDate || "__________"}
CLAIM AMOUNT: ${notice.claimAmount ? `₹${notice.claimAmount}` : "as applicable"}
ISSUE: ${lDescription}
RELIEF SOUGHT: ${lReliefSought}
RESPONSE DEADLINE: ${notice.deadline} days
    `.trim();
    try {
      const { data } = await noticesAPI.draft(context, lSenderName, lRecipientName, notice.tone);
      setNotice({ noticeOutput: data.notice });
      toast.success("Notice drafted!");
    } catch { toast.error("Draft failed"); }
    finally { setLoading(false); }
  };

  const handleClear = () => {
    clearNotice();
    setLSenderName(""); setLSenderAddress(""); setLSenderPhone(""); setLSenderEmail("");
    setLRecipientName(""); setLRecipientAddress(""); setLRecipientDesig("");
    setLDescription(""); setLReliefSought("");
    toast.success("Form cleared");
  };

  const copy = async () => {
    await navigator.clipboard.writeText(notice.noticeOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const ic = "input text-sm";
  const lc = "label mb-1";

  return (
    <div className="space-y-8 page-enter">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <div className="eyebrow mb-3">Automated Drafting · Legally Structured</div>
          <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
            Legal Notice <em className="not-italic text-coral-600">Drafter</em>
          </h1>
          <p className="text-slate-500 text-sm">
            Fill in the details below. Blank optional fields appear as
            <span className="font-mono text-slate-700 mx-1">__________</span>
            in the notice. Verify with a licensed advocate before sending.
          </p>
        </div>
        {(notice.noticeOutput || lDescription) && (
          <button onClick={handleClear}             className="btn-ghost text-xs text-coral-600 self-start sm:self-end"
>
            ↺ Start Fresh
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-5">

          {/* Notice Details — selects update store directly (no rapid fire) */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Scale className="w-4 h-4 text-coral-500" /> Notice Details
            </p>
            <div className="space-y-4">
              <div>
                <label className={lc}>Notice Type *</label>
                <select value={notice.noticeType}
                  onChange={(e) => setNotice({ noticeType: e.target.value })} className={ic}>
                  {NOTICE_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={lc}>Incident Date <span className="text-slate-400 font-normal">(optional)</span></label>
                  <input type="date" value={notice.issueDate}
                    max={new Date().toISOString().split("T")[0]}
                    onChange={(e) => setNotice({ issueDate: e.target.value })} className={ic} />
                </div>
                <div>
                  <label className={lc}>Claim Amount ₹ <span className="text-slate-400 font-normal">(optional)</span></label>
                  <input type="number" value={notice.claimAmount}
                    onChange={(e) => setNotice({ claimAmount: e.target.value })}
                    placeholder="e.g. 80000" className={ic} />
                </div>
              </div>
              <div>
                <label className={lc}>Response Deadline *</label>
                <select value={notice.deadline}
                  onChange={(e) => setNotice({ deadline: e.target.value })} className={ic}>
                  {["7","15","30","60"].map((d) => <option key={d} value={d}>{d} days</option>)}
                </select>
              </div>
            </div>
          </div>

          {/* Sender — all text inputs use local state + onBlur */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-teal-500" /> Sender (You / Your Client) *
            </p>
            <div className="space-y-3">
              <div>
                <label className={lc}>Full Name *</label>
                <input value={lSenderName}
                  onChange={(e) => setLSenderName(e.target.value)}
                  onBlur={(e) => setNotice({ senderName: e.target.value })}
                  placeholder="e.g. Ramesh Kumar Sharma" className={ic} />
              </div>
              <div>
                <label className={lc}>Full Address *</label>
                <textarea value={lSenderAddress}
                  onChange={(e) => setLSenderAddress(e.target.value)}
                  onBlur={(e) => setNotice({ senderAddress: e.target.value })}
                  placeholder="House No., Street, City, State, PIN Code"
                  rows={2} className={`${ic} resize-none`} />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={lc}>Phone <span className="text-slate-400 font-normal">(optional)</span></label>
                  <input value={lSenderPhone}
                    onChange={(e) => setLSenderPhone(e.target.value)}
                    onBlur={(e) => setNotice({ senderPhone: e.target.value })}
                    placeholder="+91 98765 43210" className={ic} />
                </div>
                <div>
                  <label className={lc}>Email <span className="text-slate-400 font-normal">(optional)</span></label>
                  <input type="email" value={lSenderEmail}
                    onChange={(e) => setLSenderEmail(e.target.value)}
                    onBlur={(e) => setNotice({ senderEmail: e.target.value })}
                    placeholder="you@email.com" className={ic} />
                </div>
              </div>
            </div>
          </div>

          {/* Recipient */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-amber-500" /> Recipient (Other Party) *
            </p>
            <div className="space-y-3">
              <div>
                <label className={lc}>Full Name / Company Name *</label>
                <input value={lRecipientName}
                  onChange={(e) => setLRecipientName(e.target.value)}
                  onBlur={(e) => setNotice({ recipientName: e.target.value })}
                  placeholder="e.g. ABC Builders Pvt. Ltd." className={ic} />
              </div>
              <div>
                <label className={lc}>Designation / Role <span className="text-slate-400 font-normal">(optional)</span></label>
                <input value={lRecipientDesig}
                  onChange={(e) => setLRecipientDesig(e.target.value)}
                  onBlur={(e) => setNotice({ recipientDesig: e.target.value })}
                  placeholder="e.g. Managing Director, Landlord" className={ic} />
              </div>
              <div>
                <label className={lc}>Address <span className="text-slate-400 font-normal">(leave blank to fill later)</span></label>
                <textarea value={lRecipientAddress}
                  onChange={(e) => setLRecipientAddress(e.target.value)}
                  onBlur={(e) => setNotice({ recipientAddress: e.target.value })}
                  placeholder="House No., Street, City, State, PIN Code"
                  rows={2} className={`${ic} resize-none`} />
              </div>
            </div>
          </div>

          {/* Issue + Relief */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-purple-500" /> Issue & Relief *
            </p>
            <div className="space-y-3">
              <div>
                <label className={lc}>Describe the Issue / Grievance *</label>
                <textarea value={lDescription}
                  onChange={(e) => setLDescription(e.target.value)}
                  onBlur={(e) => setNotice({ description: e.target.value })}
                  placeholder="e.g. I vacated the rented premises on 15/03/2025 after giving 30 days written notice. The landlord has not returned the security deposit of ₹80,000 despite repeated requests over the past 4 months."
                  rows={4} className={`${ic} resize-none`} />
              </div>
              <div>
                <label className={lc}>Relief / Demand Sought *</label>
                <textarea value={lReliefSought}
                  onChange={(e) => setLReliefSought(e.target.value)}
                  onBlur={(e) => setNotice({ reliefSought: e.target.value })}
                  placeholder="e.g. Return of security deposit of ₹80,000 along with interest at 18% per annum, failing which legal proceedings will be initiated."
                  rows={3} className={`${ic} resize-none`} />
              </div>
            </div>
          </div>

          {/* Tone — buttons update store directly */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Scale className="w-4 h-4 text-slate-500" /> Legal Tone *
            </p>
            <div className="space-y-2">
              {TONES.map(({ key, label, desc, color }) => (
                <button key={key} onClick={() => setNotice({ tone: key })}
                  className={`w-full text-left p-3 rounded-xl border transition-all
                    ${notice.tone === key ? color : "bg-bg2 border-slate-100 text-slate-600 hover:border-slate-200"}`}>
                  <p className="font-semibold text-sm">{label}</p>
                  <p className="text-xs mt-0.5 opacity-70">{desc}</p>
                </button>
              ))}
            </div>
          </div>

          <motion.button onClick={generate} disabled={loading}
            whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.99 }}
            className="btn-primary w-full py-3.5 text-base disabled:opacity-60">
            {loading
              ? <span className="flex items-center justify-center gap-2"><Loader2 className="w-4 h-4 animate-spin" /> Drafting Notice…</span>
              : <span className="flex items-center justify-center gap-2"><PenLine className="w-4 h-4" />{notice.noticeOutput ? "Regenerate Notice" : "Generate Legal Notice"}</span>
            }
          </motion.button>
        </div>

        {/* Output panel */}
        <div className="card p-6 flex flex-col min-h-[600px]">
          <div className="flex items-center justify-between mb-4">
            <p className="font-semibold text-navy-800 text-sm flex items-center gap-2">
              <FileText className="w-4 h-4 text-coral-500" /> Generated Notice
            </p>
            {notice.noticeOutput && (
              <div className="flex gap-2">
                <button onClick={copy} className="btn-ghost text-xs flex items-center gap-1.5">
                  {copied ? <CheckCheck className="w-3.5 h-3.5 text-teal-500" /> : <Copy className="w-3.5 h-3.5" />}
                  {copied ? "Copied!" : "Copy"}
                </button>
                <a href={`data:text/plain;charset=utf-8,${encodeURIComponent(notice.noticeOutput)}`}
                  download={`Legal_Notice_${notice.noticeType.replace(/\s+/g,"_")}_${lSenderName||"Draft"}.txt`}
                  className="btn-ghost text-xs flex items-center gap-1.5">
                  <Download className="w-3.5 h-3.5" /> Download
                </a>
              </div>
            )}
          </div>

          {!notice.noticeOutput && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12">
              <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mb-4">
                <PenLine className="w-6 h-6 text-slate-300" />
              </div>
              <p className="text-slate-400 text-sm font-medium">Fill in the details and generate your notice</p>
              <p className="text-slate-300 text-xs mt-1 max-w-xs">
                Blank optional fields appear as <span className="font-mono text-slate-400 mx-1">__________</span> for manual completion
              </p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 text-coral-400 animate-spin mb-3" />
              <p className="text-slate-400 text-sm">Drafting your legal notice…</p>
            </div>
          )}

          {notice.noticeOutput && !loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 overflow-y-auto">
              <div className="flex items-center gap-2 mb-3 p-2 rounded-lg bg-amber-50 border border-amber-100">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                <p className="text-xs text-amber-700">
                  Fill in any <span className="font-mono font-bold">__________</span> blanks before sending. Verify with a licensed advocate.
                </p>
              </div>
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                <pre className="font-mono text-xs text-slate-800 whitespace-pre-wrap leading-relaxed">
                  {notice.noticeOutput}
                </pre>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}