import streamlit as st
import sqlite3
import random
import json
from google import genai
from google.genai import types

st.title("🗣️ Citizen Intake Portal")
st.caption("Select your neighborhood area from the checklist index, then describe your grievance contextually.")

# 1. STRUCTURAL GEOLOCATION INDEX (Ensures exact, non-overlapping regional mapping)
VIZAG_NEIGHBORHOODS = {
    "MVP Colony": {"lat": 17.7406, "lon": 83.3366},
    "Gopalapatnam": {"lat": 17.7592, "lon": 83.2244},
    "Adarsh Nagar": {"lat": 17.7288, "lon": 83.3150},
    "Madhurawada": {"lat": 17.8189, "lon": 83.3444},
    "Gajuwaka": {"lat": 17.6896, "lon": 83.2089},
    "Siripuram": {"lat": 17.7214, "lon": 83.3161},
    "Maddilapalem": {"lat": 17.7301, "lon": 83.3195},
    "Jagadamba Junction": {"lat": 17.7121, "lon": 83.3031}
}

# Add a clear UI dropdown selection tool right at the top
selected_area = st.selectbox(
    "📍 Select Affected Neighborhood / Locality:", 
    options=list(VIZAG_NEIGHBORHOODS.keys())
)

# Setup continuous chat log stream state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Please select your locality above, then describe the infrastructure issue you are facing today."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle fresh text input
if prompt := st.chat_input("Describe the problem here..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    assigned_cat = "Other"
    assigned_urgency = 5
    ai_mode_notice = ""
    
    # Extract the exact fixed coordinates based on the user's dropdown choice
    geo_data = VIZAG_NEIGHBORHOODS[selected_area]
    
    # Add a safe, tightly controlled coordinate jitter so multiple pins in the same area don't stack perfectly on top of each other
    target_lat = geo_data["lat"] + random.uniform(-0.0015, 0.0015)
    target_lon = geo_data["lon"] + random.uniform(-0.0015, 0.0015)

    # 2. CORE ENGINE: Check if password key exists in active memory
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
            assigned_cat = "Other"
            ai_mode_notice = f"⚠️ Key Error: Handled by Local Parser"
    else:
        # Offline keywords parser for category sorting
        prompt_lower = prompt.lower()
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
        ai_response = f"Grievance filed! Reference ID: **{tracking_id}**. Location locked to **{selected_area}**. Category: **{assigned_cat}** (Urgency: **{assigned_urgency}/10**).\n\n*({ai_mode_notice})*"
        st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
