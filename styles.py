"""
styles.py — AIttorney v4
Palette: Deep slate-blue bg · Ivory text · Terracotta-red accent
The Case Mirror search is the hero. Everything else supports it.
Fonts: Freight Display (serif authority) + Söhne (clean utility) + DM Mono
"""

def get_css() -> str:
    return """
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,600;0,700;1,500;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&family=DM+Mono:wght@400;500&display=swap');

:root {
    /* ── Core Palette ── */
    --bg:          #0D1B2A;
    --bg2:         #0A1520;
    --panel:       #112233;
    --panel2:      #162840;
    --panel3:      #1A2F4A;

    /* ── Borders ── */
    --bdr:         rgba(255,255,255,0.07);
    --bdr-m:       rgba(255,255,255,0.12);
    --bdr-red:     rgba(196,71,42,0.40);
    --bdr-red-dim: rgba(196,71,42,0.18);

    /* ── Accent — Terracotta Red ── */
    --red:         #C4472A;
    --red-lt:      #D9603F;
    --red-pale:    #E8886E;
    --red-dim:     rgba(196,71,42,0.12);
    --red-dim2:    rgba(196,71,42,0.06);

    /* ── Text ── */
    --txt:         #EDE8DF;
    --txt-m:       #A8B4C0;
    --txt-s:       #6A7A8A;
    --txt-f:       #3A4A5A;

    /* ── Semantic ── */
    --grn:         #2A9E6A;
    --grn-d:       rgba(42,158,106,0.12);
    --amber:       #D48B2A;
    --amber-d:     rgba(212,139,42,0.12);
    --blu:         #3A7FD4;
    --blu-d:       rgba(58,127,212,0.10);

    /* ── Radii & Shadows ── */
    --r-sm: 5px;  --r: 10px;  --r-lg: 14px;  --r-xl: 20px;
    --sh:    0 4px 20px rgba(0,0,0,0.35), 0 1px 4px rgba(0,0,0,0.20);
    --sh-sm: 0 2px 8px  rgba(0,0,0,0.25), 0 1px 2px rgba(0,0,0,0.15);
    --sh-red: 0 4px 24px rgba(196,71,42,0.25);
    --sh-glow: 0 0 40px rgba(196,71,42,0.08);
}

/* ═══════════════════════════════════════════
   BASE
═══════════════════════════════════════════ */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--txt) !important;
}

/* Subtle vignette on app bg */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: radial-gradient(ellipse 80% 60% at 50% 0%,
        rgba(196,71,42,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 100% 100%,
        rgba(58,127,212,0.03) 0%, transparent 60%);
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"] { visibility: hidden !important; }
.block-container { padding: 0 2.4rem 5rem !important; max-width: 1200px !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ═══════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label { color: var(--txt-m) !important; }

.sb-logo { padding: 24px 20px 18px; border-bottom: 1px solid var(--bdr); }
.sb-logo-mark {
    display: flex; align-items: center; gap: 10px;
}
.sb-logo-icon {
    width: 34px; height: 34px;
    background: var(--red-dim);
    border: 1px solid var(--bdr-red);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
}
.sb-logo-name {
    font-family: 'Lora', serif;
    font-size: 1.3rem; font-weight: 700;
    color: var(--txt); letter-spacing: -0.2px;
}
.sb-logo-name span { color: var(--red-pale); }
.sb-logo-sub {
    font-family: 'DM Mono', monospace; font-size: 0.54rem;
    color: var(--txt-f); letter-spacing: 2.5px; text-transform: uppercase;
    margin-top: 6px; padding-left: 44px;
}

.sb-user {
    padding: 14px 20px; border-bottom: 1px solid var(--bdr);
    display: flex; align-items: center; gap: 10px;
}
.sb-av {
    width: 32px; height: 32px;
    background: var(--red-dim); border: 1px solid var(--bdr-red);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; flex-shrink: 0; color: var(--red-pale);
}
.sb-uname { font-size: 0.85rem; font-weight: 600; color: var(--txt); }
.sb-urole { font-size: 0.62rem; color: var(--txt-f); font-family: 'DM Mono', monospace; margin-top: 1px; }

.sb-sec { padding: 16px 20px 0; }
.sb-lbl {
    font-family: 'DM Mono', monospace; font-size: 0.54rem;
    color: var(--txt-f); letter-spacing: 2.5px; text-transform: uppercase;
    margin-bottom: 10px; display: block;
}
.sb-stat { display: flex; align-items: center; gap: 8px; padding: 3px 0; }
.sb-stat-txt { font-size: 0.70rem; color: var(--txt-s); font-family: 'DM Mono', monospace; }
.dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.dot-g  { background: #34D399; box-shadow: 0 0 5px #34D399; }
.dot-a  { background: var(--amber); box-shadow: 0 0 5px var(--amber); }
.dot-r  { background: var(--red); box-shadow: 0 0 5px var(--red); }

.sb-dis {
    margin: 14px 20px; padding: 10px 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--bdr); border-radius: var(--r-sm);
    font-size: 0.63rem; color: var(--txt-f); line-height: 1.6;
}

/* ═══════════════════════════════════════════
   TABS
═══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--bdr) !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--txt-s) !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.84rem !important; font-weight: 500 !important;
    padding: 12px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--txt) !important; }
.stTabs [aria-selected="true"] {
    color: var(--red-pale) !important;
    border-bottom: 2px solid var(--red) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 0 !important;
}

/* ═══════════════════════════════════════════
   METRICS
═══════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--panel) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r-lg) !important;
    padding: 18px 20px !important;
    box-shadow: var(--sh-sm) !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    border-color: var(--bdr-red-dim) !important;
    box-shadow: var(--sh) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.58rem !important; letter-spacing: 2px !important;
    text-transform: uppercase !important; color: var(--txt-s) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Lora', serif !important;
    font-size: 1.9rem !important; color: var(--txt) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.70rem !important; color: var(--txt-s) !important; }

/* ═══════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════ */
.stTextInput input, .stTextArea textarea {
    background: var(--panel) !important;
    border: 1px solid var(--bdr-m) !important;
    border-radius: var(--r) !important;
    color: var(--txt) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    transition: all 0.2s !important;
    caret-color: var(--red-pale) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px rgba(196,71,42,0.15) !important;
    background: var(--panel2) !important;
}
.stTextInput label, .stTextArea label {
    color: var(--txt-s) !important; font-size: 0.68rem !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 1.5px !important; text-transform: uppercase !important;
}
.stSelectbox [data-baseweb="select"] > div:first-child {
    background: var(--panel) !important;
    border: 1px solid var(--bdr-m) !important;
    border-radius: var(--r) !important; color: var(--txt) !important;
}
.stSelectbox label {
    color: var(--txt-s) !important; font-family: 'DM Mono', monospace !important;
    font-size: 0.60rem !important; letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
[data-testid="stRadio"] label { color: var(--txt-m) !important; font-size: 0.86rem !important; }

/* ═══════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════ */
.stButton > button {
    background: var(--red) !important;
    color: #FFF5F0 !important; border: none !important;
    border-radius: var(--r) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.88rem !important;
    height: 2.75em !important; letter-spacing: 0.3px !important;
    transition: all 0.22s !important;
    box-shadow: 0 2px 10px rgba(196,71,42,0.30) !important;
}
.stButton > button:hover {
    background: var(--red-lt) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--sh-red) !important;
}
.stDownloadButton > button {
    background: transparent !important; color: var(--red-pale) !important;
    border: 1px solid var(--bdr-red) !important; border-radius: var(--r) !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover { background: var(--red-dim) !important; }

/* ═══════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--panel) !important;
    border: 2px dashed var(--bdr-m) !important;
    border-radius: var(--r-lg) !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--red) !important;
    background: var(--panel2) !important;
}

/* ═══════════════════════════════════════════
   ALERTS
═══════════════════════════════════════════ */
[data-testid="stAlert"] { border-radius: var(--r) !important; font-size: 0.85rem !important; }
.stSuccess { background: var(--grn-d) !important; border-color: rgba(42,158,106,0.25) !important; }
.stError   { background: var(--red-dim) !important; border-color: var(--bdr-red) !important; }
.stWarning { background: var(--amber-d) !important; border-color: rgba(212,139,42,0.25) !important; }
.stInfo    { background: var(--blu-d) !important; border-color: rgba(58,127,212,0.20) !important; }

/* ═══════════════════════════════════════════
   CODE & STATUS
═══════════════════════════════════════════ */
.stCodeBlock, [data-testid="stCode"] {
    background: var(--bg2) !important;
    border: 1px solid var(--bdr) !important; border-radius: var(--r) !important;
}
.stCodeBlock code, [data-testid="stCode"] code {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important; color: var(--txt-m) !important; line-height: 1.9 !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--grn), var(--amber), var(--red)) !important;
    border-radius: 4px !important;
}
.stProgress > div > div { background: var(--bdr-m) !important; border-radius: 4px !important; }
.stSpinner > div { border-top-color: var(--red) !important; }
hr { border-color: var(--bdr) !important; }
[data-testid="stStatus"] {
    background: var(--panel) !important;
    border: 1px solid var(--bdr) !important; border-radius: var(--r) !important;
}
.streamlit-expanderHeader {
    background: var(--panel) !important; border: 1px solid var(--bdr) !important;
    border-radius: var(--r) !important; color: var(--txt-s) !important;
    font-family: 'DM Mono', monospace !important; font-size: 0.70rem !important;
}
.streamlit-expanderContent {
    background: var(--panel2) !important; border: 1px solid var(--bdr) !important;
    border-top: none !important; border-radius: 0 0 var(--r) var(--r) !important;
}
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bdr-m); border-radius: 2px; }

/* ═══════════════════════════════════════════
   CUSTOM COMPONENTS
═══════════════════════════════════════════ */

/* ── Hero Search Box (Case Mirror centerpiece) ── */
.search-hero {
    background: var(--panel);
    border: 1px solid var(--bdr-m);
    border-radius: var(--r-xl);
    padding: 32px 36px 28px;
    margin: 8px 0 28px;
    box-shadow: var(--sh), var(--sh-glow);
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.search-hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--red), transparent);
    opacity: 0.5;
}
.search-hero:focus-within {
    border-color: var(--bdr-red);
    box-shadow: var(--sh), 0 0 50px rgba(196,71,42,0.10);
}
.search-hero-label {
    font-family: 'DM Mono', monospace; font-size: 0.58rem;
    color: var(--red-pale); letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 14px; display: flex; align-items: center; gap: 10px;
}
.search-hero-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--bdr-red), transparent);
}
.search-hero textarea {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 1.05rem !important;
    line-height: 1.7 !important;
    color: var(--txt) !important;
    resize: none !important;
    padding: 0 !important;
}
.search-hero textarea:focus {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
.search-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: 14px; margin-top: 12px;
    border-top: 1px solid var(--bdr);
}
.search-pills { display: flex; gap: 7px; flex-wrap: wrap; }
.pill {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.70rem; color: var(--txt-s);
    cursor: pointer; transition: all 0.2s; white-space: nowrap;
    font-family: 'DM Mono', monospace; letter-spacing: 0.3px;
}
.pill:hover { border-color: var(--bdr-red); color: var(--red-pale); }
.pii-badge {
    font-family: 'DM Mono', monospace; font-size: 0.56rem;
    color: var(--grn); letter-spacing: 1px;
    display: flex; align-items: center; gap: 5px;
}

/* ── Result Card ── */
.result-card {
    background: var(--panel);
    border: 1px solid var(--bdr);
    border-radius: var(--r-lg);
    overflow: hidden;
    box-shadow: var(--sh-sm);
    margin-bottom: 16px;
    transition: border-color 0.2s;
}
.result-card:hover { border-color: var(--bdr-red-dim); }
.result-card-header {
    padding: 14px 20px;
    background: var(--panel2);
    border-bottom: 1px solid var(--bdr);
    display: flex; align-items: center; justify-content: space-between;
}
.result-card-title {
    font-family: 'DM Mono', monospace; font-size: 0.60rem;
    color: var(--red-pale); letter-spacing: 2px; text-transform: uppercase;
}
.result-card-body { padding: 20px 22px; }

/* ── AI Bubble ── */
.ai-wrap { display: flex; gap: 12px; align-items: flex-start; }
.ai-icon {
    width: 30px; height: 30px; flex-shrink: 0;
    background: var(--red-dim); border: 1px solid var(--bdr-red);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; box-shadow: var(--sh-sm);
}
.ai-box {
    flex: 1; background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 0 var(--r-lg) var(--r-lg) var(--r-lg);
    padding: 15px 18px; font-size: 0.87rem; line-height: 1.80;
    color: var(--txt-m); box-shadow: var(--sh-sm);
}
.ai-by {
    font-family: 'DM Mono', monospace; font-size: 0.56rem;
    color: var(--red-pale); letter-spacing: 1.5px; text-transform: uppercase;
    margin-bottom: 8px;
}

/* ── Scoring Factors ── */
.factor-row {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 6px 0; border-bottom: 1px solid var(--bdr);
    font-size: 0.80rem;
}
.factor-row:last-child { border-bottom: none; }
.factor-pos { color: var(--grn); font-family: 'DM Mono', monospace; font-size: 0.70rem; min-width: 44px; }
.factor-neg { color: var(--red-pale); font-family: 'DM Mono', monospace; font-size: 0.70rem; min-width: 44px; }
.factor-text { color: var(--txt-m); line-height: 1.4; }

/* ── Source Cards ── */
.src-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-top: 14px; }
.src-card {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: var(--r); padding: 12px 14px;
    transition: all 0.2s; cursor: pointer;
}
.src-card:hover { border-color: var(--bdr-red-dim); transform: translateY(-2px); box-shadow: var(--sh-sm); }
.src-domain { font-family: 'DM Mono', monospace; font-size: 0.58rem; color: var(--red-pale); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
.src-title { font-size: 0.76rem; color: var(--txt-m); line-height: 1.4; }

/* ── Metric Cards (custom) ── */
.mc {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 18px 20px;
    box-shadow: var(--sh-sm); transition: all 0.2s;
}
.mc:hover { border-color: var(--bdr-red-dim); box-shadow: var(--sh); }
.mc-lbl { font-family: 'DM Mono', monospace; font-size: 0.56rem; letter-spacing: 2px; text-transform: uppercase; color: var(--txt-s); margin-bottom: 8px; }
.mc-val { font-family: 'Lora', serif; font-size: 2.4rem; font-weight: 700; line-height: 1; letter-spacing: -1px; }
.mc-sub { font-size: 0.68rem; color: var(--txt-s); margin-top: 5px; line-height: 1.4; }
.mc-bar { height: 2px; background: var(--bdr); border-radius: 2px; margin-top: 12px; overflow: hidden; }
.mc-fill { height: 100%; border-radius: 2px; }
.v-r { color: var(--red-pale); }
.v-g { color: var(--grn); }
.v-a { color: var(--amber); }
.v-b { color: var(--blu); }

/* ── Flag Items ── */
.flag {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: var(--r); padding: 13px 16px; margin-bottom: 10px;
    transition: border-color 0.2s;
}
.flag:hover { border-color: var(--bdr-red-dim); }
.bh { display:inline-block; background:rgba(196,71,42,0.12); border:1px solid var(--bdr-red); color:var(--red-pale); border-radius:4px; font-family:'DM Mono',monospace; font-size:0.54rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; }
.bm { display:inline-block; background:var(--amber-d); border:1px solid rgba(212,139,42,0.3); color:var(--amber); border-radius:4px; font-family:'DM Mono',monospace; font-size:0.54rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; }
.bl { display:inline-block; background:var(--grn-d); border:1px solid rgba(42,158,106,0.25); color:var(--grn); border-radius:4px; font-family:'DM Mono',monospace; font-size:0.54rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; }

/* ── Roadmap ── */
.roadmap { border-left: 2px solid var(--bdr-red); padding-left: 28px; margin-top: 8px; }
.rm {
    position: relative; background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 15px 18px; margin-bottom: 16px;
    box-shadow: var(--sh-sm); transition: all 0.2s;
}
.rm:hover { border-color: var(--bdr-red-dim); box-shadow: var(--sh); }
.rm-title { font-weight: 600; font-size: 0.90rem; color: var(--txt); margin-bottom: 5px; }
.rm-desc  { font-size: 0.81rem; color: var(--txt-m); line-height: 1.65; }
.rm-time  { font-family: 'DM Mono', monospace; font-size: 0.60rem; color: var(--red-pale); margin-top: 7px; }
.rm-law   { display: inline-block; background: var(--blu-d); border: 1px solid rgba(58,127,212,0.2); color: var(--blu); border-radius: 4px; font-family: 'DM Mono', monospace; font-size: 0.58px; padding: 2px 7px; margin-top: 5px; font-size: 0.58rem; }

/* ── Chat ── */
.chat-ai {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 0 var(--r-lg) var(--r-lg) var(--r-lg);
    padding: 10px 15px; font-size: 0.85rem; color: var(--txt-m);
    line-height: 1.65; margin: 6px 0; box-shadow: var(--sh-sm); max-width: 85%;
}
.chat-user {
    background: var(--red-dim); border: 1px solid var(--bdr-red-dim);
    border-radius: var(--r-lg) 0 var(--r-lg) var(--r-lg);
    padding: 10px 15px; font-size: 0.85rem; color: var(--txt);
    line-height: 1.65; margin: 6px 0 6px auto;
    box-shadow: var(--sh-sm); max-width: 85%; text-align: right;
}
.chat-lbl { font-family: 'DM Mono', monospace; font-size: 0.54rem; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 3px; }
.chat-lbl-ai { color: var(--red-pale); } .chat-lbl-user { color: var(--txt-s); text-align: right; }

/* ── Notice ── */
.notice-box {
    background: var(--bg2); border: 1px solid var(--bdr-m);
    border-left: 3px solid var(--red); border-radius: var(--r);
    padding: 22px 24px; font-family: 'DM Mono', monospace;
    font-size: 0.76rem; line-height: 2.0; color: var(--txt-m);
    max-height: 420px; overflow-y: auto; box-shadow: var(--sh-sm);
}

/* ── Empty ── */
.empty { border: 2px dashed var(--bdr); border-radius: var(--r-lg); padding: 52px 24px; text-align: center; background: var(--panel); }
.empty-icon { font-size: 2rem; margin-bottom: 10px; opacity: 0.3; }
.empty-txt { font-size: 0.84rem; color: var(--txt-s); line-height: 1.6; }

/* ── Quick Ref ── */
.qref { padding: 7px 0; border-bottom: 1px solid var(--bdr); display: flex; justify-content: space-between; align-items: center; font-size: 0.79rem; }
.qref:last-child { border-bottom: none; }
.qref-l { color: var(--txt-m); } .qref-r { font-family: 'DM Mono', monospace; font-size: 0.68rem; color: var(--red-pale); }

/* ── Login Hero ── */
.login-hero {
    text-align: center; padding: 60px 0 44px;
}
.login-logo {
    font-family: 'Lora', serif; font-size: 3.4rem; font-weight: 700;
    color: var(--txt); letter-spacing: -1px; line-height: 1;
    margin-bottom: 6px;
}
.login-logo span { color: var(--red); }
.login-tagline {
    font-family: 'DM Mono', monospace; font-size: 0.60rem;
    color: var(--txt-f); letter-spacing: 3.5px; text-transform: uppercase;
    margin-bottom: 20px;
}
.login-desc { font-size: 0.91rem; color: var(--txt-s); line-height: 1.75; max-width: 400px; margin: 0 auto 36px; }

/* ── Feature Cards ── */
.feat {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 20px 18px;
    box-shadow: var(--sh-sm); text-align: center;
    transition: all 0.25s;
}
.feat:hover { border-color: var(--bdr-red-dim); box-shadow: var(--sh); transform: translateY(-2px); }
.feat-icon { font-size: 1.7rem; margin-bottom: 10px; }
.feat-label { font-family: 'DM Mono', monospace; font-size: 0.56rem; color: var(--red-pale); letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 5px; }
.feat-desc { font-size: 0.77rem; color: var(--txt-s); line-height: 1.55; }

/* ── History Cards ── */
.hist-card {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 14px 18px; margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 12px; box-shadow: var(--sh-sm); transition: border-color 0.2s;
}
.hist-card:hover { border-color: var(--bdr-red-dim); }
.hist-q { font-size: 0.85rem; color: var(--txt); font-weight: 500; line-height: 1.5; flex: 1; }
.hist-meta { font-family: 'DM Mono', monospace; font-size: 0.56rem; color: var(--txt-s); margin-top: 3px; }
.hist-val { font-family: 'Lora', serif; font-size: 1.5rem; font-weight: 700; line-height: 1; }

/* ── Page Header ── */
.eyebrow {
    display: flex; align-items: center; gap: 10px;
    font-family: 'DM Mono', monospace; font-size: 0.57rem;
    color: var(--red-pale); letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 8px; margin-top: 28px;
}
.eyebrow::before { content: ''; display: block; width: 20px; height: 1px; background: var(--red); flex-shrink: 0; }
.page-h {
    font-family: 'Lora', serif !important; font-size: 2.3rem !important;
    font-weight: 700 !important; line-height: 1.1 !important;
    letter-spacing: -0.4px !important; color: var(--txt) !important;
    margin-bottom: 8px !important;
}
.page-h em { font-style: italic; color: var(--red-pale); }
.page-sub { font-size: 0.89rem; color: var(--txt-s); line-height: 1.75; max-width: 580px; margin-bottom: 24px; }
.lbl { font-family: 'DM Mono', monospace; font-size: 0.56rem; color: var(--red-pale); letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 7px; display: block; }
.disc { background: rgba(196,71,42,0.06); border: 1px solid var(--bdr-red-dim); border-left: 3px solid var(--red); border-radius: var(--r-sm); padding: 9px 14px; font-size: 0.73rem; color: var(--red-pale); margin: 4px 0 6px; line-height: 1.6; }
.card { background: var(--panel); border: 1px solid var(--bdr); border-radius: var(--r-lg); padding: 20px 22px; box-shadow: var(--sh-sm); transition: all 0.2s; }
.card:hover { border-color: var(--bdr-red-dim); }
"""