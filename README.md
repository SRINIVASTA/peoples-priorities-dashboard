# 🏛️ People's Priorities Dashboard (Streamlit Edition)

An AI-powered, zero-cloud-cost citizen grievance tracking and analytical intelligence platform built entirely in Python. Inspired by the core community engagement workflows of the People's Priorities platform, this application acts as a dual-sided portal connecting local citizen feedback directly with Members of Parliament (MPs) and verification staff.

---

## 🚀 Key Features

* **💬 Multilingual Citizen Intake Portal:** Contextual chatbot interface processing natural inputs across English, Telugu, and Hindi. No rigid form layout constraints.
* **✨ Intelligent Location-Category Linker:** Rule-based fallback system and structural LLM output constraints mapping inputs natively onto regional sectors (e.g., MVP Colony, Madhurawada, Gajuwaka).
* **🔑 Zero-Trust Key Management:** High-security sidebar password box frame. Paste your key directly into the application layout; it remains isolated within active session memory, completely hidden from version control.
* **📊 MP Analytical Hotspot Grid:** OpenStreetMap-driven density visuals scaling bubble sizes dynamically against urgency metrics.
* **🛡️ Operational Staff Desk:** Live editable spreadsheet engine (`st.data_editor`) allowing workflow transitions (Pending ➡️ Verified ➡️ Resolved) saved back to the database.

---

## 🛠️ Technology Stack

* **Frontend & Server Engine:** Streamlit Framework
* **AI Core Integration:** Google GenAI SDK (`gemini-2.5-flash`)
* **Analytical Mapping Layer:** Plotly Express (`scatter_mapbox`)
* **Storage Layer:** Serverless SQLite Engine (`peoples_priorities.db`)

---

## 📂 Project Architecture

```text
peoples_priorities_app/
├── app.py                  # Main Registry, Database Init & Sidebar Auth
├── requirements.txt         # Dependency Package List
├── .gitignore               # Safe Tracking Filters (Excludes .db files)
└── views/
    ├── citizen_chat.py      # Intake Chatbot & Geo-Fencing Routing Logic
    ├── mp_dashboard.py      # Interactive Analytical Charts & Zoom Maps
    └── staff_console.py     # Grid Editor for Task Triaging & Lifecycle Updates
```

---

## 🔧 Installation & Local Setup

### 1. Clone the Workspace
```bash
git clone https://github.com
cd peoples-priorities-dashboard
```

### 2. Provision Dependencies
Ensure Python 3.11+ is initialized. Install the package configurations using your terminal:
```bash
pip install -r requirements.txt
```

### 3. Initialize Local Session Run
```bash
streamlit run app.py
```

---

## 🔒 Security Best Practices

This repository utilizes a **Zero-Persistence Secrets** architecture. 
* **Never** store your `AIzaSy...` key directly inside code blocks.
* To activate live AI features, use the **🔑 Authentication** panel on the live interface. 
* The configuration uses a hard `.gitignore` block to ensure local state databases are completely filtered out from public cloud branches:
  ```text
  *.db
  .streamlit/
  __pycache__/
  ```

---

## 💡 How to Test the Tracking Workflow
1. Run the application frame and open the sidebar menu.
2. Paste your Google AI Studio API Key into the password-masked box (or run blank for rule-based mock testing).
3. Navigate to **🗣️ Report an Issue**, type: `Road pothole near MVP Colony sector 2`, and submit.
4. Click **📊 View MP Dashboard**. The map camera center automatically recalculates onto the street coordinates of **MVP Colony** with precise, jitter-controlled visualization dots.
