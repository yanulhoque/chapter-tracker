import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Quran Tracker", page_icon="📖")
st.title("📖 Quran Chapter Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Load the full table (30 chapters)
def get_all_data():
    return conn.read(worksheet="Sheet1", ttl=0)

df = get_all_data()

# 2. Sidebar for User Selection
users = ["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"]
selected_user = st.sidebar.selectbox("Identify yourself:", users)

# 3. Check for Book Completion
completed_count = len(df[df['status'] == 'Completed'])
st.sidebar.metric("Quran progress", f"{completed_count} / 30")

if completed_count == 30:
    if st.button("🎉 All chapters complete Alhamdulillah! Start another Khatam"):
        df['status'] = 'Available'
        df['user'] = ''
        conn.update(worksheet="Sheet1", data=df)
        st.cache_data.clear()
        st.rerun()

st.divider()

# 4. Display Chapters
for index, row in df.iterrows():
    ch_num = row['chapter']
    status = row['status']
    assigned_user = row['user']
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    col1.write(f"**Chapter {ch_num}**")
    
    if status == "Available":
        col2.info("Available")
        if col3.button(f"Reserve Ch {ch_num}", key=f"res_{ch_num}"):
            df.at[index, 'status'] = 'Reserved'
            df.at[index, 'user'] = selected_user
            conn.update(worksheet="Sheet1", data=df)
            st.cache_data.clear()
            st.rerun()
            
    elif status == "Reserved":
        if assigned_user == selected_user:
            col2.warning(f"Reserved by YOU")
            if col3.button(f"Mark Complete", key=f"done_{ch_num}"):
                df.at[index, 'status'] = 'Completed'
                conn.update(worksheet="Sheet1", data=df)
                st.cache_data.clear()
                st.rerun()
        else:
            col2.error(f"Taken by {assigned_user}")
            col3.write("🔒 Locked")
            
    elif status == "Completed":
        col2.success(f"Finished by {assigned_user}")
        col3.write("✅")