import streamlit as st
import sqlite3
import random
import json
from google import genai
from google.genai import types
from geopy.geocoders import Nominatim

st.title("🗣️ Citizen Intake Portal")
st.caption("Describe your issue contextually in English, Telugu, or Hindi. Be sure to mention the specific neighborhood or street name.")

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
    
    # 1. DYNAMIC CITY-WIDE GEOCODING ENGINE
    # Default fallback coordinates centered on Visakhapatnam City Center
    target_lat = 17.7043
    target_lon = 83.2977
    detected_area = "Visakhapatnam"
    
    # Initialize the free OpenStreetMap geolocator tool
    geolocator = Nominatim(user_agent="peoples_priorities_vizag_tracker")
    
    # First, let's look for a key location word inside the text prompt
    words = prompt.split()
    location_query = ""
    
    # Clean up search strings looking for structural place indicators
    for word in words:
        if word.lower() in ["colony", "street", "nagar", "road", "mvp", "gajuwaka", "madhurawada", "siripuram", "maddilapalem", "jagadamba"]:
            # Try to grab the context surrounding the target word
            idx = words.index(word)
            start_idx = max(0, idx - 2)
            location_query = " ".join(words[start_idx:idx + 2])
            break

    if location_query:
        try:
            # Force the engine to append Visakhapatnam to keep map pins tightly within city limits
            full_search_string = f"{location_query}, Visakhapatnam, Andhra Pradesh, India"
            location = geolocator.geocode(full_search_string, timeout=5)
            
            if location:
                # Add a subtle random jitter so multiple complaints on the exact same street don't stack directly on top of each other
                target_lat = location.latitude + random.uniform(-0.0005, 0.0005)
                target_lon = location.longitude + random.uniform(-0.0005, 0.0005)
                detected_area = location.address.split(',')[0]
        except Exception:
            pass # Keep default city center if API times out

    # 2. CORE CATEGORIZATION ENGINE: Check for live API Key password entries
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
            ai_mode_notice = f"⚠️ Key Error: Fallback Engine Used"
    else:
        # Offline keywords parser for category sorting
        prompt_lower = prompt.lower()
        if "water" in prompt_lower or "pipe" in prompt_lower: assigned_cat = "Water Supply"; assigned_urgency = 7
        elif "road" in prompt_lower or "pothole" in prompt_lower: assigned_cat = "Road Damage"; assigned_urgency = 6
        elif "power" in prompt_lower or "current" in prompt_lower: assigned_cat = "Power Outage"; assigned_urgency = 8
        elif "garbage" in prompt_lower or "waste" in prompt_lower: assigned_cat = "Garbage"; assigned_urgency = 4
        ai_mode_notice = "💡 Running in Offline Local Rule Mode"

    tracking_id = f"TRK-{random.randint(100, 999)}"
    
    # Save target coordinates straight to the main local database file
    conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (id, category, urgency_score, summary, status, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tracking_id, assigned_cat, assigned_urgency, prompt, "Pending", target_lat, target_lon)
    )
    conn.commit()
    conn.close()
    
    with st.chat_message("assistant"):
        ai_response = f"Grievance recorded! Reference ID: **{tracking_id}**. Location identified near **{detected_area}**. Category: **{assigned_cat}** (Urgency: **{assigned_urgency}/10**).\n\n*({ai_mode_notice})*"
        st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
