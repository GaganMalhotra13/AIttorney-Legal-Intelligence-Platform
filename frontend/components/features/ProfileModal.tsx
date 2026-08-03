"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { authAPI } from "@/lib/api";
import { useStore } from "@/store/useStore";
import { createPortal } from "react-dom";
import toast from "react-hot-toast";
import {
  X, User, Mail, Phone, Shield,
  Lock, Eye, EyeOff, Loader2, Crown
} from "lucide-react";

interface ProfileModalProps {
  open:    boolean;
  onClose: () => void;
}

export default function ProfileModal({ open, onClose }: ProfileModalProps) {
  const { user, setUser } = useStore();

  // Phone edit
  const [phone,        setPhone]        = useState("");
  const [savingPhone,  setSavingPhone]  = useState(false);

  // Password edit
  const [currentPw,    setCurrentPw]    = useState("");
  const [newPw,        setNewPw]        = useState("");
  const [confirmPw,    setConfirmPw]    = useState("");
  const [showCurrent,  setShowCurrent]  = useState(false);
  const [showNew,      setShowNew]      = useState(false);
  const [showConfirm,  setShowConfirm]  = useState(false);
  const [savingPw,     setSavingPw]     = useState(false);

  const ic  = "input text-sm";
  const lc  = "label mb-1";

  const savePhone = async () => {
    if (!phone.trim()) { toast.error("Enter a phone number"); return; }
    if (!/^[6-9]\d{9}$/.test(phone.replace(/\s/g, ""))) {
      toast.error("Enter a valid 10-digit Indian mobile number");
      return;
    }
    setSavingPhone(true);
    try {
      await authAPI.updateProfile({ phone: phone.trim() });
      toast.success("Phone number updated");
      setPhone("");
    } catch {
      toast.error("Failed to update phone");
    } finally {
      setSavingPhone(false);
    }
  };

  const savePassword = async () => {
    if (!currentPw)           { toast.error("Enter current password");           return; }
    if (newPw.length < 6)     { toast.error("New password must be 6+ characters"); return; }
    if (newPw !== confirmPw)  { toast.error("Passwords don't match");             return; }
    if (newPw === currentPw)  { toast.error("New password must be different");    return; }

    setSavingPw(true);
    try {
      await authAPI.changePassword(currentPw, newPw);
      toast.success("Password changed successfully");
      setCurrentPw(""); setNewPw(""); setConfirmPw("");
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Failed to change password");
    } finally {
      setSavingPw(false);
    }
  };

  const initials = user?.name
    ?.split(" ")
    .map((n: string) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2) || "U";

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
           <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/40 z-[9998]"
        />

        {/* Modal */}
        {/* Modal */}
<div className="fixed inset-0 z-[9999] flex items-center justify-center pointer-events-none">

<motion.div
  initial={{ opacity: 0, scale: 0.95, y: 20 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  exit={{ opacity: 0, scale: 0.95, y: 20 }}
  transition={{ duration: 0.2, ease: [0.16, 1, 1, 1] }}
  className="
    pointer-events-auto
    w-[calc(100%-2rem)]
    max-w-md
    max-h-[90vh]
    bg-surface
    rounded-2xl
    shadow-2xl
    border
    border-slate-100
    overflow-hidden
  "
>

            {/* Header */}
            <div className="bg-navy-900 px-6 py-5 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-coral-600 flex items-center
                                justify-center shadow-coral flex-shrink-0">
                  <span className="font-bold text-white text-lg">{initials}</span>
                </div>
                <div>
                  <p className="font-semibold text-white text-base">{user?.name}</p>
                  <p className="text-white/50 text-xs font-mono">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-white/40 hover:text-white
                           hover:bg-white/10 transition-all"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Body */}
            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">

              {/* Read-only info */}
              <div className="space-y-3">
                <p className="text-xs font-semibold text-slate-400 uppercase
                               tracking-widest">
                  Account Info
                </p>

                <div className="grid grid-cols-2 gap-3">
                  {/* Name — read only */}
                  <div>
                    <label className={lc}>
                      <User className="w-3 h-3 inline mr-1" /> Name
                    </label>
                    <div className="input text-sm bg-slate-50 text-slate-400
                                    cursor-not-allowed select-none">
                      {user?.name || "—"}
                    </div>
                  </div>

                  {/* Plan — read only */}
                  <div>
                    <label className={lc}>
                      <Crown className="w-3 h-3 inline mr-1" /> Plan
                    </label>
                    <div className="input text-sm bg-slate-50 text-slate-400
                                    cursor-not-allowed select-none flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-teal-500 inline-block" />
                      Free
                    </div>
                  </div>
                </div>

                {/* Email — read only */}
                <div>
                  <label className={lc}>
                    <Mail className="w-3 h-3 inline mr-1" /> Email
                  </label>
                  <div className="input text-sm bg-slate-50 text-slate-400
                                  cursor-not-allowed select-none font-mono ">
                    {user?.email || "—"}
                  </div>
                </div>

                <p className="text-2xs text-slate-300 font-mono">
                  Name and email cannot be changed. Contact support if needed.
                </p>
              </div>

              <hr className="border-slate-100" />

              {/* Phone — editable */}
              <div className="space-y-3">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  <Phone className="w-3 h-3 inline mr-1" /> Phone Number
                </p>
                <div>
                  <label className={lc}>New Phone Number</label>
                  <input
                    value={phone}
                    onChange={(e) => setPhone(e.target.value.replace(/\D/g, "").slice(0, 10))}
                    placeholder="10-digit mobile number"
                    className={ic}
                    type="tel"
                    maxLength={10}
                  />
                </div>
                <button
                  onClick={savePhone}
                  disabled={savingPhone || !phone.trim()}
                  className="btn-primary w-full py-2.5 text-sm disabled:opacity-50"
                >
                  {savingPhone
                    ? <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-3.5 h-3.5 animate-spin" /> Saving…
                      </span>
                    : "Update Phone Number"
                  }
                </button>
              </div>

              <hr className="border-slate-100" />

              {/* Password — editable */}
              <div className="space-y-3">
                <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
                  <Lock className="w-3 h-3 inline mr-1" /> Change Password
                </p>

                {/* Current password */}
                <div>
                  <label className={lc}>Current Password</label>
                  <div className="relative">
                    <input
                      type={showCurrent ? "text" : "password"}
                      value={currentPw}
                      onChange={(e) => setCurrentPw(e.target.value)}
                      placeholder="Your current password"
                      className={`${ic} pr-10`}
                    />
                    <button
                      onClick={() => setShowCurrent(!showCurrent)}
                      className="absolute right-3 top-1/2 -translate-y-1/2
                                 text-slate-400 hover:text-slate-600"
                    >
                      {showCurrent
                        ? <EyeOff className="w-4 h-4" />
                        : <Eye    className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* New password */}
                <div>
                  <label className={lc}>New Password</label>
                  <div className="relative">
                    <input
                      type={showNew ? "text" : "password"}
                      value={newPw}
                      onChange={(e) => setNewPw(e.target.value)}
                      placeholder="Minimum 6 characters"
                      className={`${ic} pr-10`}
                    />
                    <button
                      onClick={() => setShowNew(!showNew)}
                      className="absolute right-3 top-1/2 -translate-y-1/2
                                 text-slate-400 hover:text-slate-600"
                    >
                      {showNew
                        ? <EyeOff className="w-4 h-4" />
                        : <Eye    className="w-4 h-4" />}
                    </button>
                  </div>
                  {/* Strength indicator */}
                  {newPw && (
                    <div className="flex gap-1 mt-1.5">
                      {[1, 2, 3].map((i) => (
                        <div key={i} className={`h-1 flex-1 rounded-full transition-colors ${
                          newPw.length >= i * 4
                            ? i === 1 ? "bg-coral-400"
                            : i === 2 ? "bg-amber-400"
                            : "bg-teal-400"
                            : "bg-slate-100"
                        }`} />
                      ))}
                    </div>
                  )}
                </div>

                {/* Confirm password */}
                <div>
                  <label className={lc}>Confirm New Password</label>
                  <div className="relative">
                    <input
                      type={showConfirm ? "text" : "password"}
                      value={confirmPw}
                      onChange={(e) => setConfirmPw(e.target.value)}
                      placeholder="Re-enter new password"
                      className={`${ic} pr-10 ${
                        confirmPw && confirmPw !== newPw
                          ? "border-coral-300 bg-coral-50"
                          : ""
                      }`}
                    />
                    <button
                      onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-3 top-1/2 -translate-y-1/2
                                 text-slate-400 hover:text-slate-600"
                    >
                      {showConfirm
                        ? <EyeOff className="w-4 h-4" />
                        : <Eye    className="w-4 h-4" />}
                    </button>
                  </div>
                  {confirmPw && confirmPw !== newPw && (
                    <p className="text-xs text-coral-500 mt-1">Passwords don't match</p>
                  )}
                </div>

                <button
                  onClick={savePassword}
                  disabled={savingPw || !currentPw || !newPw || !confirmPw}
                  className="btn-primary w-full py-2.5 text-sm disabled:opacity-50"
                >
                  {savingPw
                    ? <span className="flex items-center justify-center gap-2">
                        <Loader2 className="w-3.5 h-3.5 animate-spin" /> Changing…
                      </span>
                    : "Change Password"
                  }
                </button>
              </div>

              {/* Security note */}
              <div className="flex items-start gap-2 p-3 rounded-xl
                              bg-slate-50 border border-slate-100">
                <Shield className="w-3.5 h-3.5 text-slate-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-slate-400 leading-relaxed">
                  Password is stored as a bcrypt hash. We never store your plain text password.
                  Changing your password will not log you out of this session.
                </p>
              </div>
            </div>
          </motion.div> </div>
        </>
      )}
    </AnimatePresence>
  );
}