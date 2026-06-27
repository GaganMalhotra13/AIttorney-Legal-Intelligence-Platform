"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { documentsAPI } from "@/lib/api";
import toast from "react-hot-toast";
import {
  Upload, FolderOpen, Search, Loader2, FileText,
  Tag, Calendar, Users, Trash2, X, CheckCircle2
} from "lucide-react";

interface Doc {
  _id:      string;
  filename: string;
  label:    string;
  snippet?:  string;
  size_bytes: number;
  created_at: string;
  metadata: {
    doc_type:    string;
    parties:     string[];
    key_dates:   string[];
    case_number: string | null;
    court:       string | null;
    summary:     string;
    tags:        string[];
  };
}

const DOC_TYPE_COLORS: Record<string, string> = {
  FIR:      "bg-red-50 text-red-600 border-red-200",
  Contract: "bg-blue-50 text-blue-600 border-blue-200",
  Judgment: "bg-teal-50 text-teal-600 border-teal-200",
  Notice:   "bg-amber-50 text-amber-600 border-amber-200",
  Other:    "bg-slate-100 text-slate-600 border-slate-200",
};

function formatBytes(bytes: number): string {
  if (bytes < 1024)       return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentVaultPage() {
  const [docs,      setDocs]      = useState<Doc[]>([]);
  const [query,     setQuery]     = useState("");
  const [results,   setResults]   = useState<Doc[] | null>(null);
  const [uploading, setUploading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [loading,   setLoading]   = useState(true);
  const [selected,  setSelected]  = useState<Doc | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = () =>
    documentsAPI.list()
      .then((r) => setDocs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file",  file);
    fd.append("label", file.name);
    try {
      await documentsAPI.upload(fd);
      toast.success(`${file.name} uploaded and tagged by AI`);
      load();
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) { setResults(null); return; }
    setSearching(true);
    try {
      const { data } = await documentsAPI.search(query);
      setResults(data);
    } catch {
      toast.error("Search failed");
    } finally {
      setSearching(false);
    }
  };
// Add this function inside DocumentVaultPage component, before return
const highlightSnippet = (snippet: string, query: string) => {
  if (!snippet || !query) return snippet;
  const words = query.split(" ").filter(w => w.length > 2);
  if (words.length === 0) return snippet;

  const regex = new RegExp(`(${words.map(w =>
    w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi");

  const parts = snippet.split(regex);
  return parts.map((part, i) =>
    regex.test(part)
      ? <mark key={i} className="bg-coral-100 text-coral-800 rounded px-0.5 font-medium not-italic">{part}</mark>
      : part
  );
};
  const handleDelete = async (id: string) => {
    try {
      await documentsAPI.delete(id);
      setDocs((prev) => prev.filter((d) => d._id !== id));
      if (selected?._id === id) setSelected(null);
      toast.success("Document deleted");
    } catch {
      toast.error("Delete failed");
    }
  };

  const displayDocs = results ?? docs;

  return (
    <div className="space-y-8 page-enter">
      {/* Header */}
      <div>
        <div className="eyebrow mb-3">Document Intelligence · AI Tagging · Semantic Search</div>
<h1 className="font-display text-2xl sm:text-3xl md:text-4xl font-bold text-navy-900 tracking-tight mb-3">
          Document <em className="not-italic text-coral-600">Vault</em>
        </h1>
        <p className="text-slate-500 text-sm">
          Upload FIRs, court orders, contracts, and judgments. AI automatically extracts
          parties, dates, and case numbers. Search across all your documents semantically.
        </p>
      </div>

      {/* Upload + Search */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Upload zone */}
        <div>
          <input ref={fileRef} type="file"
            accept=".pdf,.txt,.doc,.docx"
            className="hidden" onChange={handleUpload} />
          <div
            onClick={() => !uploading && fileRef.current?.click()}
            className={`card p-8 flex flex-col items-center justify-center
                        text-center cursor-pointer border-2 border-dashed
                        min-h-[140px] transition-all
                        ${uploading
                          ? "border-coral-300 bg-coral-50"
                          : "border-slate-200 hover:border-coral-300 hover:bg-coral-50"
                        }`}
          >
            {uploading ? (
              <>
                <Loader2 className="w-8 h-8 text-coral-500 animate-spin mb-3" />
                <p className="font-semibold text-coral-700 text-sm">
                  AI is tagging your document…
                </p>
                <p className="text-coral-500 text-xs mt-1">
                  Extracting parties, dates, case numbers
                </p>
              </>
            ) : (
              <>
                <Upload className="w-8 h-8 text-slate-300 mb-3" />
                <p className="font-semibold text-slate-600 text-sm">
                  Upload Legal Document
                </p>
                <p className="text-slate-400 text-xs mt-1">
                  PDF, TXT, DOC · Max 10MB · AI auto-tags
                </p>
              </>
            )}
          </div>
        </div>

        {/* Semantic search */}
        <div className="card p-5">
          <p className="label mb-3 flex items-center gap-1.5">
            <Search className="w-3 h-3" /> Semantic Search
          </p>
          <div className="flex gap-2 mb-3">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="e.g. 'cheque bounce case' or 'tenant deposit'"
              className="input flex-1 text-sm"
            />
            <button
              onClick={handleSearch}
              disabled={searching}
              className="btn-primary px-4 disabled:opacity-60"
            >
              {searching
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : <Search className="w-4 h-4" />
              }
            </button>
          </div>
          {results !== null && (
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-400">
                {results.length} result{results.length !== 1 ? "s" : ""} found
              </p>
              <button
                onClick={() => { setResults(null); setQuery(""); }}
                className="text-xs text-coral-500 hover:text-coral-700 flex items-center gap-1"
              >
                <X className="w-3 h-3" /> Clear
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Documents + Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
  {/* Document list */}
  <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
            <p className="label flex items-center gap-1.5">
              <FolderOpen className="w-3 h-3" />
              {results !== null ? "Search Results" : "All Documents"}
              <span className="font-mono text-[10px] bg-slate-100 text-slate-500
                               px-1.5 py-0.5 rounded-md ml-1">
                {displayDocs.length}
              </span>
            </p>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="skeleton h-24 rounded-2xl" />
              ))}
            </div>
          ) : displayDocs.length === 0 ? (
            <div className="card p-12 text-center">
              <FolderOpen className="w-10 h-10 text-slate-200 mx-auto mb-3" />
              <p className="text-slate-400 text-sm font-medium">
                {results !== null ? "No documents match" : "No documents yet"}
              </p>
              <p className="text-slate-300 text-xs mt-1">
                {results !== null
                  ? "Try a different search query"
                  : "Upload your first legal document above"
                }
              </p>
            </div>
          ) : (
            <AnimatePresence>
              {displayDocs.map((doc, i) => {
                const typeColor = DOC_TYPE_COLORS[doc.metadata?.doc_type] || DOC_TYPE_COLORS.Other;
                const isSelected = selected?._id === doc._id;
                return (
                  <motion.div
                    key={doc._id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                    onClick={() => setSelected(isSelected ? null : doc)}
                    className={`card p-4 cursor-pointer transition-all
                                ${isSelected ? "border-coral-300 shadow-card-md" : ""}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center
                                      justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-slate-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <p className="font-semibold text-sm text-navy-800 truncate">
                            {doc.label}
                          </p>
                          {doc.metadata?.doc_type && (
                            <span className={`badge text-[9px] px-1.5 py-0.5 rounded-md
                                            border font-mono ${typeColor}`}>
                              {doc.metadata.doc_type}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 line-clamp-1 mb-2">
                          {doc.metadata?.summary || "No summary"}
                        </p>
                        {results !== null && doc.snippet && (
                            <p className="text-xs font-mono text-coral-600 bg-coral-50 px-2 py-1
                                           rounded-lg mt-1.5 border border-coral-100 line-clamp-2">
                              {doc.snippet}
                            </p>
                          )}

                                
                        <div className="flex items-center gap-3 flex-wrap">
                          {doc.metadata?.parties?.slice(0, 2).map((p) => (
                            <span key={p} className="flex items-center gap-1
                                                     text-2xs text-slate-400 font-mono">
                              <Users className="w-2.5 h-2.5" /> {p}
                            </span>
                          ))}
                          <span className="text-2xs text-slate-400 font-mono">
                            {formatBytes(doc.size_bytes)}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDelete(doc._id); }}
                        className="p-1.5 rounded-lg text-slate-300 hover:text-red-500
                                   hover:bg-red-50 transition-all flex-shrink-0"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
{results !== null && doc.snippet && (
  <div className="mt-2 px-2 py-1.5 rounded-lg bg-coral-50
                  border border-coral-100 text-xs text-slate-600
                  leading-relaxed font-mono">
    <span className="text-coral-500 font-sans font-semibold mr-1">
      Found:
    </span>
    {highlightSnippet(doc.snippet, query)}
  </div>
)}
                    {/* Tags */}
                    {doc.metadata?.tags?.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {doc.metadata.tags.map((tag) => (
                          <span key={tag}
                            className="inline-flex items-center gap-1 px-2 py-0.5
                                       rounded-md bg-slate-100 text-slate-500
                                       text-2xs font-mono">
                            <Tag className="w-2.5 h-2.5" /> {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
          )}
        </div>

        {/* Detail panel */}
        <div>
          <AnimatePresence mode="wait">
            {selected ? (
              <motion.div
                key={selected._id}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 12 }}
className="card p-5 lg:sticky lg:top-4"
              >
                <div className="flex items-center justify-between mb-4">
                  <p className="label">Document Details</p>
                  <button onClick={() => setSelected(null)}
                    className="text-slate-400 hover:text-slate-600 transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <p className="font-semibold text-navy-800 text-sm mb-1">{selected.label}</p>
                <p className="font-mono text-2xs text-slate-400 mb-4">
                  {formatBytes(selected.size_bytes)} ·{" "}
                  {selected.created_at
                    ? new Date(selected.created_at).toLocaleDateString("en-IN")
                    : "—"}
                </p>

                <div className="space-y-4">
                  {/* Summary */}
                  {selected.metadata?.summary && (
                    <div>
                      <p className="label mb-1">AI Summary</p>
                      <p className="text-xs text-slate-600 leading-relaxed">
                        {selected.metadata.summary}
                      </p>
                    </div>
                  )}
                  

                  {/* Parties */}
                  {selected.metadata?.parties?.length > 0 && (
                    <div>
                      <p className="label mb-2 flex items-center gap-1">
                        <Users className="w-3 h-3" /> Parties
                      </p>
                      <div className="space-y-1">
                        {selected.metadata.parties.map((p) => (
                          <p key={p} className="text-xs text-slate-600 bg-slate-50
                                                px-2 py-1 rounded-lg">
                            {p}
                          </p>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Key dates */}
                  {selected.metadata?.key_dates?.length > 0 && (
                    <div>
                      <p className="label mb-2 flex items-center gap-1">
                        <Calendar className="w-3 h-3" /> Key Dates
                      </p>
                      <div className="space-y-1">
                        {selected.metadata.key_dates.map((d) => (
                          <p key={d} className="text-xs text-slate-600">{d}</p>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Case number */}
                  {selected.metadata?.case_number && (
                    <div>
                      <p className="label mb-1">Case Number</p>
                      <p className="font-mono text-xs text-coral-600">
                        {selected.metadata.case_number}
                      </p>
                    </div>
                  )}

                  {/* Court */}
                  {selected.metadata?.court && (
                    <div>
                      <p className="label mb-1">Court</p>
                      <p className="text-xs text-slate-600">{selected.metadata.court}</p>
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="card p-8 text-center"
              >
                <FolderOpen className="w-8 h-8 text-slate-200 mx-auto mb-3" />
                <p className="text-slate-400 text-sm">
                  Click a document to see AI-extracted details
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}