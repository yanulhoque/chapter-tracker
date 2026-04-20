import streamlit as st
from itertools import count
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.title("📖 Group Chapter Tracker")

# 1. Connect to Google Sheets
# Note: In production, you'll put your sheet URL in Streamlit Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Function to get current status from the sheet
def get_data():
    df = conn.read(worksheet="Sheet1", usecols=[0, 1])
    # Convert the sheet key-value pairs into a dictionary
    return dict(zip(df['key'], df['value']))

# 3. Function to update the sheet
def update_data(new_chapter, new_total):
    updated_df = pd.DataFrame({
        "key": ["current_chapter", "total_reads"],
        "value": [new_chapter, new_total]
    })
    conn.update(worksheet="Sheet1", data=updated_df)
    st.cache_data.clear() # Refresh the app's cache

# Load current state
data = get_data()
current_ch = int(data['current_chapter'])
total_reads = int(data['total_reads'])

# UI Logic
users = ["Alice", "Bob", "Charlie", "Diana"] # Add your names here
selected_user = st.selectbox("Who is reading this chapter?", users)

col1, col2 = st.columns(2)
col1.metric("Current Chapter", f"{current_ch} / 30")
col2.metric("Total Book Completions", total_reads)

if st.button(f"Confirm: {selected_user} finished Chapter {current_ch}"):
    if current_ch < 30:
        new_ch = current_ch + 1
        new_total = total_reads
    else:
        new_ch = 1
        new_total = total_reads + 1
        st.balloons()
        st.success("The book has been finished! Restarting...")

    update_data(new_ch, new_total)
    st.rerun()