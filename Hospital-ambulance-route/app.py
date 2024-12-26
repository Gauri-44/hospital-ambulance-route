import streamlit as st

# Set up the configuration for the Streamlit app
st.set_page_config(
    page_title="Hospital and Ambulance Locator",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Title of the main page
st.title("Hospital and Ambulance Locator")

# Sidebar for navigation
st.sidebar.title("Navigation")
st.sidebar.success("Select a page above.")

# Content for the main page
st.write("""
Welcome to the Hospital and Ambulance Locator app! Use the sidebar to navigate through different functionalities of the app.

- **🚑 Ambulance Locator**: Find real-time locations of ambulances and hospitals.
- **📈 Graph Algorithms**: Explore graph algorithms and their applications.
- **📊 EDA**: Perform exploratory data analysis on hospital and ambulance data.
""")
