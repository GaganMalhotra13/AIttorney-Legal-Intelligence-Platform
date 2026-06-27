"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/store/useStore";
import {
  Scale, Landmark, FileText, PenLine, Map,
  History, LogOut, ChevronRight, ChevronDown, LayoutDashboard,
  BarChart2, FolderOpen, Calendar, AlertTriangle, Users, Shield, Menu, X
} from "lucide-react";

const NAV_CORE = [
  { href: "/dashboard/home",            icon: LayoutDashboard, label: "Home"            },
  { href: "/dashboard/case-mirror",     icon: Landmark,        label: "Case Mirror"     },
  { href: "/dashboard/contract-audit",  icon: FileText,        label: "Contract Audit"  },
  { href: "/dashboard/notice-drafter",  icon: PenLine,         label: "Notice Drafter"  },
  { href: "/dashboard/roadmap",         icon: Map,             label: "Legal Roadmap"   },
  { href: "/dashboard/advocate-finder", icon: Users,           label: "Find Advocate"   },
];

const NAV_TOOLS = [
  { href: "/dashboard/document-vault", icon: FolderOpen,  label: "Document Vault" },
  { href: "/dashboard/case-tracker",   icon: Calendar,    label: "Case Tracker"   },
  { href: "/dashboard/analytics",      icon: BarChart2,   label: "Analytics"      },
  { href: "/dashboard/history",        icon: History,     label: "History"        },
];

