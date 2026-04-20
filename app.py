import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Quran Tracker", page_icon="📖")
st.title("📖 Quran Chapter Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Load data and force string types to avoid the TypeError
def get_all_data():
    df = conn.read(worksheet="Sheet1", ttl=0)
    # Ensure status and user columns are treated as strings
    df['status'] = df['status'].astype(str)
    df['user'] = df['user'].astype(str)
    return df

df = get_all_data()

# 2. Sidebar for User Selection
users = ["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"]
selected_user = st.sidebar.selectbox("Select your name:", users)

# 3. Track Progress
completed_chapters = df[df['status'] == 'Completed']
progress = len(completed_chapters)
st.sidebar.metric("Current progress", f"{progress} / 30")

# 4. Reset Logic (When all 30 are done)
if progress == 30:
    st.confetti() # Just for fun!
    if st.sidebar.button("🎉 Finish Khatam and start another one!"):
        # Reset all chapters to available
        df['status'] = 'Available'
        df['user'] = ''
        conn.update(worksheet="Sheet1", data=df)
        st.cache_data.clear()
        st.rerun()

st.write("### Juz list")
st.info("Select your name from the sidebar, then reserve a chapter below.")

# 5. Display Chapters
for index, row in df.iterrows():
    ch_num = row['chapter']
    status = str(row['status'])
    assigned_user = str(row['user'])
    
    # Create a nice container for each chapter
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 2])
        
        col1.write(f"**Juz {ch_num}**")
        
        if status == "Available" or status == "nan" or assigned_user == "":
            col2.caption("🟢 Available")
            if col3.button("Reserve", key=f"res_{ch_num}", use_container_width=True):
                df.at[index, 'status'] = 'Reserved'
                df.at[index, 'user'] = selected_user
                conn.update(worksheet="Sheet1", data=df)
                st.cache_data.clear()
                st.rerun()
                
        elif status == "Reserved":
            if assigned_user == selected_user:
                col2.warning("🕒 Reading in progress")
                if col3.button("Mark as complete", key=f"done_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Completed'
                    conn.update(worksheet="Sheet1", data=df)
                    st.cache_data.clear()
                    st.rerun()
            else:
                col2.error(f"👤 {assigned_user}")
                col3.write("🔒 Reserved")
                
        elif status == "Completed":
            col2.success(f"✅ {assigned_user}")
            col3.write("Finished")
        
        st.divider()