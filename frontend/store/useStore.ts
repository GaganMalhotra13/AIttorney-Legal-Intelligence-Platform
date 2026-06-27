import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  email: string;
  name:  string;
  token: string;
}

interface CaseResult {
  query:      string;
  analysis:   string;
  win_prob:   number;
  grade:      string;
  laws:       string;
  sources:    any[];
  score_data: any;
}

interface AppStore {
  // Auth
  user:          User | null;
  setUser:       (u: User | null) => void;
  logout:        () => void;

  // Case Mirror
  caseResult:    CaseResult | null;
  setCaseResult: (r: CaseResult | null) => void;
  liveContext:   string;
  setLiveContext:(c: string) => void;
  caseQuery:     string;
  setCaseQuery:  (q: string) => void;
  caseType:      string;
  setCaseType:   (t: string) => void;
  claimAmt:      number;
  setClaimAmt:   (a: number) => void;
  location:      string;
  setLocation:   (l: string) => void;

  // Module results — keyed by module name
  moduleResults: Record<string, string | any[]>;
  setModule:     (key: string, value: string | any[]) => void;
  clearModules:  () => void;

  // UI state
  activeModule:  string;
  setActiveModule:(m: string) => void;
}

export const useStore = create<AppStore>()(
  persist(
    (set) => ({
      user:       null,
      setUser:    (user) => set({ user }),
     logout: () => {
  // Revoke refresh token on backend
  const refreshToken = typeof window !== "undefined"
    ? localStorage.getItem("refresh_token") : null;

  if (refreshToken) {
    // Fire and forget — don't await
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).catch(() => {});
  }

  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
  }

  set({
    user:          null,
    caseResult:    null,
    liveContext:   "",
    caseQuery:     "",
    moduleResults: {},
    activeModule:  "opponent",
  });

  if (typeof window !== "undefined") {
    window.location.href = "/";
  }
},
      caseResult:    null,
      setCaseResult: (caseResult) => set({ caseResult }),
      liveContext:   "",
      setLiveContext:(liveContext) => set({ liveContext }),
      caseQuery:     "",
      setCaseQuery:  (caseQuery) => set({ caseQuery }),
      caseType:      "Consumer Dispute",
      setCaseType:   (caseType) => set({ caseType }),
      claimAmt:      0,
      setClaimAmt:   (claimAmt) => set({ claimAmt }),
      location:      "India (General)",
      setLocation:   (location) => set({ location }),

      moduleResults: {},
      setModule:     (key, value) =>
        set((s) => ({ moduleResults: { ...s.moduleResults, [key]: value } })),
      clearModules:  () => set({ moduleResults: {} }),

      activeModule:   "opponent",
      setActiveModule:(activeModule) => set({ activeModule }),
    }),
    {
      name: "aittorney-store",
      partialize: (s) => ({ 
        user:          s.user,
        caseResult:    s.caseResult,
        liveContext:   s.liveContext,
        moduleResults: s.moduleResults,
        caseQuery:     s.caseQuery,
        caseType:      s.caseType,
        claimAmt:      s.claimAmt,
        location:      s.location,
        activeModule:  s.activeModule,

       }),
    }
  )
);