const STATUS = [
  { label: "Gemini API",        live: true },
  { label: "18-Source Search",  live: true },
  { label: "11 AI Modules",     live: true },
  { label: "FastAPI Backend",   live: true },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useStore();
  const router   = useRouter();
  const pathname = usePathname();

  const [collapsed,    setCollapsed]    = useState(false);
  const [authChecked,  setAuthChecked]  = useState(false);
  const [statusOpen,   setStatusOpen]   = useState(false);
  const [isMobile,     setIsMobile]     = useState(false);
  const [mobileOpen,   setMobileOpen]   = useState(false);

  // ── Mobile detection ─────────────────────────────────────
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  // Close mobile nav on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // ── Auth check ────────────────────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      router.replace("/");
      return;
    }

    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const expired = payload.exp * 1000 < Date.now();
      if (expired) {
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token");
        router.replace("/");
        return;
      }
    } catch {
      localStorage.removeItem("token");
      router.replace("/");
      return;
    }

    if (pathname === "/dashboard") {
      router.replace("/dashboard/home");
    }

    setAuthChecked(true);
  }, [pathname]);

  if (!authChecked || !user) return (
    <div className="flex h-screen items-center justify-center bg-ivory">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-violet-600 flex items-center justify-center">
          <Scale className="w-4 h-4 text-white" />
        </div>
        <p className="text-sm text-ink-400 font-mono">Verifying session…</p>
      </div>
    </div>
  );

  const initials = user.name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2);

  type NavItemProps = (typeof NAV_CORE)[number];
  const NavItem = ({ href, icon: Icon, label }: NavItemProps) => {
    const active = pathname === href || (href !== "/dashboard/home" && pathname.startsWith(href));
    const showLabel = isMobile || !collapsed;
    return (
      <Link href={href}>
        <motion.div
          whileHover={{ x: showLabel ? 2 : 0 }}
          title={!showLabel ? label : undefined}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                      transition-all cursor-pointer group
                      ${active
                        ? "bg-coral-50 text-coral-700 border border-coral-100"
                        : "text-slate-500 hover:text-navy-800 hover:bg-bg2"}`}
        >
          <Icon className={`w-4 h-4 flex-shrink-0 ${active ? "text-coral-600" : "text-slate-400 group-hover:text-navy-600"}`} />
          <AnimatePresence>
            {showLabel && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 truncate">
                {label}
              </motion.span>
            )}
          </AnimatePresence>
          {active && showLabel && <ChevronRight className="w-3 h-3 text-coral-400 flex-shrink-0" />}
        </motion.div>
      </Link>
    );
  };

  const sidebarShowLabels = isMobile || !collapsed;

  return (
    <div className="flex h-screen overflow-hidden bg-bg relative">

      {/* ── Mobile hamburger button ─────────────────────────── */}
      {isMobile && !mobileOpen && (
        <button
          onClick={() => setMobileOpen(true)}
          className="fixed top-3 left-3 z-50 p-2.5 rounded-xl bg-surface border border-slate-200
                     shadow-md text-slate-600 active:scale-95 transition-all"
        >
          <Menu className="w-5 h-5" />
        </button>
      )}

      {/* ── Mobile backdrop ──────────────────────────────────── */}
      <AnimatePresence>
        {isMobile && mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setMobileOpen(false)}
            className="fixed inset-0 bg-black/40 z-40"
          />
        )}
      </AnimatePresence>

      {/* ── Sidebar ──────────────────────────────────────────── */}
      <motion.aside
        animate={
          isMobile
            ? { x: mobileOpen ? 0 : -280 }
            : { width: collapsed ? 64 : 240 }
        }
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className={`bg-surface border-r border-slate-100 shadow-sm flex flex-col overflow-hidden z-50
                    ${isMobile
                      ? "fixed inset-y-0 left-0 w-[280px]"
                      : "flex-shrink-0 relative"}`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-coral-600 flex items-center justify-center flex-shrink-0 shadow-coral">
              <Scale className="w-4 h-4 text-white" />
            </div>
            <AnimatePresence>
              {sidebarShowLabels && (
                <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} transition={{ duration: 0.15 }} className="min-w-0">
                  <p className="font-display font-bold text-navy-900 text-lg leading-none truncate">AI<span className="text-coral-600">ttorney</span></p>
                  <p className="font-mono text-[9px] text-slate-400 tracking-widest uppercase mt-0.5">Legal Intelligence Platform</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          {isMobile && (
            <button
              onClick={() => setMobileOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-navy-700 hover:bg-bg2 flex-shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 overflow-y-auto space-y-0.5">
          <AnimatePresence>
            {sidebarShowLabels && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="px-3 pt-3 pb-1 font-mono text-[9px] text-slate-400 uppercase tracking-widest">
                Core
              </motion.p>
            )}
          </AnimatePresence>
          {NAV_CORE.map((item) => <NavItem key={item.href} {...item} />)}

          <AnimatePresence>
            {sidebarShowLabels && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="px-3 pt-4 pb-1 font-mono text-[9px] text-slate-400 uppercase tracking-widest">
                Tools
              </motion.p>
            )}
          </AnimatePresence>
          {NAV_TOOLS.map((item) => <NavItem key={item.href} {...item} />)}
        </nav>

        {/* Status — collapsible */}
        <AnimatePresence>
          {sidebarShowLabels && (
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="border-t border-ink-100/50"
            >
              <button
                onClick={() => setStatusOpen(!statusOpen)}
                className="w-full px-4 py-3 flex items-center justify-between
                           hover:bg-ink-50/50 transition-colors"
              >
                <p className="label mb-0">System</p>
                <motion.div animate={{ rotate: statusOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
                  <ChevronDown className="w-3.5 h-3.5 text-ink-300" />
                </motion.div>
              </button>

              <AnimatePresence>
                {statusOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-3 space-y-1.5">
                      {STATUS.map(({ label, live }) => (
                        <div key={label} className="flex items-center gap-2">
                          <div
                            className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                              live ? "bg-sage-500" : "bg-ink-300"
                            }`}
                            style={live ? { animation: "pulseLive 2.4s ease-in-out infinite" } : {}}
                          />
                          <span className="font-mono text-[10px] text-ink-300">{label}</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>

        {/* User */}
        <div className="p-3 border-t border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-coral-100 border border-coral-200 flex items-center justify-center flex-shrink-0">
              <span className="font-bold text-coral-700 text-xs">{initials}</span>
            </div>
            <AnimatePresence>
              {sidebarShowLabels && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 min-w-0">
                  <p className="font-semibold text-navy-800 text-xs truncate">{user.name}</p>
                  <p className="text-slate-400 text-xs font-mono truncate">{user.email}</p>
                </motion.div>
              )}
            </AnimatePresence>
            <button onClick={logout} title="Sign out"
              className="p-1.5 rounded-lg text-slate-400 hover:text-coral-600 hover:bg-coral-50 transition-all flex-shrink-0">
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Collapse toggle — desktop only */}
        {!isMobile && (
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="absolute top-1/2 -right-3 w-6 h-6 bg-surface border border-slate-200
                       rounded-full flex items-center justify-center shadow-sm text-slate-400
                       hover:text-navy-600 hover:border-slate-300 transition-all z-20"
          >
            <motion.div animate={{ rotate: collapsed ? 0 : 180 }}>
              <ChevronRight className="w-3 h-3" />
            </motion.div>
          </button>
        )}
      </motion.aside>

      {/* ── Main ─────────────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto">
        <div className={`bg-coral-50 border-b border-coral-100 px-4 sm:px-6 py-2 flex items-center gap-2 ${isMobile ? "pl-14" : ""}`}>
          <Shield className="w-3.5 h-3.5 text-coral-500 flex-shrink-0" />
          <p className="text-xs text-coral-600 font-medium leading-snug">
            <strong>Educational Use Only</strong>
            <span className="hidden sm:inline"> — AIttorney provides general legal information, not legal advice.</span>
          </p>
        </div>
        <div className="p-4 sm:p-6 md:p-8 max-w-[1200px] mx-auto page-enter">{children}</div>
      </main>
    </div>
  );
}