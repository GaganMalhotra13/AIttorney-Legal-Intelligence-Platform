import axios from "axios";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: BASE });

// Auto-attach token
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    config.withCredentials = true;
  }
  return config;
});

// Auto-logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/";
    }
    return Promise.reject(err);
  }
);

// ── Auth ──────────────────────────────────────────────────────
export const authAPI = {
  login:    (email: string, password: string) =>
    api.post("/api/auth/login", { email, password }),
  register: (name: string, email: string, password: string) =>
    api.post("/api/auth/register", { name, email, password }),
};

// ── Cases ─────────────────────────────────────────────────────
export interface CaseRequest {
  query: string;
  case_type: string;
  location?: string;
  claim_amt?: number;
  language?: string;
  incident_date?: string;
}

export interface Source {
  id?: string;
  title?: string;
  url?: string;
  excerpt?: string;
}

export interface Landmark {
  title: string;
  description: string;
  date?: string;
}

export interface ScoreData {
  [key: string]: unknown;
}

// ── Brain Modules ─────────────────────────────────────────────
export const brainAPI = {
  opponent:     (query: string, live_context: string) =>
    api.post("/api/brain/opponent", { query, live_context }),
  evidence:     (query: string, case_type: string) =>
    api.post("/api/brain/evidence", { query, case_type }),
  settlement:   (query: string, claim_amount: number, case_type: string, live_context: string) =>
    api.post("/api/brain/settlement", { query, claim_amount, case_type, live_context }),
  jurisdiction: (query: string, location: string) =>
    api.post("/api/brain/jurisdiction", { query, location }),
  timeline:     (query: string, score_data: object, case_type: string) =>
    api.post("/api/brain/timeline", { query, score_data, case_type }),
  brief:        (data: object) =>
    api.post("/api/brain/brief", data),
  fir:          (data: object) =>
    api.post("/api/brain/fir", data),
  mediation:    (data: object) =>
    api.post("/api/brain/mediation", data),
  limitation:   (data: object) =>
    api.post("/api/brain/limitation", data),
  compare:      (query: string, live_context: string, case_type: string) =>
    api.post("/api/brain/compare", { query, live_context, case_type }),
  whatsapp:     (chat_export: string, case_type: string) =>
    api.post("/api/brain/analyze-whatsapp", { chat_export, case_type }),
};

// ── Contracts ─────────────────────────────────────────────────
export const contractsAPI = {
  audit:    (text: string, role: string) =>
    api.post("/api/contracts/audit", { text, role }),
  chat:     (question: string, context: string, doc_id?: string) =>
    api.post("/api/contracts/chat", { question, context, doc_id }),
  simplify: (text: string, role: string) =>
    api.post("/api/contracts/simplify", { text, role }),
};

// ── Notices ───────────────────────────────────────────────────
export const noticesAPI = {
  draft: (context: string, sender: string, recipient: string, tone: string) =>
    api.post("/api/notices/draft", { context, sender, recipient, tone }),
};

// ── History ───────────────────────────────────────────────────
export const historyAPI = {
  cases: () => api.get("/api/cases/history"),
  stats: () => api.get("/api/cases/stats"), 
};

// ── Analytics ─────────────────────────────────────────────────
export const analyticsAPI = {
  overview: () => api.get("/api/analytics/overview"),
};

// ── Documents ─────────────────────────────────────────────────
export const documentsAPI = {
  upload: (formData: FormData) =>
    api.post("/api/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  list:   () => api.get("/api/documents/"),
  search: (query: string) =>
    api.post("/api/documents/search", null, { params: { query } }),
  delete: (id: string) => api.delete(`/api/documents/${id}`),
};

// ── Case Tracker ──────────────────────────────────────────────
export const trackerAPI = {
  list:         ()               => api.get("/api/tracker/"),
  add:          (data: object)   => api.post("/api/tracker/", data),
  updateStatus: (id: string, status: string) =>
    api.patch(`/api/tracker/${id}/status?status=${status}`),
  delete:       (id: string)     => api.delete(`/api/tracker/${id}`),
};
export interface CaseResponse {
  id?:        string;
  query:      string;
  analysis:   string;
  win_prob:   number;
  grade:      string;
  laws:       string;
  sources:    Source[];
  landmarks:  Landmark[];
  score_data: ScoreData;
}
export const casesAPI = {
  analyze: (data: CaseRequest) =>
    api.post<CaseResponse>("/api/cases/analyze", data),
  history: () =>
    api.get("/api/cases/history"),
  stats:   () =>
    api.get("/api/cases/stats"),
  getById: (id: string) =>
    api.get<CaseResponse>(`/api/cases/${id}`),
  delete:  (id: string) =>
    api.delete(`/api/cases/${id}`),
};