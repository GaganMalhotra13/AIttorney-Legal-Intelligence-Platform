"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { authAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import { Scale, Zap, FileText, Landmark } from "lucide-react";

const DEMO_EMAIL    = "test123@testing.com";
const DEMO_PASSWORD = "test123";

const FEATURES = [
  { icon: Zap,      label: "18-Source RAG Pipeline",   desc: "Live search across IndianKanoon, LiveLaw & 16 more with Cohere reranking"  },
  { icon: Scale,    label: "28-Signal Scoring Engine",  desc: "Explainable win probability — not a hardcoded number"                      },
  { icon: FileText, label: "11 AI Legal Modules",       desc: "FIR drafts, settlement estimates, opponent analysis, case comparator"      },
  { icon: Landmark, label: "Landmark Judgments",        desc: "Direct IndianKanoon scraping with citation counts and full text"           },
];

export default function LoginPage() {
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [loading,  setLoading]  = useState(false);
  const setUser = useStore((s) => s.setUser);
  const router  = useRouter();

  // Autofill demo password ONLY when demo email is typed —
  // does not block or restrict any other email
  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setEmail(val);
    if (val === DEMO_EMAIL) {
      setPassword(DEMO_PASSWORD);
    }
  };

  const handleLogin = async () => {
    if (!email.trim())    { toast.error("Enter your email"); return; }
    if (!password.trim()) { toast.error("Enter your password"); return; }

    setLoading(true);
    try {
      const { data } = await authAPI.login(email, password);
      localStorage.setItem("token",         data.access_token  || "");
      localStorage.setItem("refresh_token", data.refresh_token || "");
      setUser({
        email: data.user?.email || email,
        name:  data.user?.name  || "",
        token: data.access_token,
      });
      toast.success(`Welcome, ${(data.user?.name || "").split(" ")[0]}!`);
      router.push("/dashboard/home");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.replace("/dashboard/home");
    }
  }, []);

  return (
    <div className="min-h-screen bg-bg flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-[52%] bg-navy-900 relative overflow-hidden flex-col justify-between p-12">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "radial-gradient(circle, #ffffff 1px, transparent 1px)", backgroundSize: "28px 28px" }} />
        <div className="absolute top-0 left-0 w-96 h-96 bg-coral-500 rounded-full filter blur-3xl opacity-10 -translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-teal-500 rounded-full filter blur-3xl opacity-8 translate-x-1/3 translate-y-1/3" />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, ease: [0.16,1,0.3,1] }} className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-coral-600 flex items-center justify-center shadow-coral"><Scale className="w-5 h-5 text-white" /></div>
            <span className="font-display text-2xl font-bold text-white tracking-tight">AI<span className="text-coral-400">ttorney</span></span>
          </div>
          <p className="font-mono text-2xs tracking-widest uppercase text-white/30 ml-[52px]">Legal Intelligence Platform · v7</p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.1, ease: [0.16,1,0.3,1] }} className="relative z-10">
          <h1 className="font-display text-5xl font-bold text-white leading-[1.1] tracking-tight mb-6">
            Plain language in.<br /><span className="text-coral-400">Full legal intelligence</span><br />out.
          </h1>
          <p className="text-white/50 text-base leading-relaxed max-w-sm">
            Describe your situation in plain language. Get win probability, landmark judgments, and 11 AI modules from 18 live Indian legal databases.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }} className="relative z-10 grid grid-cols-2 gap-3">
          {FEATURES.map(({ icon: Icon, label, desc }, i) => (
            <motion.div key={label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 + i * 0.05 }}
              className="p-4 rounded-xl bg-white/[0.04] border border-white/[0.07]">
              <div className="w-7 h-7 rounded-lg bg-coral-500/20 flex items-center justify-center mb-3"><Icon className="w-3.5 h-3.5 text-coral-400" /></div>
              <p className="font-semibold text-white text-xs mb-1">{label}</p>
              <p className="text-white/40 text-xs leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Right — form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.6, ease: [0.16,1,0.3,1] }} className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-10">
            <div className="w-9 h-9 rounded-xl bg-coral-600 flex items-center justify-center"><Scale className="w-4 h-4 text-white" /></div>
            <span className="font-display text-xl font-bold text-navy-900">AI<span className="text-coral-600">ttorney</span></span>
          </div>

          <div className="mb-8">
            <h2 className="font-display text-3xl font-bold text-navy-900 tracking-tight mb-2">Welcome back</h2>
            <p className="text-slate-500 text-sm">Sign in to your workspace to continue your legal research.</p>
          </div>

          {/* Demo credentials — informational only, not a restriction */}
          <div className="mb-6 p-4 rounded-xl bg-coral-50 border border-coral-100">
            <p className="text-xs text-coral-700 font-semibold mb-1">Try the demo</p>
            <p className="font-mono text-xs text-coral-600">{DEMO_EMAIL}</p>
            <p className="text-xs text-coral-400 mt-1">Password auto-fills when you type this email ↑ — or sign in with your own account.</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="label">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={handleEmailChange}
                placeholder="you@example.com"
                className="input"
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="input"
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
              />
            </div>
            <motion.button onClick={handleLogin} disabled={loading} whileHover={{ scale: 1.01, y: -1 }} whileTap={{ scale: 0.99 }}
              className="btn-primary w-full py-3 text-base disabled:opacity-60 disabled:cursor-not-allowed">
              {loading
                ? <span className="flex items-center justify-center gap-2"><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Signing in…</span>
                : "Enter Workspace →"}
            </motion.button>
          </div>

          <p className="text-center text-sm text-slate-400 mt-4">
            Don't have an account?{" "}
            <a href="/signup" className="text-coral-600 font-medium hover:underline">
              Create one
            </a>
          </p>

          <p className="text-center text-slate-400 text-xs mt-6 font-mono">Educational use only · Not legal advice</p>
        </motion.div>
      </div>
    </div>
  );
}