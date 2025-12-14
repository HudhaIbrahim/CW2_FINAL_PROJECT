import streamlit as st
from app.data.db import connect_database
from app.data.incidents import Incident
import datetime
from openai import OpenAI

st.set_page_config(
    page_title="Cyber Incidents Dashboard",
    page_icon="👾",
    layout="wide"
)

# Session state guards
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
     st.error("You must be logged in to view the dashboard.")
     if st.button("Go to login page"):
        st.switch_page("Home.py") # back to the first page
     st.stop()

# If logged in, show dashboard content
st.title("👾 Cyber Incidents Dashboard")
st.success(f"Hello, **{st.session_state.username}**!")

incident_tab, analytics_tab, AI_tab = st.tabs(["Incidents", "Analytics", "AI Incident Analyzer"])

with incident_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Read and display the database as a table
    incidents = Incident.get_all_incidents()
    st.dataframe(incidents, use_container_width=True)

    # Add new incidents to the database with a form
    with st.form("new_incident"):
        # Form inputs
        incident_date = st.date_input(
            "Incident Date",
            value=datetime.date.today(),  # Default to today
            max_value=datetime.date.today()  # Can't select future dates
        )
        description = st.text_input("Incident Description")
        severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
        status = st.selectbox("Status", ["open", "in progress", "resolved", "closed", "investigating"])
        incident_type = st.selectbox("Incident Type", ["data_breach", "phishing", "ddos", "malware", "unauthorized_access", "ransomware"])
        reported_by = st.text_input("Reported By")

        # Form submit button
        submitted = st.form_submit_button("Add Incident")

    # After the form is submitted
    if submitted:
        if incident_date and description and severity and status and incident_type and reported_by:  # Check all required fields
            Incident(
                date=incident_date.strftime("%m/%d/%Y"), 
                severity=severity, 
                incident_type=incident_type, 
                status=status, 
                description=description,
                reported_by=reported_by
            ).insert_incident()
            st.success("New incident added.")
            st.rerun()
        else:
            st.error("You must fill in all the fields")

    # Update form
    incident_id = [str(inc["id"]) for _, inc in incidents.iterrows()]
    with st.form("update_status"):
        incident_id = st.selectbox("Select Incident ID to update", incident_id)
        new_status = st.selectbox("Status", ["open", "closed", "resolved", "investigating"])
        update_button = st.form_submit_button("Update")

    # When the form is submitted
    if update_button:
        if incident_id:
            Incident.update_incident_status(incident_id, new_status)
            st.rerun()
        else:
            st.error("You must select an Incident ID.")

    # Delete Incident
    selected_id = st.selectbox("Select incident you intend to delete", incident_id)

    col1, col2 = st.columns([2, 1])

    # Display a warning message
    with col1:
        st.warning(f"Delete incident {selected_id} permenantly?.")

    with col2:
        if st.button("Delete", type="primary"):
            Incident.delete_incident(selected_id)
            st.success("Incident deleted.")
            st.rerun()

with analytics_tab:
    total, open_count, critical, phishing_total = Incident.compute_incident_metrics(conn)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Incidents", total)

    with col2:
        st.metric("Open Incidents", open_count)

    with col3:
        st.metric("Critical Incidents", critical)


    st.subheader("Attack Types Overview")
    cyber_attacks =Incident.get_incidents_by_type_count(conn)
    st.bar_chart(
        cyber_attacks,
        x="incident_type",
        y="count",
    )

    st.subheader("Time Series Analysis of Phishing Attacks")
    df_trends = Incident.get_daily_phishing_count(conn)
    st.line_chart(df_trends, x="date", y="count")

with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input("Your OpenAI API key", type="password")

    client = OpenAI(api_key=api_key)

    st.title("🔍 AI Incident Analyzer")

    #Fetch incident from database
    incidents = Incident.get_all_incidents()

    if not incidents.empty:
        # Let user select an incident
        incident_options = [
            f"{inc['id']}: {inc['incident_type']} - {inc['severity']}"for _, row in incidents.iterrows() for inc in [row.to_dict()]
        ]
        
        selected_idx = st.selectbox(
            "Select incident to analyze:",
            range(len(incidents)),
            format_func=lambda i: incident_options[i]
        )
        
        incident = incidents.iloc[selected_idx] #.iloc to get row by index
        
        # Display incident details
        st.subheader("📋 Incident Details")
        st.write(f"**Type:** {incident['incident_type']}")
        st.write(f"**Severity:** {incident['severity']}")
        st.write(f"**Description:** {incident['description']}")
        st.write(f"**Status:** {incident['status']}")
    
    # Analyze with AI
    if st.button("🤖 Analyze with AI", type="primary"):
        with st.spinner("AI analyzing incident..."):
            
            # Create analysis prompt
            analysis_prompt = f"""Analyze this cybersecurity incident:

                                Type: {incident['incident_type']}
                                Severity: {incident['severity']}
                                Description: {incident['description']}
                                Status: {incident['status']}

                                Provide:
                                1. Root cause analysis
                                2. Immediate actions needed
                                3. Long-term prevention measures
                                4. Risk assessment"""
            # Call ChatGPT API
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )
            
            # Display AI analysis
            st.subheader("🧠 AI Analysis")
            st.write(response.choices[0].message.content)
            
