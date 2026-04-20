import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time

st.set_page_config(page_title="Quran Tracker", page_icon="📖")
st.title("📖 Quran Chapter Tracker")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Robust data loading with error handling
def get_all_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        # Force types to string to avoid the previous TypeError
        df['status'] = df['status'].astype(str)
        df['user'] = df['user'].astype(str)
        return df
    except Exception as e:
        st.error("The app is having trouble reaching Google Sheets. Please wait a moment and refresh.")
        st.stop()

df = get_all_data()

# 3. Centralized update function with a "cooldown" to prevent API errors
def safe_update(new_df):
    try:
        with st.spinner("Updating status..."):
            conn.update(worksheet="Sheet1", data=new_df)
            st.cache_data.clear()
            # A 1-second pause prevents Google from flagging rapid clicks as spam
            time.sleep(1) 
            st.rerun()
    except Exception as e:
        st.error("Google is busy! Please wait 10 seconds before trying again.")

# 4. Sidebar for User Selection
users = ["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"]
selected_user = st.sidebar.selectbox("Select your name:", users)

# 5. Track Progress
completed_chapters = df[df['status'] == 'Completed']
progress = len(completed_chapters)
st.sidebar.metric("Current progress", f"{progress} / 30")

# 6. Reset Logic (When all 30 are done)
if progress == 30:
    st.balloons()
    st.confetti() 
    if st.sidebar.button("🎉 Finish Khatam and start another one!"):
        # Reset all chapters to available
        df['status'] = 'Available'
        df['user'] = ''
        safe_update(df)

st.write("### Juz list")
st.info(f"Welcome **{selected_user}**. Please reserve a Juz or mark your progress below.")

# 7. Display Chapters
for index, row in df.iterrows():
    ch_num = row['chapter']
    status = str(row['status'])
    assigned_user = str(row['user'])
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 2])
        
        col1.write(f"**Juz {ch_num}**")
        
        # Check for different possible empty values
        if status in ["Available", "nan", "None", ""]:
            col2.caption("🟢 Available")
            if col3.button("Reserve", key=f"res_{ch_num}", use_container_width=True):
                df.at[index, 'status'] = 'Reserved'
                df.at[index, 'user'] = selected_user
                safe_update(df)
                
        elif status == "Reserved":
            if assigned_user == selected_user:
                col2.warning("🕒 Reading in progress")
                if col3.button("Mark as complete", key=f"done_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Completed'
                    safe_update(df)
            else:
                col2.error(f"👤 {assigned_user}")
                col3.write("🔒 Reserved")
                
        elif status == "Completed":
            col2.success(f"✅ {assigned_user}")
            col3.write("Finished")
        
        st.divider()