"""
pages/case_mirror.py — AIttorney v6
The legal intelligence terminal. 11 AI modules. 18 sources. One input.
"""
import streamlit as st
import time
from utils.anonymize import anonymize
from utils.search import get_live_cases, get_source_registry
from utils.ai import analyze_case, get_applicable_laws
from utils.scoring import compute_win_probability
from utils.legal_brain import (
    generate_legal_brief, analyze_opponent, evidence_checklist,
    estimate_settlement, case_strength_timeline, jurisdiction_advisor,
    fir_draft, mediation_script, limitation_checker, case_comparator,
)
from utils.database import save_case
from config import QUICK_SCENARIOS

CASE_TYPES = [
    "Consumer Dispute", "Cheque Bounce (NI Act §138)", "Employment / Labour",
    "Property / Real Estate", "Landlord / Tenant", "Family / Matrimonial",
    "Motor Accident", "Cyber Crime / Online Fraud", "Criminal / FIR",
    "Medical Negligence", "Contract Breach", "Other",
]

EXAMPLES = [
    "Landlord won't return ₹80,000 deposit after 4 months",
    "Fired the day after filing a harassment complaint",
    "Received a bounced cheque of ₹3.5 lakhs from supplier",
    "Builder 2 years late on flat delivery, now demanding more money",
    "Online store sent fake product, ignoring refund requests",
    "Neighbour constructed wall encroaching on my property",
    "Hospital overcharged and gave wrong treatment",
    "UPI fraud — ₹45,000 transferred to scammer",
]


def _gauge(prob: int, grade: str) -> str:
    c = {"Strong":"#2A9E6A","Moderate":"#D48B2A","Weak":"#C4472A"}.get(grade,"#6A7A8A")
    f = int((prob/100)*163)
    return f"""<div style="text-align:center;padding:6px 0;">
<svg width="130" height="76" viewBox="0 0 130 76" style="overflow:visible;">
<path d="M 10 72 A 55 55 0 0 1 120 72" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="10" stroke-linecap="round"/>
<path d="M 10 72 A 55 55 0 0 1 120 72" fill="none" stroke="{c}" stroke-width="10" stroke-linecap="round" stroke-dasharray="{f} 163"/>
<text x="65" y="66" text-anchor="middle" font-family="Lora,serif" font-size="26" font-weight="700" fill="{c}">{prob}%</text>
<text x="65" y="78" text-anchor="middle" font-family="DM Mono,monospace" font-size="8" fill="#6A7A8A" letter-spacing="2">{grade.upper()}</text>
</svg></div>"""


def _timeline_html(stages: list[dict]) -> str:
    if not stages: return ""
    html = '<div style="margin-top:6px;">'
    for s in stages:
        p = s.get("prob", 50)
        c = "#2A9E6A" if p >= 60 else "#D48B2A" if p >= 40 else "#C4472A"
        html += f"""
        <div style="margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:0.80rem;color:var(--txt-m);font-weight:500;">{s['stage']}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.72rem;color:{c};font-weight:600;">{p}%</span>
          </div>
          <div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px;overflow:hidden;">
            <div style="width:{p}%;height:100%;background:{c};border-radius:3px;"></div>
          </div>
          <div style="font-size:0.72rem;color:var(--txt-s);margin-top:3px;line-height:1.4;">{s.get('note','')}</div>
        </div>"""
    html += "</div>"
    return html


def _ai_box(content: str, byline: str = "AIttorney") -> str:
    return f"""<div class="ai-wrap">
  <div class="ai-icon">⚖️</div>
  <div class="ai-box"><div class="ai-by">{byline}</div>
  {content.replace(chr(10),"<br>")}</div></div>"""


