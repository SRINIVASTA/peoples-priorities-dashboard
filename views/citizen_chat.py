import streamlit as st
import sqlite3
import random
import json
from google import genai
from google.genai import types

st.title("🗣️ Citizen Intake Portal")
st.caption("Select the specific street or neighborhood, then describe your grievance contextually.")

# COMPLETE VISAKHAPATNAM GEOSPATIAL NEIGHBORHOOD INDEX
VIZAG_NEIGHBORHOODS = {
    # Central & Commercial Areas
    "Dwaraka Nagar (Main Road)": {"lat": 17.7214, "lon": 83.3032},
    "Daba Gardens (Jail Road)": {"lat": 17.7144, "lon": 83.2987},
    "Asilmetta Junction": {"lat": 17.7226, "lon": 83.3072},
    "Siripuram Junction": {"lat": 17.7214, "lon": 83.3161},
    "Jagadamba Junction": {"lat": 17.7121, "lon": 83.3031},
    "Suryabagh (Main Market)": {"lat": 17.7101, "lon": 83.2965},
    "Ramnagar": {"lat": 17.7220, "lon": 83.3115},
    
    # Residential Hubs & Sectors
    "MVP Colony (Sector 1-5)": {"lat": 17.7406, "lon": 83.3366},
    "MVP Colony (Sector 6-12)": {"lat": 17.7452, "lon": 83.3321},
    "Seethammadhara": {"lat": 17.7412, "lon": 83.3129},
    "Maddilapalem (National Highway)": {"lat": 17.7301, "lon": 83.3195},
    "Akkayyapalem Main Road": {"lat": 17.7285, "lon": 83.2944},
    "Kancharapalem": {"lat": 17.7275, "lon": 83.2750},
    "HB Colony": {"lat": 17.7485, "lon": 83.3210},
    
    # Northern Corridors
    "Madhurawada (Sector 1)": {"lat": 17.8189, "lon": 83.3444},
    "Madhurawada (Mithilapuri Colony)": {"lat": 17.8250, "lon": 83.3510},
    "Arilova Health City Road": {"lat": 17.7645, "lon": 83.3130},
    "Yendada": {"lat": 17.7812, "lon": 83.3482},
    "Rushikonda Beach Road": {"lat": 17.7820, "lon": 83.3835},
    
    # Western & Suburban Corridors
    "Gopalapatnam Main Road": {"lat": 17.7592, "lon": 83.2244},
    "Pendurthi Junction": {"lat": 17.8080, "lon": 83.2215},
    "Simhachalam Hill Down": {"lat": 17.7662, "lon": 83.2505},
    "Adarsh Nagar": {"lat": 17.7288, "lon": 83.3150},
    "Madhavadhara": {"lat": 17.7471, "lon": 83.2544},
    
    # Industrial & Southern Corridors
    "Gajuwaka Junction": {"lat": 17.6896, "lon": 83.2089},
    "Auto Nagar Industrial Estate": {"lat": 17.6750, "lon": 83.1920},
    "Kurmannapalem Junction": {"lat": 17.6712, "lon": 83.1610},
    "Aganampudi Highway Section": {"lat": 17.6625, "lon": 83.1340},
    "Steel Plant Township": {"lat": 17.6350, "lon": 83.1590},
    "Pedagantyada": {"lat": 17.6640, "lon": 83.2149},
    
    # Coastal & Waltair Lines
    "Beach Road (RK Beach Area)": {"lat": 17.7142, "lon": 83.3245},
    "Chinna Waltair": {"lat": 17.7225, "lon": 83.3320},
    "Pedda Waltair": {"lat": 17.7310, "lon": 83.3415},
    "Daspalla Hills": {"lat": 17.7125, "lon": 83.3170}
}

# Group neighborhoods by zones to make choices clear and easy to navigate
sorted_neighborhoods = sorted(list(VIZAG_NEIGHBORHOODS.keys()))

selected_area = st.selectbox(
    "📍 Select Affected Street Location / Ward Corridor:", 
    options=sorted_neighborhoods
)

# Setup continuous chat log stream state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! Please select your precise locality from the index box above, then describe the issue."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle fresh text input
if prompt := st.chat_input("Describe the problem here..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    assigned_cat = "Other"
    assigned_urgency = 5
    ai_mode_notice = ""
    
    # Read the explicit coordinates straight out of the selection configuration data block
    geo_data = VIZAG_NEIGHBORHOODS[selected_area]
    
    # Subtle random coordinate jitter prevents multiple pins at the exact same location from stacking perfectly
    target_lat = geo_data["lat"] + random.uniform(-0.0008, 0.0008)
    target_lon = geo_data["lon"] + random.uniform(-0.0008, 0.0008)

    # Check if password key exists in active memory
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
            ai_mode_notice = f"⚠️ Key Error: Handled by Fallback Parser"
    else:
        # Offline keywords parser for category sorting
        prompt_lower = prompt.lower()
        if "water" in prompt_lower or "pipe" in prompt_lower: assigned_cat = "Water Supply"; assigned_urgency = 7
        elif "road" in prompt_lower or "pothole" in prompt_lower: assigned_cat = "Road Damage"; assigned_urgency = 6
        elif "power" in prompt_lower or "current" in prompt_lower: assigned_cat = "Power Outage"; assigned_urgency = 8
        elif "garbage" in prompt_lower or "waste" in prompt_lower: assigned_cat = "Garbage"; assigned_urgency = 4
        ai_mode_notice = "💡 Running in Offline Local Rule Mode"

    tracking_id = f"TRK-{random.randint(100, 999)}"
    
    # Save clean record transaction directly to your local database file
    conn = sqlite3.connect("peoples_priorities.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO complaints (id, category, urgency_score, summary, status, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tracking_id, assigned_cat, assigned_urgency, prompt, "Pending", target_lat, target_lon)
    )
    conn.commit()
    conn.close()
    
    with st.chat_message("assistant"):
        ai_response = f"Grievance recorded! Reference ID: **{tracking_id}**. Location locked to **{selected_area}**. Category: **{assigned_cat}** (Urgency: **{assigned_urgency}/10**).\n\n*({ai_mode_notice})*"
        st.write(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
