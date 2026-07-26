import streamlit as st

TARGET_URL = "https://team37.yanulhoque.workers.dev/"

# Injects JavaScript to immediately change the browser's location
st.markdown(
    f'<meta http-equiv="refresh" content="0;URL=\'{TARGET_URL}\' />', 
    unsafe_allow_html=True
)
st.write("Redirecting you now...")
