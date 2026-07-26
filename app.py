import streamlit as st

TARGET_URL = "https://team37.yanulhoque.workers.dev/"

# Set a clean page title
st.set_page_config(page_title="Page Moved", page_icon="🔗")

# Display the moved message and the clickable link
st.warning("### This page has moved.")
st.markdown(f"Please click the link below to visit the new site:")
st.markdown(f"### ➡️ [{TARGET_URL}]({TARGET_URL})")

# Hide standard Streamlit header and footer menus for a cleaner look
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, 
    unsafe_allow_html=True
)
