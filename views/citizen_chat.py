import streamlit as st
import sqlite3
import random
import json
from google import genai
from google.genai import types

st.title("🗣️ Citizen Intake Portal")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Please describe the local issue you are facing today."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Type your issue here..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    assigned_cat = "Other"
    assigned_urgency = 5
    ai_mode_notice = ""
    
    if "TEMPORARY_GEMINI_KEY" in st.session_state and st.session_state["TEMPORARY_GEMINI_KEY"]:
        try:
            client = genai.Client(api_key=st.session_state["TEMPORARY_GEMINI_KEY"])
            analysis_prompt = f"""
            Analyze this citizen complaint: "{prompt}"
            Classify it into one of these strict categories: 'Water Supply', 'Road Damage', 'Power Outage', 'Garbage'.
            Assign an urgency score from 1 to 10 based on public safety risk.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=analysis_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "category": types.Schema(type=types.Type.STRING),
                            "urgency_score": types.Schema(type=types.Type.INTEGER),
                        },
                        required=["category", "urgency_score"],
                    ),
                ),
            )
            ai_data = json.loads(response.text)
            assigned_cat = ai_data.get("category", "Other")
            assigned_urgency = ai_data.get("urgency_score", 5)
            ai_mode_notice = "✨ Live Gemini AI Categorized"
        except Exception as e:
            assigned_cat = random.choice(["Water Supply", "Road Damage", "Power Outage", "Garbage"])
            assigned_urgency = random.randint(4, 9)
            ai_mode_notice = f"⚠️ Key Error: Used Fallback Parser"
    else:
        # Fallback offline parsing
        prompt_lower = prompt.lower()
        if "water" in prompt_lower or "pipe" in prompt_lower: assigned_cat = "Water Supply"; assigned_urgency = 7
        elif "road" in prompt_lower or "pothole" in prompt_lower: assigned_cat = "Road Damage"; assigned_urgency = 6
        elif "power" in prompt_lower or "electricity" in prompt_lower: assigned_cat = "Power Outage"; assigned_urgency = 8
        elif "garbage" in prompt_lower or "waste" in prompt_lower: assigned_cat = "Garbage"; assigned_urgency = 4
        else: assigned_cat = random.choice(["Water Supply", "Road Damage", "Power Outage", "Garbage"]); assigned_urgency = random.randint(3, 8)
        ai_mode_notice = "💡 Running in Offline Local Rule Mode"

    tracking_id = f"TRK-{random.randint(100, 999)}"
    
    # Generate random localized coordinates around Visakhapatnam area for visualization mapping
    mock_lat = random.uniform(17.6800, 17.7500)
    mock_lon = random.uniform(83.2000, 83.3500)
    
    conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (id, category, urgency_score, summary, status, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tracking_id, assigned_cat, assigned_urgency, prompt, "Pending", mock_lat, mock_lon)
    )
    conn.commit()
    conn.close()
    
    with st.chat_message("assistant"):
        ai_response = f"Grievance filed! Reference ID: **{tracking_id}**. AI Categorized: **{assigned_cat}** (Urgency: **{assigned_urgency}/10**)."
        st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
