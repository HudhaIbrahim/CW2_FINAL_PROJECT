import streamlit as st
from app.data.db import connect_database
from openai import OpenAI
from app.data.it_operations import Tickets
import datetime

st.set_page_config(
    page_title="IT Tickets Dashboard",
    page_icon="🖥️",
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
st.title("🖥️ IT Operations Dashboard")
st.success(f"Hello, **{st.session_state.username}**!")

tickets_tab, analytics_tab, AI_tab = st.tabs(["Tickets", "Analytics", "AI Assistant"])

with tickets_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Display tickets in a table
    tickets = Tickets.get_all_tickets(conn)
    st.dataframe(tickets, use_container_width=True)

    # Add new ticket form
    with st.form("new_ticket"):
        ticket_id = st.text_input("Ticket ID")
        status = st.selectbox("Status", ["open", "in_progress", "resolved", "closed"])
        category = st.selectbox("Category", ["hardware", "software", "network", "other","access"])
        subject = st.text_input("Subject")
        description = st.text_area("Description")
        created_date = st.date_input(
            "Ticket Date",
            value=datetime.date.today(),  # Default to today
            max_value=datetime.date.today()  # Can't select future dates
        )
        resolved_date = st.date_input(
            "Resolved Date",
            value=datetime.date.today(),  # Default to today
            max_value=datetime.date.today()  # Can't select future dates
        )
        assigned_to = st.text_input("Assigned To")
        # Form submit button
        submitted = st.form_submit_button("Add Ticket")

    # After the form is submitted
    if submitted:
        if ticket_id and subject:  # Check required fields
            # Clean and format the ticket ID
            # Convert to uppercase
            ticket_id_upper = ticket_id.upper().strip()

            # Remove any existing "TCK-" prefix to avoid duplication
            if ticket_id_upper.startswith("TCK-"):
                ticket_id_upper = ticket_id_upper.removeprefix("TCK-")
            
            # Add the correct prefix
            formatted_ticket_id = f"TCK-{ticket_id_upper}"
            
            # Insert with formatted ticket ID
            Tickets(
                ticket_id=formatted_ticket_id,  
                status=status,
                category=category,
                subject=subject,
                description=description,
                created_date=created_date.strftime("%m/%d/%Y"),
                resolved_date=resolved_date.strftime("%m/%d/%Y"),
                assigned_to=assigned_to,
            ).insert_ticket()
            st.success(f"Ticket {formatted_ticket_id} added successfully!")
            st.rerun()
        else:
            st.error("You must fill in Ticket ID and Subject.")




    # Update form
    ticket_ids = [str(inc["ticket_id"]) for _, inc in tickets.iterrows()]
    with st.form("update_ticket"):
        ticket_id = st.selectbox("Ticket ID", ticket_ids)
        new_status = st.selectbox("Status", ["open", "in_progress", "resolved", "closed"])
        update_button = st.form_submit_button("Update")

    if update_button:
        if ticket_id and new_status:
            Tickets.update_ticket_status(conn, ticket_id, new_status)
            st.rerun()
        else:
            st.error("You must fill in all the fields.")

    # Delete Ticket
    selected_id = st.selectbox("Select incident to delete", ticket_ids)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.warning(f"Delete Ticket {selected_id}? This cannot be undone.")

    with col2:
        if st.button("Delete", type="primary"):
            Tickets.delete_ticket(conn, selected_id)  # Delete ticket
            st.success("Incident deleted.")
            st.rerun()

with analytics_tab:
    conn = connect_database()
    # Performance chart
    total, open_tickets, unresolved = Tickets.get_ticket_kpis(conn)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tickets", total)
    with col2:
        st.metric("Open Tickets", open_tickets, delta=f"{open_tickets} pending")
    with col3:
        st.metric("Unresolved Tickets", unresolved)

    st.divider()
    st.subheader("Staff Resolution Performance")
    st.markdown("##### Identify top performers and areas for improvement.")
    staff_performance = Tickets.get_tickets_resolved_by_staff(conn)
    st.dataframe(staff_performance, use_container_width=True)
    st.bar_chart(
        staff_performance,
        x="assigned_to",
        y="resolved_tickets",
        height=400
    )

with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input("Your OpenAI API key", type="password")
    # Get user input
    prompt = st.chat_input("Enter your message here...")

    if api_key:
        # Create OpenAI client from the key STRING
        client = OpenAI(api_key=api_key)

        # Page title
        st.title("🤖 IT Operations Assistant")
        st.caption("Powered by GPT-4.1-mini")

        # Initialize session state for messages
        TICKET_KEY = "tickets_key"

        #	Initialize	session	state	for	messages
        if TICKET_KEY not in st.session_state:
            st.session_state[TICKET_KEY]= [
                {
                    "role": "system",
                    "content": """You are an IT operations expert. 
                    Help with IT ticket management, ticket resolution stratergies, and best practices. 
                    Explain concepts clearly and suggest appropriate techniques.
                    Tone: Professional, technical
                    Format: Clear, structured responses"""
                }
            ]
        messages = st.session_state[TICKET_KEY]

        # Sidebar with controls
        with st.sidebar:
            st.subheader("Chat controls")

            #	Display	message	count
            message_count = len([m for m in messages if m["role"] != "system"])
            st.metric("Messages", message_count)

            # Clear chat button
            if st.button("🗑 Clear	Chat", use_container_width=True):
                st.session_state[TICKET_KEY] = []
                st.rerun()


        # Display all previous messages
        for message in messages:
            if message["role"] != "system":  # Don't display system prompt
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt:
            #	Display	user	message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Add user message to session state
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Call OpenAI API (with streaming)
            with st.spinner("Thinking..."):
                completion = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    stream=True  # Enable streaming (response appears word by word)
                    # Returns a generator instead of complete response
                )

            # Display streaming response
            with st.chat_message("assistant"):
                container = st.empty()  # Create empty container(placeholder) to update
                full_reply = ""  # string to accumulate the full response

                # Process each chunk as it arrives
                for chunk in completion:  # Loop through each chunk of response
                    delta = chunk.choices[0].delta  # Get the new content
                    if delta.content:  # Check if chunk has content
                        full_reply += delta.content  # Add to full response (connects the new text in each chunk)
                        container.markdown(full_reply + "▌")  # Update display with current text

                    # Remove cursor and show final response
                    container.markdown(full_reply)

            # save complete response to session state
            messages.append({
                "role": "assistant",
                "content": full_reply
            })

    else:
        st.info("Enter your OpenAI API key to start chatting.")