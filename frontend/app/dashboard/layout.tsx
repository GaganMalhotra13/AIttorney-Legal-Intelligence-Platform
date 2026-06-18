"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/store/useStore";
import {
  Scale, Landmark, FileText, PenLine, Map,
  History, LogOut, ChevronRight, LayoutDashboard,
  BarChart2, FolderOpen, Calendar, Shield
} from "lucide-react";

const NAV = [
  { href: "/dashboard/home",           icon: LayoutDashboard, label: "Home",           group: "main"  },
  { href: "/dashboard/case-mirror",    icon: Landmark,        label: "Case Mirror",    group: "main"  },
  { href: "/dashboard/contract-audit", icon: FileText,        label: "Contract Audit", group: "main"  },
  { href: "/dashboard/notice-drafter", icon: PenLine,         label: "Notice Drafter", group: "main"  },
  { href: "/dashboard/roadmap",        icon: Map,             label: "Legal Roadmap",  group: "main"  },
  { href: "/dashboard/document-vault", icon: FolderOpen,      label: "Document Vault", group: "tools" },
  { href: "/dashboard/case-tracker",   icon: Calendar,        label: "Case Tracker",   group: "tools" },
  { href: "/dashboard/analytics",      icon: BarChart2,       label: "Analytics",      group: "tools" },
  { href: "/dashboard/history",        icon: History,         label: "History",        group: "tools" },
];

const STATUS = [
  { label: "Gemini API",       live: true },
  { label: "18-Source Search", live: true },
  { label: "11 AI Modules",    live: true },
  { label: "FastAPI Backend",  live: true },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useStore();
  const router   = useRouter();
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && !localStorage.getItem("token")) {
      router.push("/");
    }
    if (pathname === "/dashboard") router.replace("/dashboard/home");
  }, [pathname]);

  if (!user) return null;

  const initials = user.name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2);
  const mainNav  = NAV.filter((n) => n.group === "main");
  const toolsNav = NAV.filter((n) => n.group === "tools");

  const NavItem = ({ href, icon: Icon, label }: typeof NAV[0]) => {
    const active = pathname === href || (href !== "/dashboard/home" && pathname.startsWith(href));
    return (
      <Link href={href}>
        <motion.div
          whileHover={{ x: collapsed ? 0 : 2 }}
          title={collapsed ? label : undefined}
          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                      transition-all cursor-pointer group
                      ${active
                        ? "bg-coral-50 text-coral-700 border border-coral-100"
                        : "text-slate-500 hover:text-navy-800 hover:bg-bg2"}`}
        >
          <Icon className={`w-4 h-4 flex-shrink-0 ${active ? "text-coral-600" : "text-slate-400 group-hover:text-navy-600"}`} />
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex-1 truncate">
                {label}
              </motion.span>
            )}
          </AnimatePresence>
          {active && !collapsed && <ChevronRight className="w-3 h-3 text-coral-400 flex-shrink-0" />}
        </motion.div>
      </Link>
    );
  };

  return (
    <div className="flex h-screen overflow-hidden bg-bg">
      {/* Sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 64 : 240 }}
        transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
        className="flex-shrink-0 bg-surface border-r border-slate-100 shadow-sm flex flex-col overflow-hidden relative z-10"
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-100 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-coral-600 flex items-center justify-center flex-shrink-0 shadow-coral">
            <Scale className="w-4 h-4 text-white" />
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} transition={{ duration: 0.15 }}>
                <p className="font-display font-bold text-navy-900 text-lg leading-none">AI<span className="text-coral-600">ttorney</span></p>
                <p className="font-mono text-[9px] text-slate-400 tracking-widest uppercase mt-0.5">v7 · Legal AI</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2 overflow-y-auto space-y-0.5">
          <AnimatePresence>
            {!collapsed && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="px-3 pt-3 pb-1 font-mono text-[9px] text-slate-400 uppercase tracking-widest">
                Core
              </motion.p>
            )}
          </AnimatePresence>
          {mainNav.map((item) => <NavItem key={item.href} {...item} />)}

          <AnimatePresence>
            {!collapsed && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="px-3 pt-4 pb-1 font-mono text-[9px] text-slate-400 uppercase tracking-widest">
                Tools
              </motion.p>
            )}
          </AnimatePresence>
          {toolsNav.map((item) => <NavItem key={item.href} {...item} />)}
        </nav>

        {/* Status */}
        <AnimatePresence>
          {!collapsed && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="px-4 py-3 border-t border-slate-100">
              <p className="label mb-2">System Status</p>
              <div className="space-y-1.5">
                {STATUS.map(({ label, live }) => (
                  <div key={label} className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${live ? "bg-teal-400 animate-pulse" : "bg-slate-300"}`} />
                    <span className="font-mono text-[10px] text-slate-400">{label}</span>
                  </div>
                ))}
              </div>
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
              {!collapsed && (
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

        {/* Collapse toggle */}
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
      </motion.aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <div className="bg-coral-50 border-b border-coral-100 px-6 py-2 flex items-center gap-2">
          <Shield className="w-3.5 h-3.5 text-coral-500 flex-shrink-0" />
          <p className="text-xs text-coral-600 font-medium">
            <strong>Educational Use Only</strong> — AIttorney provides general legal information, not legal advice.
          </p>
        </div>
        <div className="p-8 max-w-[1200px] mx-auto page-enter">{children}</div>
      </main>
    </div>
  );
}