import streamlit as st
import sqlite3
import random
import json
from google import genai
from google.genai import types

st.title("🗣️ Citizen Intake Portal")
st.caption("Describe your issue contextually in English, Telugu, or Hindi. No formal forms required.")

# Setup continuous chat log stream state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Please describe the local issue you are facing today."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle fresh text input
if prompt := st.chat_input("Type your issue here..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    assigned_cat = "Other"
    assigned_urgency = 5
    ai_mode_notice = ""
    
    # 1. PRIORITY GEOLOCATION EXTRACTOR (Extract neighborhood first)
    target_lat = 17.7406   # Default center point (MVP Colony)
    target_lon = 83.3366
    detected_area = "Visakhapatnam"
    
    prompt_lower = prompt.lower()
    if "mvp" in prompt_lower or "colony" in prompt_lower:
        target_lat = 17.7406 + random.uniform(-0.002, 0.002) # Subtle jitter prevents overlapping map pins
        target_lon = 83.3366 + random.uniform(-0.002, 0.002)
        detected_area = "MVP Colony"
    elif "madhurawada" in prompt_lower:
        target_lat = 17.8189 + random.uniform(-0.002, 0.002)
        target_lon = 83.3444 + random.uniform(-0.002, 0.002)
        detected_area = "Madhurawada"
    elif "gajuwaka" in prompt_lower:
        target_lat = 17.6896 + random.uniform(-0.002, 0.002)
        target_lon = 83.2089 + random.uniform(-0.002, 0.002)
        detected_area = "Gajuwaka"
    else:
        target_lat = 17.7406 + random.uniform(-0.01, 0.01)
        target_lon = 83.3366 + random.uniform(-0.01, 0.01)
        detected_area = "General Area"

    # 2. CORE ENGINE: Check if password key exists in active memory
    if "TEMPORARY_GEMINI_KEY" in st.session_state and st.session_state["TEMPORARY_GEMINI_KEY"]:
        try:
            # Initialize live client with the temporary password string
            client = genai.Client(api_key=st.session_state["TEMPORARY_GEMINI_KEY"])
            
            analysis_prompt = f"""
            Analyze this citizen complaint: "{prompt}"
            Classify it into one of these strict categories: 'Water Supply', 'Road Damage', 'Power Outage', 'Garbage'.
            Assign an urgency score from 1 to 10 based on public safety risk.
            """
            
            # Using structured schema constraints to force precise outputs
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
            # Fallback categorization engine if key error occurs
            if "water" in prompt_lower or "pipe" in prompt_lower: assigned_cat = "Water Supply"
            elif "road" in prompt_lower or "pothole" in prompt_lower: assigned_cat = "Road Damage"
            else: assigned_cat = "Other"
            ai_mode_notice = f"⚠️ Key Error: Handled by Local Parser"
    else:
        # 3. OFFLINE CATEGORIZATION RULES ENGINE (Runs second to prevent geo-overwrite)
        if "water" in prompt_lower or "pipe" in prompt_lower:
            assigned_cat = "Water Supply"
            assigned_urgency = 7
        elif "road" in prompt_lower or "pothole" in prompt_lower:
            assigned_cat = "Road Damage"
            assigned_urgency = 6
        elif "power" in prompt_lower or "current" in prompt_lower:
            assigned_cat = "Power Outage"
            assigned_urgency = 8
        elif "garbage" in prompt_lower or "waste" in prompt_lower:
            assigned_cat = "Garbage"
            assigned_urgency = 4
        else:
            assigned_cat = "Other"
            assigned_urgency = 5
        ai_mode_notice = "💡 Running in Offline Local Rule Mode"

    tracking_id = f"TRK-{random.randint(100, 999)}"
    
    # Save transaction record directly to your local database file
    conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (id, category, urgency_score, summary, status, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tracking_id, assigned_cat, assigned_urgency, prompt, "Pending", target_lat, target_lon)
    )
    conn.commit()
    conn.close()
    
    with st.chat_message("assistant"):
        ai_response = f"Grievance filed! Reference ID: **{tracking_id}**. Area Mapped: **{detected_area}**. Classified under **{assigned_cat}** with an Urgency rating of **{assigned_urgency}/10**.\n\n*({ai_mode_notice})*"
        st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
