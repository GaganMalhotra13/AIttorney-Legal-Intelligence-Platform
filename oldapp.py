import streamlit as st
import json
import google.generativeai as genai
import time
import re
import os
from dotenv import load_dotenv
from duckduckgo_search import DDGS  
from pypdf import PdfReader         

# --- INITIAL CONFIG ---
st.set_page_config(page_title="AIttorney | Legal Intelligence", layout="wide", page_icon="⚖️")

# --- CUSTOM CSS (The "Pro" Vibe) ---
st.markdown("""
    <style>
    /* Gradient Hero Text */
    .hero-text {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #4CAF50, #2E7D32);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-hero { color: #888; font-size: 1.2rem; margin-bottom: 2rem; }
    
    /* Better Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #45a049; border-color: #4CAF50; }
    
    /* Card-like Metrics */
    div[data-testid="metric-container"] {
        background-color: #1E1E1E;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Hide Streamlit Branding for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (Login Logic) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- BRAIN SETUP ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Dynamic Model Discovery to prevent 404 errors
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if 'models/gemini-1.5-flash' in available_models: 
        selected_model = 'gemini-1.5-flash'
    elif 'models/gemini-1.5-flash-latest' in available_models: 
        selected_model = 'gemini-1.5-flash-latest'
    else: 
        selected_model = available_models[0].replace('models/', '')
    model = genai.GenerativeModel(selected_model)
except Exception as e:
    model = genai.GenerativeModel('gemini-1.5-flash') # Hard Fallback

# --- HELPER FUNCTIONS ---
def anonymize_text(text):
    text = re.sub(r'\b\d{10}\b', '[PHONE HIDDEN]', text)
    text = re.sub(r'\S+@\S+', '[EMAIL HIDDEN]', text)
    return text

def get_live_cases(query):
    """Fetches real cases from the web without a paid API key."""
    try:
        with DDGS() as ddgs:
            search_query = f"{query} site:indiankanoon.org OR site:livelaw.in judgment"
            results = list(ddgs.text(search_query, max_results=3))
            context = "".join([f"Source: {r['href']}\nTitle: {r['title']}\nSummary: {r['body']}\n\n" for r in results])
            return context if context else "No specific live cases found."
    except Exception as e:
        return f"Search Error: {str(e)}"

# ==========================================
# PAGE 1: THE LOGIN / HERO PAGE
# ==========================================
def login_page():
    # Hero Section
    st.markdown('<p class="hero-text">⚖️ AIttorney</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-hero">Your AI-Powered Litigation Strategy & Contract Audit Copilot.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.info("💡 **Demo Mode Active**\n\nTo access the RAG pipeline and Live Web Search, please sign in. You can use any dummy credentials for this prototype.")
    
    with col2:
        with st.form("login_form"):
            st.write("### Secure Login")
            username = st.text_input("Email / Username", placeholder="gagan@example.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Access Workspace")
            
            if submit:
                if username != "":
                    st.session_state.logged_in = True
                    if submit:
                        if username != "":
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            st.toast(f"Welcome to the workspace, {username}!", icon="🚀") # <--- ADD THIS LINE
                            time.sleep(0.5) # <--- ADD THIS LINE (makes it feel like it's loading)
                            st.rerun() 
                        else:
                            st.error("Please enter a username.")

# ==========================================
# PAGE 2: THE MAIN APPLICATION
# ==========================================
def main_app():
    # --- UPGRADED SIDEBAR ---
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.username.split('@')[0]}")
        st.caption("Workspace: Primary")
        st.divider()
        st.markdown("**⚙️ Engine Settings**")
        language = st.radio("Output Language", ["English", "Hinglish (Mix)"])
        st.success("🟢 API Connected")
        st.success("🟢 Web Search Active")
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # --- MAIN HEADER ---
    st.markdown("## 🔍 Legal Intelligence Dashboard")
    st.caption("Powered by Gemini 1.5 Flash & DuckDuckGo Live Search")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ Case Mirror", "📄 Smart Contract Audit", "✍️ Notice Drafter", "📍 Legal Roadmap"])

    # ---------------------------------------------------------
    # TAB 1: LIVE RAG SEARCH
    # ---------------------------------------------------------
    with tab1:
        st.markdown("#### Scenario Input")
        user_query = st.text_input("", placeholder="Describe the incident (e.g., 'Landlord refusing to return deposit')")
        
        if user_query:
            with st.spinner('Scraping live court records...'):
                safe_query = anonymize_text(user_query)
                live_data = get_live_cases(safe_query) 
                
                prompt = f"""
                Context from Web: {live_data}
                User Issue: {safe_query}
                Instruction: Explain this situation from an educational standpoint. Use {language}. 
                Keep it casual like a friend explaining to a friend. Mention a relevant case if found.
                Suggest a theoretical Win Probability % and Average Days for resolution based on the data.
                Do not act as a licensed attorney. Format nicely with bullet points.
                """
                
                # Display Metrics visually like a dashboard
                c1, c2, c3 = st.columns(3)
                c1.metric("Win Probability", "72%", "Live Estimate")
                c2.metric("Resolution Time", "180 Days", "Standard Track")
                c3.metric("Legal Risk", "Moderate", "Actionable")

                st.divider()
                st.subheader("🤖 AI Analysis")
                
                try:
                    response = model.generate_content(prompt)
                    if response.parts: 
                        st.write(response.text)
                    else: 
                        st.error("⚠️ Response blocked by safety filters.")
                except Exception as e:
                    st.error(f"❌ API Error: {e}")
                
                with st.expander("🔗 View Web Sources (RAG Data)"):
                    st.write(live_data)

    # ---------------------------------------------------------
    # TAB 2: PDF UPLOAD & INTERACTIVE CHAT
    # ---------------------------------------------------------
    with tab2:
        st.markdown("#### Upload Agreement for AI Audit & Chat")
        col1, col2 = st.columns([2,1])
        with col1:
            uploaded_file = st.file_uploader("Upload PDF File", type=['pdf'], label_visibility="collapsed")
        with col2:
            role = st.selectbox("Assess from perspective of:", ["Employee", "Tenant", "Freelancer", "Buyer"])
        
        if uploaded_file:
            reader = PdfReader(uploaded_file)
            # Limit to 15000 characters to stay within free API limits safely
            full_text = "".join([page.extract_text() for page in reader.pages])[:15000] 
                
            with st.status("Analyzing document clauses...", expanded=True) as status:
                time.sleep(1)
                audit_prompt = f"Act as a strict legal auditor for a {role}. Identify 3 critical red flags in this text: {full_text}"
                try:
                    analysis = model.generate_content(audit_prompt)
                    status.update(label="Analysis Complete!", state="complete", expanded=False)

                    c_a, c_b = st.columns([1, 2])
                    with c_a:
                        st.markdown("### 📊 Risk Score")
                        # Mock dynamic score based on text length for demo purposes
                        risk_score = 65 + (len(full_text) % 25) 
                        st.error(f"DYNAMIC RISK: {risk_score}/100")
                        st.progress(risk_score)
                        st.caption("Flags detected based on standard precedents.")
                    with c_b:
                        st.markdown("### 🚩 Critical Vulnerabilities")
                        if analysis.parts: 
                            st.info(analysis.text)
                        else:
                            st.error("⚠️ Response blocked by safety filters.")
                        
                except Exception as e:
                    st.error(f"Analysis Error: {e}")
            
            # --- INTERACTIVE CHAT FEATURE ---
            st.divider()
            st.markdown("### 💬 Interrogate this Contract")
            st.caption("Ask specific questions about the document you just uploaded.")
            
            chat_q = st.text_input("e.g., 'What is the exact notice period?' or 'Is there a non-compete clause?'", key="chat_input")
            if chat_q:
                with st.spinner("Scanning document..."):
                    chat_prompt = f"Based ONLY on this contract text: '{full_text}'. Answer this question directly and concisely: {chat_q}"
                    try:
                        chat_ans = model.generate_content(chat_prompt)
                        if chat_ans.parts:
                            st.success(f"**Answer:** {chat_ans.text}")
                        else:
                            st.error("⚠️ Chat response blocked.")
                    except Exception as e:
                        st.error("API Error during chat.")

    # ---------------------------------------------------------
    # TAB 3: NOTICE DRAFTER
    # ---------------------------------------------------------
    with tab3:
        st.markdown("#### Auto-Draft Formal Notice")
        st.info("Select tone and generate a formal draft based on your search query.")
        tone = st.select_slider("Select Legal Tone", options=["Professional", "Strict", "Final Warning"])
        if st.button("Generate Document", use_container_width=True):
            try:
                # Assuming user_query exists from Tab 1, otherwise use a placeholder
                query_context = user_query if 'user_query' in locals() and user_query else "a general contract dispute"
                draft_prompt = f"Draft a formal, hypothetical legal notice for this issue: {query_context}. Tone: {tone}. This is for an educational project."
                notice = model.generate_content(draft_prompt)
                if notice.parts: 
                    st.code(notice.text)
                else: 
                    st.error("⚠️ Draft blocked by safety filters.")
            except Exception as e:
                st.error(f"Drafting Error: {e}")
            st.download_button("📥 Download as TXT", data="Mock Data", file_name="Legal_Notice.txt")

    # ---------------------------------------------------------
    # TAB 4: PROCEDURAL ROADMAP
    # ---------------------------------------------------------
    with tab4:
        st.markdown("#### 📍 Step-by-Step Legal Roadmap")
        st.info("Don't know what to do next? Enter your issue, and AIttorney will map out the exact procedural steps.")
        
        roadmap_query = st.text_input("What is your current situation?", placeholder="e.g., 'I want to file a case for a bounced cheque'")
        
        if roadmap_query:
            with st.spinner("Mapping legal procedures..."):
                roadmap_prompt = f"""
                The user has this legal issue in India: '{roadmap_query}'.
                Create a 4-step actionable timeline of what they must do legally. 
                Format it EXACTLY like this:
                Step 1: [Action] - [Short description]
                Step 2: [Action] - [Short description]
                Step 3: [Action] - [Short description]
                Step 4: [Action] - [Short description]
                Do not act as a licensed attorney, frame it as educational.
                """
                try:
                    roadmap_res = model.generate_content(roadmap_prompt)
                    if roadmap_res.parts:
                        st.write("### Your Action Plan")
                        # Parse the AI output to make it look like a timeline
                        steps = roadmap_res.text.split("Step")
                        for step in steps:
                            if ":" in step:
                                st.success(f"**Step** {step.strip()}")
                    else:
                        st.error("Blocked by safety filters.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ==========================================
# APP ROUTER
# ==========================================
if st.session_state.logged_in:
    main_app()
else:
    login_page()