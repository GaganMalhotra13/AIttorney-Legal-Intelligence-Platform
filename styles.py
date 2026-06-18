"""
styles.py — AIttorney v9
Design: Dark Luxury — Apple/Stripe tier
Base: Deep slate-black
Primary accent: Terracotta red #C4472A
Complementary: Electric teal #00C2A8 (cool contrast to warm red)
Tertiary: Warm amber #F5A623 (analogous warmth)
Fonts: Instrument Serif (display) + Geist Sans (body) + Geist Mono (code)
"""

def get_css() -> str:
    return """
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@300;400;500&display=swap');

/* ═══════════════════════════════════════════
   DESIGN TOKENS — Stripe/Apple Tier
═══════════════════════════════════════════ */
:root {
    /* Backgrounds — true depth layering */
    --bg:        #0A0B0F;
    --bg2:       #07080B;
    --panel:     #111318;
    --panel2:    #161820;
    --panel3:    #1C1F28;
    --panel-hov: #1E2130;

    /* ── Primary: Terracotta Red ── */
    --red:       #C4472A;
    --red-lt:    #D4603F;
    --red-sat:   #E05535;   /* more saturated for glows */
    --red-pale:  #F09070;
    --red-dim:   rgba(196,71,42,0.14);
    --red-dim2:  rgba(196,71,42,0.07);
    --red-glow:  rgba(224,85,53,0.30);
    --red-glow2: rgba(224,85,53,0.12);

    /* ── Complementary: Electric Teal ── */
    --teal:      #00C2A8;
    --teal-lt:   #00D4B8;
    --teal-pale: #5EE8D8;
    --teal-dim:  rgba(0,194,168,0.12);
    --teal-glow: rgba(0,194,168,0.25);

    /* ── Tertiary: Warm Amber ── */
    --amb:       #F5A623;
    --amb-lt:    #F7BA50;
    --amb-dim:   rgba(245,166,35,0.12);
    --amb-glow:  rgba(245,166,35,0.20);

    /* ── Text ── */
    --txt:       #F0EDE8;
    --txt-m:     #9BA3B8;
    --txt-s:     #5C6478;
    --txt-f:     #2E3345;

    /* ── Borders ── */
    --bdr:       rgba(255,255,255,0.06);
    --bdr-m:     rgba(255,255,255,0.10);
    --bdr-red:   rgba(196,71,42,0.40);
    --bdr-red-d: rgba(196,71,42,0.15);
    --bdr-teal:  rgba(0,194,168,0.35);
    --bdr-teal-d:rgba(0,194,168,0.12);

    /* ── Semantic ── */
    --grn:       #00C2A8;   /* teal doubles as success */
    --grn-d:     rgba(0,194,168,0.10);
    --err:       #FF5B5B;
    --err-d:     rgba(255,91,91,0.10);
    --warn:      #F5A623;
    --warn-d:    rgba(245,166,35,0.10);
    --info:      #5B8DEF;
    --info-d:    rgba(91,141,239,0.10);

    /* ── Radii ── */
    --r-xs: 4px; --r-sm: 6px; --r: 10px;
    --r-lg: 14px; --r-xl: 20px; --r-2xl: 28px;

    /* ── Shadows — deep, layered ── */
    --sh:      0 8px 40px rgba(0,0,0,0.60), 0 2px 8px rgba(0,0,0,0.40);
    --sh-sm:   0 2px 12px rgba(0,0,0,0.45), 0 1px 3px rgba(0,0,0,0.30);
    --sh-red:  0 4px 28px rgba(224,85,53,0.35), 0 0 60px rgba(224,85,53,0.10);
    --sh-teal: 0 4px 24px rgba(0,194,168,0.25);
    --sh-glow: 0 0 80px rgba(196,71,42,0.06), 0 0 40px rgba(0,194,168,0.04);

    --ease: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-out: cubic-bezier(0, 0, 0.2, 1);
}

/* ═══════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; } to { opacity: 1; }
}
@keyframes shimmer-red {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
@keyframes glow-pulse {
    0%, 100% { box-shadow: 0 0 20px var(--red-glow2); }
    50%       { box-shadow: 0 0 40px var(--red-glow), 0 0 80px var(--red-glow2); }
}
@keyframes teal-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,194,168,0.5); }
    50%       { box-shadow: 0 0 0 5px rgba(0,194,168,0); }
}
@keyframes border-glow {
    0%, 100% { border-color: var(--bdr-red-d); }
    50%       { border-color: var(--bdr-red); }
}
@keyframes hero-gradient {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ═══════════════════════════════════════════
   BASE
═══════════════════════════════════════════ */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--txt) !important;
    -webkit-font-smoothing: antialiased !important;
    text-rendering: optimizeLegibility !important;
}

/* Premium noise grain */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    opacity: 0.028;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    background-size: 180px;
}

/* Ambient lighting — red top, teal bottom right */
.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 90% 45% at 50% -5%, rgba(196,71,42,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 55% 55% at 95% 100%, rgba(0,194,168,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 40% 40% at 5% 80%, rgba(245,166,35,0.03) 0%, transparent 55%);
}

.main .block-container {
    animation: fadeUp 0.5s var(--ease) both;
    position: relative; z-index: 1;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"] { visibility: hidden !important; }
.block-container {
    padding: 0 2.8rem 6rem !important;
    max-width: 1240px !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bdr-m); border-radius: 3px; }

/* ═══════════════════════════════════════════
   SIDEBAR — Apple-dark tier
═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--bdr) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label {
    color: var(--txt-m) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.sb-logo {
    padding: 28px 22px 22px;
    border-bottom: 1px solid var(--bdr);
    position: relative;
}
/* Animated red underline on logo */
.sb-logo::after {
    content: '';
    position: absolute; bottom: -1px; left: 22px;
    width: 40px; height: 1px;
    background: var(--red);
    box-shadow: 0 0 8px var(--red-sat);
}
.sb-logo-mark { display: flex; align-items: center; gap: 12px; }
.sb-logo-icon {
    width: 38px; height: 38px;
    background: var(--red-dim);
    border: 1px solid var(--bdr-red);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    box-shadow: 0 0 20px var(--red-glow2);
}
.sb-logo-name {
    font-family: 'Instrument Serif', serif;
    font-size: 1.45rem; font-weight: 400;
    color: var(--txt); letter-spacing: -0.2px;
}
.sb-logo-name span {
    color: var(--red-pale);
    text-shadow: 0 0 20px var(--red-glow);
}
.sb-logo-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.50rem; color: var(--txt-f);
    letter-spacing: 3.5px; text-transform: uppercase;
    margin-top: 8px; padding-left: 50px;
}

.sb-user {
    padding: 15px 22px;
    border-bottom: 1px solid var(--bdr);
    display: flex; align-items: center; gap: 11px;
}
.sb-av {
    width: 34px; height: 34px;
    background: var(--red-dim);
    border: 1px solid var(--bdr-red-d);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
    color: var(--red-pale);
}
.sb-uname { font-size: 0.86rem; font-weight: 600; color: var(--txt); }
.sb-urole {
    font-size: 0.60rem; color: var(--txt-f);
    font-family: 'DM Mono', monospace; margin-top: 2px;
    letter-spacing: 0.5px;
}

.sb-sec { padding: 18px 22px 0; }
.sb-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.50rem; color: var(--txt-f);
    letter-spacing: 3.5px; text-transform: uppercase;
    margin-bottom: 10px; display: block;
}
.sb-stat { display: flex; align-items: center; gap: 9px; padding: 4px 0; }
.sb-stat-txt {
    font-size: 0.69rem; color: var(--txt-s);
    font-family: 'DM Mono', monospace; letter-spacing: 0.3px;
}
.dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.dot-g {
    background: var(--teal);
    animation: teal-pulse 2.5s ease-in-out infinite;
}
.dot-a { background: var(--amb); }
.dot-r { background: var(--red); }

.sb-dis {
    margin: 16px 22px;
    padding: 10px 13px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--bdr);
    border-radius: var(--r-sm);
    font-size: 0.61rem; color: var(--txt-f); line-height: 1.65;
}

/* ═══════════════════════════════════════════
   TABS
═══════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--bdr) !important;
    gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--txt-s) !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.83rem !important; font-weight: 500 !important;
    padding: 13px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.2s, border-color 0.2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--txt) !important; }
.stTabs [aria-selected="true"] {
    color: var(--red-pale) !important;
    border-bottom: 2px solid var(--red) !important;
    font-weight: 600 !important;
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
    padding: 20px 22px !important;
    box-shadow: var(--sh-sm) !important;
    transition: all 0.3s var(--ease) !important;
}
[data-testid="metric-container"]:hover {
    border-color: var(--bdr-red-d) !important;
    box-shadow: var(--sh), 0 0 30px var(--red-glow2) !important;
    transform: translateY(-3px) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.56rem !important; letter-spacing: 2.5px !important;
    text-transform: uppercase !important; color: var(--txt-s) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Instrument Serif', serif !important;
    font-size: 2.2rem !important; color: var(--txt) !important;
    font-weight: 400 !important; letter-spacing: -1px !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.70rem !important; color: var(--txt-s) !important;
}

/* ═══════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════ */
.stTextInput input, .stTextArea textarea {
    background: var(--panel) !important;
    border: 1px solid var(--bdr-m) !important;
    border-radius: var(--r) !important;
    color: var(--txt) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.90rem !important;
    transition: all 0.2s var(--ease) !important;
    caret-color: var(--red-pale) !important;
    box-shadow: var(--sh-sm) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 3px var(--red-dim), var(--sh-sm) !important;
    background: var(--panel2) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: var(--txt-f) !important;
    font-style: italic;
}
.stTextInput label, .stTextArea label {
    color: var(--txt-s) !important;
    font-size: 0.62rem !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}
.stSelectbox [data-baseweb="select"] > div:first-child {
    background: var(--panel) !important;
    border: 1px solid var(--bdr-m) !important;
    border-radius: var(--r) !important;
    color: var(--txt) !important;
    font-family: 'DM Sans', sans-serif !important;
    box-shadow: var(--sh-sm) !important;
    transition: border-color 0.2s !important;
}
.stSelectbox [data-baseweb="select"] > div:first-child:hover {
    border-color: var(--bdr-red-d) !important;
}
.stSelectbox label {
    color: var(--txt-s) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.58rem !important;
    letter-spacing: 2px !important; text-transform: uppercase !important;
}
[data-testid="stRadio"] label {
    color: var(--txt-m) !important; font-size: 0.86rem !important;
}
[data-testid="stNumberInput"] input {
    background: var(--panel) !important;
    border: 1px solid var(--bdr-m) !important;
    border-radius: var(--r) !important;
    color: var(--txt) !important;
    box-shadow: var(--sh-sm) !important;
}

/* ═══════════════════════════════════════════
   BUTTONS — Stripe tier
═══════════════════════════════════════════ */
.stButton > button {
    background: var(--red) !important;
    color: #FFF5F2 !important;
    border: none !important;
    border-radius: var(--r) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; font-size: 0.87rem !important;
    height: 2.75em !important; letter-spacing: 0.2px !important;
    transition: all 0.22s var(--ease) !important;
    box-shadow: 0 2px 14px var(--red-glow2), 0 1px 3px rgba(0,0,0,0.3) !important;
    position: relative; overflow: hidden;
}
.stButton > button:hover {
    background: var(--red-sat) !important;
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: var(--sh-red) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.99) !important;
}
.stDownloadButton > button {
    background: transparent !important;
    color: var(--teal) !important;
    border: 1px solid var(--bdr-teal) !important;
    border-radius: var(--r) !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    box-shadow: 0 0 12px rgba(0,194,168,0.08) !important;
}
.stDownloadButton > button:hover {
    background: var(--teal-dim) !important;
    box-shadow: var(--sh-teal) !important;
    transform: translateY(-1px) !important;
}

/* ═══════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--panel) !important;
    border: 2px dashed var(--bdr-m) !important;
    border-radius: var(--r-xl) !important;
    transition: all 0.3s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--red) !important;
    background: var(--red-dim2) !important;
    box-shadow: 0 0 30px var(--red-glow2) !important;
}

/* ═══════════════════════════════════════════
   ALERTS & STATUS
═══════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: var(--r) !important;
    font-size: 0.84rem !important;
    border-left-width: 3px !important;
}
.stSuccess { background: var(--grn-d) !important; border-color: rgba(0,194,168,0.35) !important; }
.stError   { background: var(--err-d) !important; border-color: rgba(255,91,91,0.35) !important; }
.stWarning { background: var(--warn-d) !important; border-color: rgba(245,166,35,0.35) !important; }
.stInfo    { background: var(--info-d) !important; border-color: rgba(91,141,239,0.35) !important; }

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--red) 0%, var(--red-lt) 40%, var(--teal) 100%) !important;
    border-radius: 4px !important;
    background-size: 200% 100% !important;
    animation: shimmer-red 2s ease infinite !important;
}
.stProgress > div > div { background: var(--bdr-m) !important; border-radius: 4px !important; }
.stSpinner > div { border-top-color: var(--red) !important; }

.streamlit-expanderHeader {
    background: var(--panel) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r) !important;
    color: var(--txt-s) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    transition: all 0.2s !important;
}
.streamlit-expanderHeader:hover {
    background: var(--panel2) !important;
    border-color: var(--bdr-red-d) !important;
    color: var(--red-pale) !important;
}
.streamlit-expanderContent {
    background: var(--panel2) !important;
    border: 1px solid var(--bdr) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r) var(--r) !important;
}
[data-testid="stStatus"] {
    background: var(--panel) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r) !important;
}
.stCodeBlock, [data-testid="stCode"] {
    background: var(--bg2) !important;
    border: 1px solid var(--bdr) !important;
    border-radius: var(--r) !important;
}
.stCodeBlock code, [data-testid="stCode"] code {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.77rem !important;
    color: var(--teal-pale) !important;
    line-height: 1.9 !important;
}
hr { border-color: var(--bdr) !important; }

/* ═══════════════════════════════════════════
   PAGE HEADERS
═══════════════════════════════════════════ */
.eyebrow {
    display: flex; align-items: center; gap: 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.54rem; color: var(--red-pale);
    letter-spacing: 3.5px; text-transform: uppercase;
    margin-bottom: 10px; margin-top: 32px;
    animation: fadeIn 0.4s var(--ease) 0.1s both;
}
.eyebrow::before {
    content: ''; display: block; width: 22px; height: 1px;
    background: linear-gradient(90deg, var(--red), var(--teal));
    flex-shrink: 0; box-shadow: 0 0 8px var(--red-glow);
}

.page-h {
    font-family: 'Instrument Serif', serif !important;
    font-size: 2.8rem !important; font-weight: 400 !important;
    line-height: 1.1 !important; letter-spacing: -0.5px !important;
    color: var(--txt) !important; margin-bottom: 10px !important;
    animation: fadeUp 0.5s var(--ease) 0.15s both;
}
.page-h em {
    font-style: italic; color: var(--red-pale);
    text-shadow: 0 0 30px var(--red-glow);
}

.page-sub {
    font-size: 0.89rem; color: var(--txt-s);
    line-height: 1.8; max-width: 600px;
    margin-bottom: 28px;
    animation: fadeUp 0.5s var(--ease) 0.2s both;
}

.lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.54rem; color: var(--red-pale);
    letter-spacing: 2.5px; text-transform: uppercase;
    margin-bottom: 8px; display: block;
}

.disc {
    background: rgba(196,71,42,0.06);
    border: 1px solid var(--bdr-red-d);
    border-left: 3px solid var(--red);
    border-radius: var(--r-sm);
    padding: 10px 16px;
    font-size: 0.73rem; color: var(--red-pale);
    margin: 6px 0 8px; line-height: 1.65;
    box-shadow: 0 0 20px var(--red-dim2);
}

/* ═══════════════════════════════════════════
   SEARCH HERO — The statement piece
═══════════════════════════════════════════ */
.search-hero {
    background: var(--panel);
    border: 1px solid var(--bdr-m);
    border-radius: var(--r-2xl);
    padding: 38px 42px 30px;
    margin: 8px 0 26px;
    box-shadow: var(--sh), var(--sh-glow);
    position: relative; overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.4s var(--ease);
    animation: fadeUp 0.5s var(--ease) 0.25s both;
}
/* Animated gradient top border — red to teal */
.search-hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg,
        var(--red) 0%, var(--red-lt) 25%,
        var(--amb) 50%,
        var(--teal) 75%, var(--teal-lt) 100%);
    background-size: 300% 100%;
    animation: hero-gradient 4s ease infinite;
}
/* Radial glow corners */
.search-hero::after {
    content: '';
    position: absolute; inset: 0; pointer-events: none;
    background:
        radial-gradient(circle at 0% 0%, rgba(196,71,42,0.06) 0%, transparent 40%),
        radial-gradient(circle at 100% 100%, rgba(0,194,168,0.05) 0%, transparent 40%);
}
.search-hero:focus-within {
    border-color: var(--bdr-red);
    box-shadow: var(--sh), 0 0 0 3px var(--red-dim), 0 0 60px var(--red-glow2);
}
.search-hero-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.54rem; color: var(--red-pale);
    letter-spacing: 3px; text-transform: uppercase;
    margin-bottom: 18px;
    display: flex; align-items: center; gap: 12px;
}
.search-hero-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--bdr-red-d), transparent);
}
.search-hero textarea {
    background: transparent !important;
    border: none !important; box-shadow: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.08rem !important; line-height: 1.75 !important;
    color: var(--txt) !important; resize: none !important;
    padding: 0 !important;
}
.search-hero textarea:focus {
    border: none !important; box-shadow: none !important;
    background: transparent !important;
}
.search-footer {
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 10px;
    padding-top: 16px; margin-top: 14px;
    border-top: 1px solid var(--bdr);
}
.search-pills { display: flex; gap: 7px; flex-wrap: wrap; }
.pill {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 20px; padding: 4px 13px;
    font-size: 0.68rem; color: var(--txt-s);
    cursor: pointer; transition: all 0.2s; white-space: nowrap;
    font-family: 'DM Sans', sans-serif;
}
.pill:hover {
    border-color: var(--bdr-teal-d); color: var(--teal);
    background: var(--teal-dim);
}
.pii-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.54rem; color: var(--teal);
    letter-spacing: 1px;
    text-shadow: 0 0 12px var(--teal-glow);
}

/* ═══════════════════════════════════════════
   CARDS — layered depth
═══════════════════════════════════════════ */
.card {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 22px 24px;
    box-shadow: var(--sh-sm);
    transition: all 0.3s var(--ease);
}
.card:hover {
    border-color: var(--bdr-red-d);
    box-shadow: var(--sh), 0 0 30px var(--red-glow2);
    transform: translateY(-2px);
}

.result-card {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); overflow: hidden;
    box-shadow: var(--sh-sm); margin-bottom: 16px;
    transition: all 0.25s var(--ease);
}
.result-card:hover {
    border-color: var(--bdr-red-d);
    transform: translateY(-1px);
    box-shadow: var(--sh);
}
.result-card-header {
    padding: 14px 20px;
    background: var(--panel2);
    border-bottom: 1px solid var(--bdr);
    display: flex; align-items: center; justify-content: space-between;
}
.result-card-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem; color: var(--red-pale);
    letter-spacing: 2.5px; text-transform: uppercase;
}
.result-card-body { padding: 22px 24px; }

.mc {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 20px 22px;
    box-shadow: var(--sh-sm);
    transition: all 0.3s var(--ease);
    animation: fadeUp 0.5s var(--ease) 0.3s both;
}
.mc:hover {
    border-color: var(--bdr-red-d);
    box-shadow: var(--sh), 0 0 35px var(--red-glow2);
    transform: translateY(-3px);
}
.mc-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.54rem; letter-spacing: 2.5px;
    text-transform: uppercase; color: var(--txt-s); margin-bottom: 10px;
}
.mc-val {
    font-family: 'Instrument Serif', serif;
    font-size: 2.6rem; font-weight: 400;
    line-height: 1; letter-spacing: -1.5px;
}
.mc-sub { font-size: 0.70rem; color: var(--txt-s); margin-top: 6px; line-height: 1.4; }
.mc-bar { height: 2px; background: var(--bdr); border-radius: 2px; margin-top: 14px; overflow: hidden; }
.mc-fill { height: 100%; border-radius: 2px; transition: width 1.2s var(--ease); }
.v-g { color: var(--teal); text-shadow: 0 0 20px var(--teal-glow); }
.v-a { color: var(--amb); }
.v-r { color: var(--err); }
.v-b { color: #5B8DEF; }
.v-red { color: var(--red-pale); text-shadow: 0 0 20px var(--red-glow); }

.feat {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 24px 18px; text-align: center;
    box-shadow: var(--sh-sm); transition: all 0.3s var(--ease);
}
.feat:hover {
    border-color: var(--bdr-red-d);
    box-shadow: var(--sh), 0 0 30px var(--red-glow2);
    transform: translateY(-3px);
}
.feat-icon { font-size: 1.8rem; margin-bottom: 12px; }
.feat-label {
    font-family: 'DM Mono', monospace; font-size: 0.54rem;
    color: var(--red-pale); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 7px;
}
.feat-desc { font-size: 0.76rem; color: var(--txt-s); line-height: 1.6; }

.hist-card {
    background: var(--panel); border: 1px solid var(--bdr);
    border-radius: var(--r-lg); padding: 15px 20px; margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 12px; box-shadow: var(--sh-sm); transition: all 0.2s;
}
.hist-card:hover { border-color: var(--bdr-red-d); transform: translateY(-1px); }
.hist-q { font-size: 0.85rem; color: var(--txt); font-weight: 500; line-height: 1.5; flex: 1; }
.hist-meta { font-family: 'DM Mono', monospace; font-size: 0.54rem; color: var(--txt-s); margin-top: 3px; }
.hist-val { font-family: 'Instrument Serif', serif; font-size: 1.6rem; font-weight: 400; line-height: 1; }

/* ═══════════════════════════════════════════
   AI BUBBLE
═══════════════════════════════════════════ */
.ai-wrap { display: flex; gap: 13px; align-items: flex-start; }
.ai-icon {
    width: 33px; height: 33px; flex-shrink: 0;
    background: var(--red-dim); border: 1px solid var(--bdr-red-d);
    border-radius: var(--r-sm);
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; box-shadow: 0 0 16px var(--red-glow2);
}
.ai-box {
    flex: 1; background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 0 var(--r-lg) var(--r-lg) var(--r-lg);
    padding: 16px 20px; font-size: 0.87rem;
    line-height: 1.85; color: var(--txt-m); box-shadow: var(--sh-sm);
}
.ai-by {
    font-family: 'DM Mono', monospace; font-size: 0.54rem;
    color: var(--red-pale); letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 10px;
}

/* ═══════════════════════════════════════════
   CHAT
═══════════════════════════════════════════ */
.chat-ai {
    background: var(--panel2); border: 1px solid var(--bdr);
    border-radius: 0 var(--r-lg) var(--r-lg) var(--r-lg);
    padding: 11px 16px; font-size: 0.85rem; color: var(--txt-m);
    line-height: 1.7; margin: 8px 0; box-shadow: var(--sh-sm); max-width: 85%;
}
.chat-user {
    background: var(--red-dim); border: 1px solid var(--bdr-red-d);
    border-radius: var(--r-lg) 0 var(--r-lg) var(--r-lg);
    padding: 11px 16px; font-size: 0.85rem; color: var(--txt);
    line-height: 1.7; margin: 8px 0 8px auto;
    box-shadow: var(--sh-sm); max-width: 85%; text-align: right;
}
.chat-lbl { font-family: 'DM Mono', monospace; font-size: 0.52rem; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 3px; }
.chat-lbl-ai { color: var(--red-pale); } .chat-lbl-user { color: var(--txt-s); text-align: right; }

/* ═══════════════════════════════════════════
   BADGES — teal for contrast against red UI
═══════════════════════════════════════════ */
.bh { display:inline-block; background:rgba(255,91,91,0.10); border:1px solid rgba(255,91,91,0.30); color:#FF7070; border-radius:var(--r-xs); font-family:'DM Mono',monospace; font-size:0.52rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; }
.bm { display:inline-block; background:var(--amb-dim); border:1px solid rgba(245,166,35,0.30); color:var(--amb-lt); border-radius:var(--r-xs); font-family:'DM Mono',monospace; font-size:0.52rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; }
.bl { display:inline-block; background:var(--teal-dim); border:1px solid var(--bdr-teal-d); color:var(--teal); border-radius:var(--r-xs); font-family:'DM Mono',monospace; font-size:0.52rem; padding:2px 7px; letter-spacing:0.5px; text-transform:uppercase; margin-right:8px; vertical-align:middle; box-shadow:0 0 8px rgba(0,194,168,0.15); }

.flag { background:var(--panel2); border:1px solid var(--bdr); border-radius:var(--r); padding:14px 18px; margin-bottom:10px; transition:border-color 0.2s; }
.flag:hover { border-color:var(--bdr-red-d); }

/* ═══════════════════════════════════════════
   SOURCE GRID
═══════════════════════════════════════════ */
.src-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:14px; }
.src-card { background:var(--panel2); border:1px solid var(--bdr); border-radius:var(--r); padding:13px 15px; transition:all 0.2s; }
.src-card:hover { border-color:var(--bdr-teal-d); transform:translateY(-2px); box-shadow:var(--sh-sm),0 0 16px rgba(0,194,168,0.10); }
.src-domain { font-family:'DM Mono',monospace; font-size:0.56rem; color:var(--teal); letter-spacing:1.5px; text-transform:uppercase; margin-bottom:5px; text-shadow:0 0 12px rgba(0,194,168,0.30); }
.src-title { font-size:0.75rem; color:var(--txt-m); line-height:1.45; }

/* ═══════════════════════════════════════════
   ROADMAP
═══════════════════════════════════════════ */
.roadmap { border-left:1px solid var(--bdr-red-d); padding-left:28px; margin-top:8px; }
.rm { position:relative; background:var(--panel); border:1px solid var(--bdr); border-radius:var(--r-lg); padding:16px 20px; margin-bottom:16px; box-shadow:var(--sh-sm); transition:all 0.25s; }
.rm:hover { border-color:var(--bdr-red-d); box-shadow:var(--sh),0 0 25px var(--red-glow2); transform:translateY(-2px); }
.rm-title { font-weight:600; font-size:0.92rem; color:var(--txt); margin-bottom:6px; }
.rm-desc { font-size:0.82rem; color:var(--txt-m); line-height:1.7; }
.rm-time { font-family:'DM Mono',monospace; font-size:0.58rem; color:var(--red-pale); margin-top:8px; }
.rm-law { display:inline-block; background:var(--teal-dim); border:1px solid var(--bdr-teal-d); color:var(--teal); border-radius:var(--r-xs); font-family:'DM Mono',monospace; font-size:0.56rem; padding:2px 8px; margin-top:5px; }

/* ═══════════════════════════════════════════
   NOTICE BOX
═══════════════════════════════════════════ */
.notice-box {
    background: var(--bg2); border: 1px solid var(--bdr-m);
    border-left: 3px solid var(--red); border-radius: var(--r);
    padding: 24px 28px;
    font-family: 'DM Mono', monospace;
    font-size: 0.74rem; line-height: 2.1; color: var(--txt-m);
    max-height: 440px; overflow-y: auto;
    box-shadow: var(--sh-sm), 0 0 30px var(--red-glow2);
}

/* ═══════════════════════════════════════════
   SCORING FACTORS
═══════════════════════════════════════════ */
.factor-row { display:flex; align-items:flex-start; gap:12px; padding:7px 0; border-bottom:1px solid var(--bdr); font-size:0.81rem; }
.factor-row:last-child { border-bottom:none; }
.factor-pos { color:var(--teal); font-family:'DM Mono',monospace; font-size:0.68rem; min-width:48px; padding-top:1px; text-shadow:0 0 10px rgba(0,194,168,0.30); }
.factor-neg { color:#FF7070; font-family:'DM Mono',monospace; font-size:0.68rem; min-width:48px; padding-top:1px; }
.factor-text { color:var(--txt-m); line-height:1.45; }

/* ═══════════════════════════════════════════
   MISC
═══════════════════════════════════════════ */
.qref { padding:8px 0; border-bottom:1px solid var(--bdr); display:flex; justify-content:space-between; align-items:center; font-size:0.80rem; }
.qref:last-child { border-bottom:none; }
.qref-l { color:var(--txt-m); }
.qref-r { font-family:'DM Mono',monospace; font-size:0.66rem; color:var(--red-pale); }

.empty { border:2px dashed var(--bdr); border-radius:var(--r-lg); padding:56px 24px; text-align:center; background:var(--panel); }
.empty-icon { font-size:2rem; margin-bottom:12px; opacity:0.2; }
.empty-txt { font-size:0.84rem; color:var(--txt-s); line-height:1.7; }

/* ═══════════════════════════════════════════
   LOGIN
═══════════════════════════════════════════ */
.login-hero { text-align:center; padding:64px 0 48px; }
.login-logo {
    font-family:'Instrument Serif',serif;
    font-size:4.2rem; font-weight:400;
    color:var(--txt); letter-spacing:-2px; line-height:1;
    margin-bottom:8px;
    animation:fadeUp 0.6s var(--ease) both;
}
.login-logo span {
    color:var(--red-pale);
    text-shadow:0 0 40px var(--red-glow), 0 0 80px var(--red-glow2);
}
.login-tagline {
    font-family:'DM Mono',monospace;
    font-size:0.56rem; color:var(--txt-f);
    letter-spacing:4.5px; text-transform:uppercase;
    margin-bottom:22px;
    animation:fadeUp 0.6s var(--ease) 0.1s both;
}
.login-desc {
    font-size:0.92rem; color:var(--txt-s); line-height:1.85;
    max-width:400px; margin:0 auto 40px;
    animation:fadeUp 0.6s var(--ease) 0.15s both;
}
"""