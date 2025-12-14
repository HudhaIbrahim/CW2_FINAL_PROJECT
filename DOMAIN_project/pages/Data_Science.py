import streamlit as st
from app.data.dataset import Dataset
from app.data.db import connect_database
from openai import OpenAI
import plotly.express as px
import datetime


st.set_page_config(
    page_title="Data Science Dashboard",
    page_icon="📈",
    layout="wide"
)
# Guard: check if logged in
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
st.title("📈 Data Science Dashboard")
st.success(f"Hello, **{st.session_state.username}**!")

dataset_tab, analytics_tab, AI_tab = st.tabs(["Datasets", "Analytics", "AI Assistant"])

with dataset_tab:
    conn = connect_database('DATA/intelligence_platform.db')

    # Display datasets in a table
    datasets = Dataset.get_all_datasets(conn)
    st.dataframe(datasets, use_container_width=True)

    #Add new dataset with a form
    with st.form("new_dataset"):
        # Form inputs (Streamlit widgets)
        dataset_name = st.text_input("Dataset Name")
        category = st.selectbox("Category", ["security", "operations", "marketing", "finance", "hr", "sales"])
        source = st.selectbox("Source", ["internal", "external", "public", "partner"])
        last_updated = st.date_input(
                        "Last Updated",
            value=datetime.date.today(),  # Default to today
            max_value=datetime.date.today()  # Can't select future dates
        )
        record_count = st.number_input("Record Count", min_value=0, step=1)
        file_size_mb = st.number_input("File Size (MB)", min_value=0.0, step=0.1)
        # Form submit button
        submitted = st.form_submit_button("Add Dataset")

    # After form is submitted
    if submitted:
        if dataset_name and category and source and last_updated and record_count >= 0 and file_size_mb >= 0:
            # Format dataset name
            formatted_name = dataset_name.lower()  # Convert to lowercase
            
            # Remove any existing "dataset_" prefix to avoid duplication
            if formatted_name.startswith("dataset_"):
                formatted_name = formatted_name.removeprefix("dataset_")
            
            # Add the correct prefix
            formatted_name = f"dataset_{formatted_name}"
            
            new_dataset = Dataset(
                dataset_name=formatted_name,  # Use the formatted name
                category=category,
                source=source,
                last_updated=last_updated.strftime("%m/%d/%Y"),
                record_count=record_count,
                file_size_mb=file_size_mb
            )

            new_id = new_dataset.insert_dataset()
            st.success(f"Successfully added dataset with ID {new_id}")
            st.rerun()  # Refresh the page to show the new dataset
        else:
            st.error("You must fill in all the fields")

    # Update form
    dataset_ids = [str(inc["id"]) for _, inc in datasets.iterrows()]
    with st.form("Update rows and columns"):
        selected_id = st.selectbox("Select dataset to update", dataset_ids)
        last_updated_date = st.date_input(
            "New Last Updated Date",
            value=datetime.date.today(),  # Default to today
            max_value=datetime.date.today()  # Can't select future dates
        )
        update_button = st.form_submit_button("Update")

    if update_button:
        if dataset_ids and last_updated_date:
            Dataset.update_last_updated_date(
                conn,
                int(selected_id),
                last_updated_date.strftime("%m/%d/%Y")
            )
            st.rerun()
        else:
            st.error("You must fill in all fields.")

    # Delete form
    selected_id = st.selectbox("Select dataset to delete", dataset_ids)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.warning(f"Delete Dataset {selected_id}? This cannot be undone.")

    with col2:
        if st.button("Delete", type="primary"):
            Dataset.delete_dataset(conn, selected_id)  # your DB function
            st.success("Dataset deleted.")
            st.rerun()

with analytics_tab:    
    conn = connect_database()
    
    # Graph 1: Resource Consumption by Category 
    st.subheader("Resource Consumption by Category")
    st.write("Shows which departments consume the most storage resources.")
    
    df_resource = Dataset.get_resource_consumption_by_category(conn)
    
    # Create pie chart using Plotly
    fig1 = px.pie(df_resource, 
                  values='total_size_mb', 
                  names='category',
                  title='Storage Distribution by Category')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Show data table
    st.dataframe(df_resource, use_container_width=True)

    
    # Graph 2: Data Source Dependency
    st.subheader("Data Source Dependency")
    st.write("Understanding data source dependency to manage external vendor risks.")
    
    df_source = Dataset.get_datasets_by_source_count(conn)
    
    # Create bar chart for dataset count by source
    st.bar_chart(df_source.set_index('source')['count'])
    st.caption("Number of Datasets by Source")
    
    # Show the data table below the chart
    st.dataframe(df_source, use_container_width=True)
    
    conn.close()


with AI_tab:
    #	Initialize	OpenAI	client
    api_key = st.text_input("Your OpenAI API key", type="password")
    # Get user input
    prompt = st.chat_input("Enter your message here...")

    if api_key:
        # Create OpenAI client from the key STRING
        client = OpenAI(api_key=api_key)

        # Page title
        st.title("🤖 Datascience AI Assistant")
        st.caption("Powered by GPT-4.1-mini")

        # Initialize session state for messages
        DATASET_KEY = "dataset_key"

        #	Initialize	session	state	for	messages
        if DATASET_KEY not in st.session_state:
            st.session_state[DATASET_KEY]= [
                {
                    "role": "system",
                    "content": """You are a data science expert. 
                    Help with data analysis, visualization, statistical methods, and machine learning. 
                    Explain concepts clearly and suggest appropriate techniques.
                    Tone: Professional, technical
                    Format: Clear, structured responses"""
                }
            ]
        messages = st.session_state[DATASET_KEY]

        # Sidebar with controls
        with st.sidebar:
            st.subheader("Chat controls")

            #	Display	message	count
            message_count = len([m for m in messages if m["role"] != "system"])
            st.metric("Messages", message_count)

            # Clear chat button
            if st.button("🗑 Clear	Chat", use_container_width=True):
                st.session_state[DATASET_KEY] = []
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