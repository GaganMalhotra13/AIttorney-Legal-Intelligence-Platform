# ⚖️ AIttorney - AI Legal Research & Contract Audit Platform

AIttorney is a dynamic LawTech platform that leverages **Retrieval-Augmented Generation (RAG)** to provide real-time legal research, case mirroring, and contract auditing. Built with Python and Streamlit, it orchestrates Google Gemini 1.5 and live web scraping to translate complex Indian Penal Code (BNS/IPC) statutes into accessible summaries and assess legal documents for vulnerabilities.

## 🚀 Features
- **Live Case Mirroring (Dynamic RAG):** Scrapes real-time legal precedents from IndianKanoon and LiveLaw via DuckDuckGo search integration.
- **Contract Intelligence Audit:** Uses `pypdf` to extract text from uploaded legal agreements and flags role-specific vulnerabilities (e.g., predatory clauses for tenants or employees).
- **Auto-Draft Legal Notices:** Generates customized, formal legal notices based on user-provided situational context and selected tone parameters.
- **Privacy-First Processing:** Implements regex-based PII scrubbers to anonymize phone numbers and email addresses before passing data to the LLM.

## 🛠️ Tech Stack
- **Frontend/UI:** Streamlit
- **AI/LLM Engine:** Google Gemini 1.5 Flash (via `google-generativeai`)
- **Search Retrieval:** `duckduckgo-search`
- **Document Processing:** `pypdf`

## ⚙️ Local Installation & Setup