def render(language: str):
    st.markdown('<div class="eyebrow">Legal Intelligence Terminal · 11 AI Modules · 18 Sources</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-h">What\'s Your <em>Legal Situation?</em></h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Plain language in. Full legal intelligence out — win probability, applicable laws, opponent analysis, evidence checklist, settlement range, jurisdiction guide, FIR draft, mediation script, limitation check, case comparisons, and a structured legal brief. All sourced from 18 live Indian legal databases.</p>', unsafe_allow_html=True)

    # ── HERO SEARCH ───────────────────────────────────────────
    st.markdown('<div class="search-hero">', unsafe_allow_html=True)
    st.markdown('<div class="search-hero-label">Describe your situation in plain language</div>', unsafe_allow_html=True)
    user_query = st.text_area("Q", placeholder="e.g.  'My landlord refuses to return ₹50,000 deposit. I vacated with 30-day written notice 3 months ago. He won't respond to calls or WhatsApp.'",
        height=88, label_visibility="collapsed", key="main_query")
    st.markdown('<div class="search-footer">', unsafe_allow_html=True)
    st.markdown('<div class="search-pills">' + "".join(f'<span class="pill">{e[:32]}{"…" if len(e)>32 else ""}</span>' for e in EXAMPLES[:5]) + '</div>', unsafe_allow_html=True)
    st.markdown('<div class="pii-badge">🛡️ PII Auto-Redacted Before Any API Call</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ── CONFIG ROW ────────────────────────────────────────────
    cc1, cc2, cc3, cc4, cc5 = st.columns([2, 1.4, 1.2, 1.2, 0.9])
    with cc1: case_type = st.selectbox("Case Type", CASE_TYPES)
    with cc2: claim_amt = st.number_input("Claim (₹)", min_value=0, value=0, step=5000)
    with cc3: location  = st.selectbox("Location", ["India (General)","Delhi NCR","Mumbai","Bangalore","Chennai","Kolkata","Hyderabad","Other"])
    with cc4: incident_date = st.text_input("Incident Date", placeholder="DD/MM/YYYY")
    with cc5:
        st.markdown("<br>", unsafe_allow_html=True)
        run = st.button("Analyze →", use_container_width=True)

    # ── IDLE STATE ────────────────────────────────────────────
    if not run:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="lbl">11 AI Modules Activated by a Single Input</div>', unsafe_allow_html=True)
        r1 = st.columns(4)
        r2 = st.columns(4)
        mods = [
            ("⚖️","Win Probability","28-signal scoring engine — fully explainable"),
            ("🥊","Opponent Analysis","Steelmans opposing arguments + counter-strategies"),
            ("📋","Evidence Checklist","Case-specific docs + witnesses to gather now"),
            ("💰","Settlement Estimate","Realistic ₹ range from Indian court patterns"),
            ("🗺️","Jurisdiction Guide","Exact court/forum, fees, limitation, filing steps"),
            ("📈","Case Timeline","Win probability modeled at each litigation stage"),
            ("📄","Legal Brief","Structured brief your advocate can use directly"),
            ("🚨","FIR Draft","Police complaint with IPC/BNS sections auto-identified"),
            ("🤝","Mediation Script","Pre-litigation negotiation talking points"),
            ("⏰","Limitation Check","Is your case still fileable? Deadline math"),
            ("🔍","Case Comparator","Your facts vs. similar decided Indian court cases"),
        ]
        for col, (icon, lbl, desc) in zip(r1, mods[:4]):
            with col: st.markdown(f'<div class="feat"><div class="feat-icon">{icon}</div><div class="feat-label">{lbl}</div><div class="feat-desc">{desc}</div></div>', unsafe_allow_html=True)
        for col, (icon, lbl, desc) in zip(r2, mods[4:8]):
            with col: st.markdown(f'<div class="feat"><div class="feat-icon">{icon}</div><div class="feat-label">{lbl}</div><div class="feat-desc">{desc}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="lbl">18 Live Indian Legal Sources</div>', unsafe_allow_html=True)
        sources = get_source_registry()
        tier3 = [s for s in sources if s["tier"]==3]
        tier2 = [s for s in sources if s["tier"]==2]
        chips  = '<div class="src-row" style="margin-top:6px;">'
        for s in tier3: chips += f'<span class="src-chip" style="border-color:rgba(196,71,42,0.4);color:var(--red-pale);">⭐ {s["domain"]}</span>'
        for s in tier2: chips += f'<span class="src-chip">{s["domain"]}</span>'
        chips += '</div>'
        st.markdown(chips, unsafe_allow_html=True)
        return

    # ── VALIDATE ──────────────────────────────────────────────
    query = user_query.strip()
    if not query:
        st.warning("Please describe your situation above.")
        return
    safe_query = anonymize(query)

    # ── CORE PIPELINE ─────────────────────────────────────────
    prog = st.progress(0, text="🔍 Querying 18 Indian legal databases via 5 search strategies…")
    live_ctx, raw_results = get_live_cases(safe_query)
    prog.progress(25, text="📊 Running 28-signal scoring engine…")
    score_data = compute_win_probability(safe_query, live_ctx)
    prog.progress(45, text="⚖️ Identifying applicable laws…")
    laws_text = get_applicable_laws(safe_query)
    prog.progress(65, text="🤖 Synthesizing full analysis…")
    analysis  = analyze_case(safe_query, live_ctx, language)
    prog.progress(100, text="✅ Core pipeline complete.")
    time.sleep(0.25)
    prog.empty()

    prob  = score_data["probability"]
    grade = score_data["grade"]
    pos   = score_data["positive_factors"]
    neg   = score_data["negative_factors"]

    # SCORECARD
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="lbl">Case Assessment</div>', unsafe_allow_html=True)
    sc1, sc2, sc3, sc4 = st.columns(4)
    gc = {"Strong":"var(--grn)","Moderate":"var(--amber)","Weak":"var(--red-pale)"}.get(grade,"var(--txt-s)")

    with sc1:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Win Probability</div>{_gauge(prob,grade)}<div class="mc-sub" style="text-align:center;">{score_data["confidence"]} Confidence<br><span style="font-family:DM Mono,monospace;font-size:0.58rem;color:var(--txt-f);">{len(pos)+len(neg)} signals</span></div></div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Avg. Resolution</div><div class="mc-val v-a" style="margin:8px 0 2px;">~{score_data["resolution_days"]}</div><div style="font-family:DM Mono,monospace;font-size:0.54rem;color:var(--txt-s);margin-bottom:6px;">DAYS</div><div class="mc-sub">{score_data["resolution_label"]}</div><div class="mc-bar" style="margin-top:12px;"><div class="mc-fill" style="width:{min(100,score_data["resolution_days"]//6)}%;background:var(--amber);"></div></div></div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="mc"><div class="mc-lbl">Legal Position</div><div class="mc-val" style="color:{gc};font-size:1.9rem;margin:8px 0 4px;">{grade}</div><div class="mc-sub">{len(pos)} for · {len(neg)} against</div><div class="mc-bar" style="margin-top:12px;"><div class="mc-fill" style="width:{prob}%;background:{gc};"></div></div></div>', unsafe_allow_html=True)
    with sc4:
        topic_label = raw_results[0].get("_topic","general").replace("_"," ").title() if raw_results else "General"
        st.markdown(f'<div class="mc"><div class="mc-lbl">Sources Retrieved</div><div class="mc-val v-b" style="margin:8px 0 4px;">{len(raw_results)}</div><div class="mc-sub">Across 18 legal databases<br><span style="font-family:DM Mono,monospace;font-size:0.58rem;color:var(--txt-f);">Topic: {topic_label}</span></div><div class="mc-bar" style="margin-top:12px;"><div class="mc-fill" style="width:{min(100,len(raw_results)*10)}%;background:var(--blu);"></div></div></div>', unsafe_allow_html=True)

    # Scoring breakdown
    if pos or neg:
        with st.expander("📊 Transparent Scoring Breakdown — How was this calculated?"):
            fc1, fc2 = st.columns(2)
            with fc1:
                if pos:
                    st.markdown('<div class="lbl">Strengthening Factors</div>', unsafe_allow_html=True)
                    for f in pos:
                        p = f.split("  —  "); delta=p[0].strip(); reason=p[1].strip() if len(p)>1 else ""
                        st.markdown(f'<div class="factor-row"><span class="factor-pos">{delta}</span><span class="factor-text">{reason}</span></div>', unsafe_allow_html=True)
            with fc2:
                if neg:
                    st.markdown('<div class="lbl">Weakening Factors</div>', unsafe_allow_html=True)
                    for f in neg:
                        p = f.split("  —  "); delta=p[0].strip(); reason=p[1].strip() if len(p)>1 else ""
                        st.markdown(f'<div class="factor-row"><span class="factor-neg">{delta}</span><span class="factor-text">{reason}</span></div>', unsafe_allow_html=True)
            st.caption("28-signal keyword-weighted heuristic. Not a statistical model. Consult an advocate.")

    # LAWS + ANALYSIS
    st.markdown("<br>", unsafe_allow_html=True)
    la1, la2 = st.columns([1, 2])
    with la1:
        st.markdown('<div class="lbl">⚖️ Applicable Laws</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card"><div class="result-card-body" style="font-size:0.84rem;color:var(--txt-m);line-height:1.9;">{laws_text.replace(chr(10),"<br>")}</div></div>', unsafe_allow_html=True)
    with la2:
        st.markdown('<div class="lbl">🤖 Full Analysis</div>', unsafe_allow_html=True)
        st.markdown(_ai_box(analysis, f"AIttorney · Live RAG · {language}"), unsafe_allow_html=True)

    # LIVE SOURCES
    if raw_results:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="lbl">{len(raw_results)} Results — 18 Indian Legal Databases — Authority-Ranked</div>', unsafe_allow_html=True)
        grid = '<div class="src-grid">'
        for r in raw_results[:6]:
            domain = r.get("href","").split("/")[2].replace("www.","") if "href" in r else "source"
            title  = r.get("title","")[:72]
            weight = r.get("_weight", 1)
            star   = "⭐ " if weight == 3 else ""
            grid  += f'<a href="{r.get("href","#")}" target="_blank" style="text-decoration:none;"><div class="src-card"><div class="src-domain">{star}{domain}</div><div class="src-title">{title}</div></div></a>'
        grid += "</div>"
        st.markdown(grid, unsafe_allow_html=True)

    # 11 ADVANCED AI MODULES
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="lbl">Advanced Intelligence Modules — On-Demand</div>', unsafe_allow_html=True)
    st.caption("Each runs a separate focused AI call with its own search strategy. Generate only what you need.")

    tab_opp, tab_ev, tab_set, tab_jur, tab_tl, tab_brief, tab_fir, tab_med, tab_lim, tab_cmp = st.tabs([
        "🥊 Opponent", "📋 Evidence", "💰 Settlement",
        "🗺️ Jurisdiction", "📈 Timeline", "📄 Brief",
        "🚨 FIR Draft", "🤝 Mediation", "⏰ Limitation", "🔍 Case Compare",
    ])

    # ── OPPONENT ──────────────────────────────────────────────
    with tab_opp:
        st.markdown('<div class="lbl">What Will the Other Side Argue?</div>', unsafe_allow_html=True)
        st.caption("AI steelmans the opposing position as strongly as possible, identifies your vulnerabilities, and gives counter-strategies. Do this before filing — not after.")
        if st.button("Generate Opponent Analysis →", key="opp"):
            with st.spinner("Building strongest case for the other side…"):
                st.session_state["opp"] = analyze_opponent(safe_query, live_ctx)
        if st.session_state.get("opp"):
            st.markdown(_ai_box(st.session_state["opp"], "AIttorney · Devil's Advocate Mode"), unsafe_allow_html=True)

    # ── EVIDENCE ──────────────────────────────────────────────
    with tab_ev:
        st.markdown('<div class="lbl">Exact Evidence & Documents to Gather</div>', unsafe_allow_html=True)
        st.caption("Case-specific checklist — Critical, Important, and Supportive evidence. Includes digital evidence, witnesses, and limitation warnings.")
        if st.button("Generate Evidence Checklist →", key="ev"):
            with st.spinner("Building case-specific evidence checklist…"):
                st.session_state["ev"] = evidence_checklist(safe_query, case_type)
        if st.session_state.get("ev"):
            st.markdown(_ai_box(st.session_state["ev"], "AIttorney · Evidence Module"), unsafe_allow_html=True)

    # ── SETTLEMENT ────────────────────────────────────────────
    with tab_set:
        st.markdown('<div class="lbl">Realistic Settlement Range</div>', unsafe_allow_html=True)
        if claim_amt == 0:
            st.info("Enter a claim amount in the top row to unlock the settlement estimator.")
        else:
            st.caption(f"Settlement analysis for ₹{claim_amt:,.0f} — pessimistic, realistic, optimistic ranges with fight-or-settle recommendation.")
            if st.button("Generate Settlement Estimate →", key="set"):
                with st.spinner("Analysing Indian court award patterns…"):
                    st.session_state["set"] = estimate_settlement(safe_query, claim_amt, case_type, live_ctx)
            if st.session_state.get("set"):
                st.markdown(_ai_box(st.session_state["set"], "AIttorney · Settlement Module"), unsafe_allow_html=True)

    # ── JURISDICTION ──────────────────────────────────────────
    with tab_jur:
        st.markdown('<div class="lbl">Which Court Should You File In?</div>', unsafe_allow_html=True)
        st.caption("Exact forum recommendation with filing fee, jurisdiction limits, limitation period, required documents, and the #1 mistake to avoid.")
        if st.button("Get Jurisdiction Advice →", key="jur"):
            with st.spinner("Analysing optimal jurisdiction…"):
                st.session_state["jur"] = jurisdiction_advisor(safe_query, location)
        if st.session_state.get("jur"):
            st.markdown(_ai_box(st.session_state["jur"], "AIttorney · Jurisdiction Module"), unsafe_allow_html=True)

    # ── TIMELINE ──────────────────────────────────────────────
    with tab_tl:
        st.markdown('<div class="lbl">Win Probability at Each Litigation Stage</div>', unsafe_allow_html=True)
        st.caption("6-stage model: Notice → Filing → Interim Relief → Evidence → Judgment → Appeal. Shows where you peak and where you're most vulnerable.")
        if st.button("Generate Case Timeline →", key="tl"):
            with st.spinner("Modelling case progression across 6 stages…"):
                st.session_state["tl"] = case_strength_timeline(safe_query, score_data, case_type)
        if st.session_state.get("tl"):
            st.markdown(f'<div class="result-card"><div class="result-card-header"><span class="result-card-title">Case Strength Across Litigation Stages</span></div><div class="result-card-body">{_timeline_html(st.session_state["tl"])}</div></div>', unsafe_allow_html=True)

    # ── LEGAL BRIEF ───────────────────────────────────────────
    with tab_brief:
        st.markdown('<div class="lbl">Structured Legal Brief</div>', unsafe_allow_html=True)
        st.caption("Statement of Facts → Issues of Law → Arguments → Counter-Arguments → Relief Sought → Recommendation. Hand this to your advocate as a starting point.")
        party = st.text_input("Your name for the brief:", placeholder="e.g. Rajesh Kumar", key="party")
        if st.button("Generate Legal Brief →", key="brief"):
            with st.spinner("Drafting structured brief…"):
                st.session_state["brief"] = generate_legal_brief(safe_query, live_ctx, score_data, laws_text, party or "Complainant")
        if st.session_state.get("brief"):
            st.markdown(f'<div class="notice-box">{st.session_state["brief"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("📥 Download .txt", data=st.session_state["brief"], file_name="Legal_Brief.txt", mime="text/plain", use_container_width=True)
            with c2:
                try:
                    from utils.pdf_generator import generate_notice_pdf, REPORTLAB_AVAILABLE
                    if REPORTLAB_AVAILABLE:
                        pdf = generate_notice_pdf(st.session_state["brief"], {"tone":"Legal Brief","date":"","sender":party})
                        if pdf:
                            st.download_button("📄 Download .pdf", data=pdf, file_name="Legal_Brief.pdf", mime="application/pdf", use_container_width=True)
                except: pass

    # ── FIR DRAFT ─────────────────────────────────────────────
    with tab_fir:
        st.markdown('<div class="lbl">FIR / Police Complaint Draft</div>', unsafe_allow_html=True)
        st.caption("Auto-identifies applicable IPC/BNS sections, structures the complaint chronologically, specifies which police station has jurisdiction.")
        f1, f2 = st.columns(2)
        with f1: complainant_name = st.text_input("Your full name:", key="fir_name", placeholder="Full Name")
        with f2: accused_desc = st.text_input("Accused description:", key="fir_accused", placeholder="e.g. John Doe, shopkeeper at...")
        if st.button("Generate FIR Draft →", key="fir"):
            with st.spinner("Identifying IPC/BNS sections and drafting complaint…"):
                st.session_state["fir"] = fir_draft(safe_query, complainant_name, accused_desc, location)
        if st.session_state.get("fir"):
            st.markdown(f'<div class="notice-box">{st.session_state["fir"].replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            st.download_button("📥 Download FIR Draft", data=st.session_state["fir"], file_name="FIR_Draft.txt", mime="text/plain", use_container_width=True)

    # ── MEDIATION ─────────────────────────────────────────────
    with tab_med:
        st.markdown('<div class="lbl">Pre-Litigation Mediation Script</div>', unsafe_allow_html=True)
        st.caption("Opening statement, core demands, concessions to offer, red lines, objection handling, and closing language. Prepare before the conversation, not during.")
        m1, m2 = st.columns(2)
        with m1: your_pos = st.text_area("Your position in 1-2 sentences:", height=70, key="med_pos", placeholder="e.g. I am the aggrieved tenant who paid ₹80k deposit and vacated properly...")
        with m2: ideal_out = st.text_area("Your ideal outcome:", height=70, key="med_out", placeholder="e.g. Full deposit returned within 15 days + written apology")
        other_p = st.text_input("Describe the other party:", key="med_other", placeholder="e.g. Landlord, owns building, claims damage to property")
        if st.button("Generate Mediation Script →", key="med"):
            with st.spinner("Building mediation strategy…"):
                st.session_state["med"] = mediation_script(safe_query, your_pos, other_p, ideal_out)
        if st.session_state.get("med"):
            st.markdown(_ai_box(st.session_state["med"], "AIttorney · Mediation Module"), unsafe_allow_html=True)

    # ── LIMITATION ────────────────────────────────────────────
    with tab_lim:
        st.markdown('<div class="lbl">Limitation Period Check</div>', unsafe_allow_html=True)
        date_display = incident_date if incident_date else "Not provided"
        if not incident_date:
            st.warning("Enter the incident date in the top row for an accurate limitation check.")
        else:
            st.caption(f"Checking filing deadline for a {case_type} case from {date_display}.")
        if st.button("Check Limitation Period →", key="lim"):
            with st.spinner("Calculating limitation period and checking recent condonation cases…"):
                st.session_state["lim"] = limitation_checker(case_type, date_display, safe_query)
        if st.session_state.get("lim"):
            st.markdown(_ai_box(st.session_state["lim"], "AIttorney · Limitation Module"), unsafe_allow_html=True)

    # ── CASE COMPARATOR ───────────────────────────────────────
    with tab_cmp:
        st.markdown('<div class="lbl">Compare Your Case to Decided Precedents</div>', unsafe_allow_html=True)
        st.caption("AI matches your facts to similar Indian court cases, shows how those courts ruled, and applies the legal reasoning to your situation. Closest to genuine legal research.")
        if st.button("Compare to Decided Cases →", key="cmp"):
            with st.spinner("Searching decided cases and comparing facts…"):
                try:
                    st.session_state["cmp"] = case_comparator(safe_query, live_ctx, case_type)
                except Exception as e:
                 st.error(f"Error: {e}")
                import traceback
                st.code(traceback.format_exc())
        if st.session_state.get("cmp"):
            st.markdown(_ai_box(st.session_state["cmp"], "AIttorney · Case Comparator Module"), unsafe_allow_html=True)

    # ── RAW + SAVE ────────────────────────────────────────────
    with st.expander("🔧 Raw RAG Context (Debug)"):
        st.code(live_ctx, language=None)

    save_case(st.session_state.username, query, analysis, prob, grade)
    st.markdown('<div style="font-size:0.64rem;color:var(--txt-f);margin-top:8px;font-family:DM Mono,monospace;">✓ Saved to history</div>', unsafe_allow_html=True)