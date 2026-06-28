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

interface NoticeState {
  senderName:       string;
  senderAddress:    string;
  senderPhone:      string;
  senderEmail:      string;
  recipientName:    string;
  recipientAddress: string;
  recipientDesig:   string;
  noticeType:       string;
  issueDate:        string;
  claimAmount:      string;
  description:      string;
  reliefSought:     string;
  deadline:         string;
  tone:             string;
  noticeOutput:     string;
}

interface RoadmapState {
  query:        string;
  jurisdiction: string;
  steps:        any[];
}

interface ContractState {
  text:     string;
  filename: string;
  role:     string;
  score:    any | null;
  analysis: string;
  docId:    string;
  chat:     { role: "user" | "ai"; content: string }[];
}

interface AdvocateState {
  caseType: string;
  location: string;
  summary:  string;
  results:  any[];
}

interface AppStore {
  // Auth
  user:    User | null;
  setUser: (u: User | null) => void;
  logout:  () => void;

  // Case Mirror
  caseResult:     CaseResult | null;
  setCaseResult:  (r: CaseResult | null) => void;
  liveContext:    string;
  setLiveContext: (c: string) => void;
  caseQuery:      string;
  setCaseQuery:   (q: string) => void;
  caseType:       string;
  setCaseType:    (t: string) => void;
  claimAmt:       number;
  setClaimAmt:    (a: number) => void;
  location:       string;
  setLocation:    (l: string) => void;
  moduleResults:  Record<string, string | any[]>;
  setModule:      (key: string, value: string | any[]) => void;
  clearModules:   () => void;
  activeModule:   string;
  setActiveModule:(m: string) => void;

  // Notice Drafter
  notice:      NoticeState;
  setNotice:   (updates: Partial<NoticeState>) => void;
  clearNotice: () => void;

  // Legal Roadmap
  roadmap:      RoadmapState;
  setRoadmap:   (updates: Partial<RoadmapState>) => void;
  clearRoadmap: () => void;

  // Contract Audit
  contract:      ContractState;
  setContract:   (updates: Partial<ContractState>) => void;
  clearContract: () => void;

  // Advocate Finder
  advocate:      AdvocateState;
  setAdvocate:   (updates: Partial<AdvocateState>) => void;
  clearAdvocate: () => void;
}

const DEFAULT_NOTICE: NoticeState = {
  senderName: "", senderAddress: "", senderPhone: "", senderEmail: "",
  recipientName: "", recipientAddress: "", recipientDesig: "",
  noticeType: "Security Deposit Refund", issueDate: "", claimAmount: "",
  description: "", reliefSought: "", deadline: "15",
  tone: "Professional", noticeOutput: "",
};

const DEFAULT_ROADMAP: RoadmapState = {
  query: "", jurisdiction: "India (General)", steps: [],
};

const DEFAULT_CONTRACT: ContractState = {
  text: "", filename: "", role: "Employee",
  score: null, analysis: "", docId: "", chat: [],
};

const DEFAULT_ADVOCATE: AdvocateState = {
  caseType: "Consumer Dispute", location: "Delhi NCR",
  summary: "", results: [],
};

export const useStore = create<AppStore>()(
  persist(
    (set) => ({
      // ── Auth ────────────────────────────────────────────────
      user:    null,
      setUser: (user) => set({ user }),
     logout: () => {
  const refreshToken = typeof window !== "undefined"
    ? localStorage.getItem("refresh_token") : null;
  if (refreshToken) {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    }).catch(() => {});
  }
  if (typeof window !== "undefined") {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("aittorney-store"); // ← ADD THIS — wipes entire persisted store
  }
  set({
    user:          null,
    caseResult:    null,
    liveContext:   "",
    caseQuery:     "",
    moduleResults: {},
    activeModule:  "opponent",
    notice:        DEFAULT_NOTICE,
    roadmap:       DEFAULT_ROADMAP,
    contract:      DEFAULT_CONTRACT,
    advocate:      DEFAULT_ADVOCATE,
  });
  if (typeof window !== "undefined") window.location.href = "/";
},
      // ── Case Mirror ─────────────────────────────────────────
      caseResult:     null,
      setCaseResult:  (caseResult) => set({ caseResult }),
      liveContext:    "",
      setLiveContext: (liveContext) => set({ liveContext }),
      caseQuery:      "",
      setCaseQuery:   (caseQuery) => set({ caseQuery }),
      caseType:       "Consumer Dispute",
      setCaseType:    (caseType) => set({ caseType }),
      claimAmt:       0,
      setClaimAmt:    (claimAmt) => set({ claimAmt }),
      location:       "India (General)",
      setLocation:    (location) => set({ location }),
      moduleResults:  {},
      setModule:      (key, value) =>
        set((s) => ({ moduleResults: { ...s.moduleResults, [key]: value } })),
      clearModules:   () => set({ moduleResults: {} }),
      activeModule:   "opponent",
      setActiveModule:(activeModule) => set({ activeModule }),

      // ── Notice Drafter ──────────────────────────────────────
      notice:      DEFAULT_NOTICE,
      setNotice:   (updates) => set((s) => ({ notice: { ...s.notice, ...updates } })),
      clearNotice: () => set({ notice: DEFAULT_NOTICE }),

      // ── Legal Roadmap ───────────────────────────────────────
      roadmap:      DEFAULT_ROADMAP,
      setRoadmap:   (updates) => set((s) => ({ roadmap: { ...s.roadmap, ...updates } })),
      clearRoadmap: () => set({ roadmap: DEFAULT_ROADMAP }),

      // ── Contract Audit ──────────────────────────────────────
      contract:      DEFAULT_CONTRACT,
      setContract:   (updates) => set((s) => ({ contract: { ...s.contract, ...updates } })),
      clearContract: () => set({ contract: DEFAULT_CONTRACT }),

      // ── Advocate Finder ─────────────────────────────────────
      advocate:      DEFAULT_ADVOCATE,
      setAdvocate:   (updates) => set((s) => ({ advocate: { ...s.advocate, ...updates } })),
      clearAdvocate: () => set({ advocate: DEFAULT_ADVOCATE }),
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
        notice:        s.notice,
        roadmap:       s.roadmap,
        contract:      s.contract,
        advocate:      s.advocate,
      }),
    }
  )
);