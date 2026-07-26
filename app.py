import streamlit as st

TARGET_URL = "https://team37.yanulhoque.workers.dev"

# 1. Hide default Streamlit elements so the page looks blank while redirecting
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# 2. Force the main browser window to change URLs
st.components.v1.html(
    f"""
    <script>
        window.top.location.href = "{TARGET_URL}";
    </script>
    """,
    height=0,
    width=0
)

st.subheader("Redirecting you to our new page...")
