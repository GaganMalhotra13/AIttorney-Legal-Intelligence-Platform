"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { noticesAPI } from "@/lib/api";
import toast from "react-hot-toast";
import {
  PenLine, Download, Loader2, Copy,
  CheckCheck, AlertTriangle, User, Building2,
  MapPin, Calendar, FileText, Scale, Phone
} from "lucide-react";

const TONES = [
  {
    key:   "Professional",
    label: "Professional",
    desc:  "Formal and measured. Leaves room for goodwill resolution.",
    color: "border-blue-200 bg-blue-50 text-blue-700",
  },
  {
    key:   "Strict",
    label: "Strict",
    desc:  "Firm and assertive. Hard 15-day deadline with legal consequences.",
    color: "border-amber-200 bg-amber-50 text-amber-700",
  },
  {
    key:   "Final Warning",
    label: "Final Warning",
    desc:  "Last chance before legal action. Unambiguous consequences stated.",
    color: "border-coral-200 bg-coral-50 text-coral-700",
  },
];

const NOTICE_TYPES = [
  "Security Deposit Refund",
  "Cheque Bounce (NI Act §138)",
  "Consumer Complaint",
  "Employment / Wrongful Termination",
  "Property Dispute",
  "Deficiency of Service",
  "Non-Payment of Dues",
  "Breach of Contract",
  "Medical Negligence",
  "Cyber Fraud / Online Scam",
  "Landlord-Tenant Dispute",
  "Builder Delay / RERA",
  "Motor Accident Claim",
  "Other",
];

