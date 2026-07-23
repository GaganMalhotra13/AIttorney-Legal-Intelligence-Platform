"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { authAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import {
  Scale, User, Mail, Lock, Phone, MapPin,
  Loader2, Eye, EyeOff, ArrowRight
} from "lucide-react";

const JURISDICTIONS = [
  "India (General)", "Delhi NCR", "Maharashtra",
  "Karnataka", "Tamil Nadu", "West Bengal",
  "Gujarat", "Rajasthan", "Other State / UT",
];

export default function SignupPage() {
  const router = useRouter();
  const setUser = useStore((s) => s.setUser);

  const [name,        setName]        = useState("");
  const [email,        setEmail]        = useState("");
  const [password,     setPassword]     = useState("");
  const [confirmPass,  setConfirmPass]  = useState("");
  const [phone,        setPhone]        = useState("");
  const [location,     setLocation]     = useState("India (General)");
  const [showPass,     setShowPass]     = useState(false);
  const [loading,      setLoading]      = useState(false);
  const [agreed,       setAgreed]       = useState(false);

  const validate = () => {
    if (!name.trim())              { toast.error("Enter your full name"); return false; }
    if (!email.includes("@"))      { toast.error("Enter a valid email"); return false; }
    if (password.length < 6)       { toast.error("Password must be at least 6 characters"); return false; }
    if (password !== confirmPass)  { toast.error("Passwords don't match"); return false; }
    if (!agreed)                   { toast.error("Accept the terms to continue"); return false; }
    return true;
  };

  const handleSignup = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
const { data } = await authAPI.register(name.trim(), email.trim().toLowerCase(), password);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setUser({ email: data.user.email, name: data.user.name, token: data.access_token });

      // Save optional profile fields if provided
      if (phone || location !== "India (General)") {
        try {
          // authAPI may not implement updateProfile in all builds — guard the call
          if (typeof (authAPI as any).updateProfile === "function") {
            await (authAPI as any).updateProfile({ phone, location });
          }
        } catch {
          // non-critical — profile can be completed later
        }
      }

      toast.success("Account created!");
      router.push("/dashboard/home");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Signup failed — try a different email";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
<div className="min-h-screen flex items-center justify-center bg-ivory px-4 py-6 sm:py-10">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{
              background: "linear-gradient(135deg, #C4472A 0%, #6366F1 100%)",
              boxShadow: "0 2px 8px rgba(79,70,229,0.30)",
            }}
          >
            <Scale className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-display font-bold text-ink-900 text-xl leading-none">
              AI<span className="text-coral-600">ttorney</span>
            </p>
            <p className="font-mono text-[9px] text-ink-300 tracking-widest uppercase mt-0.5">
              Legal Intelligence
            </p>
          </div>
        </div>

        {/* Card */}
<div className="card p-5 sm:p-7 space-y-5">
          <div>
            <h1 className="font-display text-2xl font-bold text-ink-900 mb-1">
              Create your account
            </h1>
            <p className="text-ink-400 text-sm">
              Free access to all 11 AI legal modules
            </p>
          </div>

          {/* Name */}
          <div>
            <label className="label">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300" />
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Gagan Malhotra"
                className="input pl-10"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="label">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300" />
              <input
                type="email"
                value={email}
onChange={(e) => setEmail(e.target.value.toLowerCase())}                placeholder="you@example.com"
                className="input pl-10"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="label">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300" />
              <input
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 characters"
                className="input pl-10 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-300 hover:text-ink-600"
              >
                {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Confirm Password */}
          <div>
            <label className="label">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300" />
              <input
                type={showPass ? "text" : "password"}
                value={confirmPass}
                onChange={(e) => setConfirmPass(e.target.value)}
                placeholder="Re-enter password"
                className="input pl-10"
              />
            </div>
          </div>

          {/* Phone — optional */}
          <div>
            <label className="label">Phone <span className="text-ink-300 font-normal">(optional)</span></label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300" />
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 98765 43210"
                className="input pl-10"
              />
            </div>
          </div>

          {/* Location — optional */}
          <div>
            <label className="label">Location <span className="text-ink-300 font-normal">(optional)</span></label>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-300 pointer-events-none" />
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="input pl-10"
              >
                {JURISDICTIONS.map((j) => <option key={j}>{j}</option>)}
              </select>
            </div>
          </div>

          {/* Terms */}
          <label className="flex items-start gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-0.5"
            />
            <span className="text-xs text-ink-400 leading-relaxed">
              I understand AIttorney provides educational legal information only,
              not legal advice, and is not a substitute for a licensed advocate.
            </span>
          </label>

          {/* Submit */}
          <motion.button
            onClick={handleSignup}
            disabled={loading}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="btn-primary w-full disabled:opacity-60"
          >
            {loading
              ? <span className="flex items-center justify-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Creating account…
                </span>
              : <span className="flex items-center justify-center gap-2">
                  Create Account <ArrowRight className="w-4 h-4" />
                </span>
            }
          </motion.button>

          {/* Login link */}
          <p className="text-center text-sm text-ink-400">
            Already have an account?{" "}
            <a href="/" className="text-coral-600 font-medium hover:underline">
              Sign in
            </a>
          </p>
        </div>
      </motion.div>
    </div>
  );
}