export default function NoticeDrafterPage() {
  // Sender details
  const [senderName,    setSenderName]    = useState("");
  const [senderAddress, setSenderAddress] = useState("");
  const [senderPhone,   setSenderPhone]   = useState("");
  const [senderEmail,   setSenderEmail]   = useState("");

  // Recipient details
  const [recipientName,    setRecipientName]    = useState("");
  const [recipientAddress, setRecipientAddress] = useState("");
  const [recipientDesig,   setRecipientDesig]   = useState("");

  // Case details
  const [noticeType,   setNoticeType]   = useState("Security Deposit Refund");
  const [issueDate,    setIssueDate]    = useState("");
  const [claimAmount,  setClaimAmount]  = useState("");
  const [description,  setDescription]  = useState("");
  const [reliefSought, setReliefSought] = useState("");
  const [deadline,     setDeadline]     = useState("15");

  // Output
  const [tone,    setTone]    = useState("Professional");
  const [output,  setOutput]  = useState("");
  const [loading, setLoading] = useState(false);
  const [copied,  setCopied]  = useState(false);

  const validate = () => {
    if (!senderName.trim())    { toast.error("Sender name is required"); return false; }
    if (!senderAddress.trim()) { toast.error("Sender address is required"); return false; }
    if (!recipientName.trim()) { toast.error("Recipient name is required"); return false; }
    if (!description.trim())   { toast.error("Issue description is required"); return false; }
    if (!reliefSought.trim())  { toast.error("Relief sought is required"); return false; }
    return true;
  };

  const generate = async () => {
    if (!validate()) return;
    setLoading(true);

    // Build rich context for the AI
    const context = `
NOTICE TYPE: ${noticeType}
SENDER: ${senderName}, ${senderAddress}${senderPhone ? `, Phone: ${senderPhone}` : ""}${senderEmail ? `, Email: ${senderEmail}` : ""}
RECIPIENT: ${recipientName}${recipientDesig ? ` (${recipientDesig})` : ""}, ${recipientAddress || "__________, __________"}
INCIDENT DATE: ${issueDate || "____________"}
CLAIM AMOUNT: ${claimAmount ? `₹${claimAmount}` : "as applicable"}
ISSUE: ${description}
RELIEF SOUGHT: ${reliefSought}
RESPONSE DEADLINE: ${deadline} days
    `.trim();

    try {
      const { data } = await noticesAPI.draft(
        context,
        senderName,
        recipientName,
        tone
      );
      setOutput(data.notice);
      toast.success("Notice drafted!");
    } catch {
      toast.error("Draft failed");
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const inputClass = "input text-sm";
  const labelClass = "label mb-1";

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div>
        <div className="eyebrow mb-3">Automated Drafting · PDF Output · Legally Structured</div>
        <h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold
                       text-navy-900 tracking-tight mb-3">
          Legal Notice <em className="not-italic text-coral-600">Drafter</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Fill in the details below. Blank fields will appear as underlined spaces
          in the notice for manual completion. Always verify with a licensed advocate before sending.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ── INPUT PANEL ─────────────────────────────── */}
        <div className="space-y-5">

          {/* Notice Type */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Scale className="w-4 h-4 text-coral-500" /> Notice Details
            </p>
            <div className="space-y-4">
              <div>
                <label className={labelClass}>Notice Type *</label>
                <select
                  value={noticeType}
                  onChange={(e) => setNoticeType(e.target.value)}
                  className={inputClass}
                >
                  {NOTICE_TYPES.map((t) => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>
                    Incident / Issue Date
                    <span className="text-slate-400 font-normal ml-1">(optional)</span>
                  </label>
                  <input
                    type="date"
                    value={issueDate}
                    max={new Date().toISOString().split("T")[0]}
                    onChange={(e) => setIssueDate(e.target.value)}
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>
                    Claim Amount (₹)
                    <span className="text-slate-400 font-normal ml-1">(optional)</span>
                  </label>
                  <input
                    type="number"
                    value={claimAmount}
                    onChange={(e) => setClaimAmount(e.target.value)}
                    placeholder="e.g. 80000"
                    className={inputClass}
                  />
                </div>
              </div>
              <div>
                <label className={labelClass}>Response Deadline (days) *</label>
                <select
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className={inputClass}
                >
                  {["7", "15", "30", "60"].map((d) => (
                    <option key={d} value={d}>{d} days</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Sender Details */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <User className="w-4 h-4 text-teal-500" /> Sender (You / Your Client) *
            </p>
            <div className="space-y-3">
              <div>
                <label className={labelClass}>Full Name *</label>
                <input
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  placeholder="e.g. Ramesh Kumar Sharma"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>Full Address *</label>
                <textarea
                  value={senderAddress}
                  onChange={(e) => setSenderAddress(e.target.value)}
                  placeholder="House No., Street, City, State, PIN Code"
                  rows={2}
                  className={`${inputClass} resize-none`}
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>
                    Phone
                    <span className="text-slate-400 font-normal ml-1">(optional)</span>
                  </label>
                  <input
                    value={senderPhone}
                    onChange={(e) => setSenderPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>
                    Email
                    <span className="text-slate-400 font-normal ml-1">(optional)</span>
                  </label>
                  <input
                    type="email"
                    value={senderEmail}
                    onChange={(e) => setSenderEmail(e.target.value)}
                    placeholder="you@email.com"
                    className={inputClass}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Recipient Details */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-amber-500" /> Recipient (Other Party) *
            </p>
            <div className="space-y-3">
              <div>
                <label className={labelClass}>Full Name / Company Name *</label>
                <input
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  placeholder="e.g. ABC Builders Pvt. Ltd. / Mr. Suresh Landlord"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>
                  Designation / Role
                  <span className="text-slate-400 font-normal ml-1">(optional)</span>
                </label>
                <input
                  value={recipientDesig}
                  onChange={(e) => setRecipientDesig(e.target.value)}
                  placeholder="e.g. Managing Director, Landlord, Store Manager"
                  className={inputClass}
                />
              </div>
              <div>
                <label className={labelClass}>
                  Address
                  <span className="text-slate-400 font-normal ml-1">
                    (leave blank to add later)
                  </span>
                </label>
                <textarea
                  value={recipientAddress}
                  onChange={(e) => setRecipientAddress(e.target.value)}
                  placeholder="House No., Street, City, State, PIN Code"
                  rows={2}
                  className={`${inputClass} resize-none`}
                />
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
                <label className={labelClass}>Describe the Issue / Grievance *</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g. I vacated the rented premises on 15/03/2025 after giving 30 days written notice. The landlord has not returned the security deposit of ₹80,000 despite repeated requests over the past 4 months."
                  rows={4}
                  className={`${inputClass} resize-none`}
                />
              </div>
              <div>
                <label className={labelClass}>Relief / Demand Sought *</label>
                <textarea
                  value={reliefSought}
                  onChange={(e) => setReliefSought(e.target.value)}
                  placeholder="e.g. Return of security deposit of ₹80,000 along with interest at 18% per annum from the date of vacation, failing which legal proceedings will be initiated."
                  rows={3}
                  className={`${inputClass} resize-none`}
                />
              </div>
            </div>
          </div>

          {/* Tone */}
          <div className="card p-5">
            <p className="font-semibold text-navy-800 text-sm mb-4 flex items-center gap-2">
              <Scale className="w-4 h-4 text-slate-500" /> Legal Tone *
            </p>
            <div className="space-y-2">
              {TONES.map(({ key, label, desc, color }) => (
                <button
                  key={key}
                  onClick={() => setTone(key)}
                  className={`w-full text-left p-3 rounded-xl border transition-all
                              ${tone === key
                                ? color
                                : "bg-bg2 border-slate-100 text-slate-600 hover:border-slate-200"}`}
                >
                  <p className="font-semibold text-sm">{label}</p>
                  <p className="text-xs mt-0.5 opacity-70">{desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Generate */}
          <motion.button
            onClick={generate}
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="btn-primary w-full py-3.5 text-base disabled:opacity-60"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Drafting Notice…
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <PenLine className="w-4 h-4" /> Generate Legal Notice
              </span>
            )}
          </motion.button>
        </div>

        {/* ── OUTPUT PANEL ────────────────────────────── */}
        <div className="card p-6 flex flex-col min-h-[600px]">
          <div className="flex items-center justify-between mb-4">
            <p className="font-semibold text-navy-800 text-sm flex items-center gap-2">
              <FileText className="w-4 h-4 text-coral-500" /> Generated Notice
            </p>
            {output && (
              <div className="flex gap-2">
                <button
                  onClick={copy}
                  className="btn-ghost text-xs flex items-center gap-1.5"
                >
                  {copied
                    ? <CheckCheck className="w-3.5 h-3.5 text-teal-500" />
                    : <Copy className="w-3.5 h-3.5" />}
                  {copied ? "Copied!" : "Copy"}
                </button>
                <a
                  href={`data:text/plain;charset=utf-8,${encodeURIComponent(output)}`}
                  download={`Legal_Notice_${noticeType.replace(/\s+/g, "_")}_${senderName || "Draft"}.txt`}
                  className="btn-ghost text-xs flex items-center gap-1.5"
                >
                  <Download className="w-3.5 h-3.5" /> Download
                </a>
              </div>
            )}
          </div>

          {!output && !loading && (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-12">
              <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center
                              justify-center mb-4">
                <PenLine className="w-6 h-6 text-slate-300" />
              </div>
              <p className="text-slate-400 text-sm font-medium">
                Fill in the details and generate your notice
              </p>
              <p className="text-slate-300 text-xs mt-1 max-w-xs">
                Blank optional fields will appear as underlined spaces
                in the final notice for manual completion later
              </p>
            </div>
          )}

          {loading && (
            <div className="flex-1 flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 text-coral-400 animate-spin mb-3" />
              <p className="text-slate-400 text-sm">Drafting your legal notice…</p>
            </div>
          )}

          {output && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex-1 overflow-y-auto"
            >
              {/* Watermark disclaimer */}
              <div className="flex items-center gap-2 mb-3 p-2 rounded-lg
                              bg-amber-50 border border-amber-100">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                <p className="text-xs text-amber-700">
                  Fill in any <span className="font-mono font-bold">__________</span> blanks
                  before sending. Verify with a licensed advocate.
                </p>
              </div>

              {/* Notice output — styled like a real legal document */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                <pre className="font-mono text-xs text-slate-800 whitespace-pre-wrap
                                leading-relaxed">
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