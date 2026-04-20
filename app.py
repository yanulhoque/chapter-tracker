import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Quran Tracker", page_icon="📖")
st.title("Team 37 Chapter Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Load data
def get_all_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        # Force chapter to int to remove decimals, then to string for display
        df['chapter'] = pd.to_numeric(df['chapter']).astype(int)
        df['status'] = df['status'].astype(str)
        df['user'] = df['user'].astype(str)
        
        # Load History for Stats
        try:
            history_df = conn.read(worksheet="History", ttl=0)
        except:
            history_df = pd.DataFrame(columns=['date', 'user', 'chapter', 'khatam_number'])
            
        return df, history_df
    except Exception as e:
        st.error(f"Error reaching Google Sheets: {e}")
        st.stop()

df, history_df = get_all_data()

# 2. Sidebar Stats & Selection
users = ["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"]
selected_user = st.sidebar.selectbox("Select your name:", users)

st.sidebar.divider()
st.sidebar.subheader("📊 Stats")

# Calculate Stats
if not history_df.empty:
    total_khatams = history_df['khatam_number'].max() if 'khatam_number' in history_df.columns else 0
    st.sidebar.write(f"**Total Khatams:** {int(total_khatams)}")
    
    # User Leaderboard (Most chapters read overall)
    st.sidebar.write("**Leaderboard (Top Readers):**")
    leaderboard = history_df['user'].value_counts().head(5)
    st.sidebar.table(leaderboard)
else:
    st.sidebar.write("No history recorded yet.")

# 3. Track Current Progress
completed_chapters = df[df['status'].str.contains('Completed', na=False)]
progress = len(completed_chapters)
st.sidebar.metric("Current Khatam Progress", f"{progress} / 30")

# 4. Centralized update function
def safe_update(main_df, log_entry=None):
    try:
        with st.spinner("Updating status..."):
            conn.update(worksheet="Sheet1", data=main_df)
            if log_entry is not None:
                # Append to History sheet
                global history_df
                new_history = pd.concat([history_df, pd.DataFrame([log_entry])], ignore_index=True)
                conn.update(worksheet="History", data=new_history)
            
            st.cache_data.clear()
            time.sleep(1) 
            st.rerun()
    except Exception as e:
        st.error(f"Update failed: {e}")

# 5. Reset Logic
if progress == 30:
    st.balloons()
    if st.sidebar.button("Khatam finished Alhamdulillah. Start another one!"):
        df['status'] = 'Available'
        df['user'] = ''
        safe_update(df)

st.write("### Juz list")
st.info(f"Welcome **{selected_user}**. Please reserve a Juz or mark your progress below.")

# 6. Display Chapters
for index, row in df.iterrows():
    ch_num = int(row['chapter']) # Ensure it's an integer for display
    status = str(row['status']).strip()
    assigned_user = str(row['user']).strip()
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 2])
        col1.write(f"**Juz {ch_num}**")
        
        if status in ["Available", "nan", "None", ""]:
            col2.caption("🟢 Available")
            if col3.button("Reserve", key=f"res_{ch_num}", use_container_width=True):
                df.at[index, 'status'] = 'Reserved'
                df.at[index, 'user'] = selected_user
                safe_update(df)
                
        elif status == "Reserved":
            if assigned_user == selected_user:
                col2.warning("🕒 Reading")
                if col3.button("Complete", key=f"done_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Completed'
                    
                    # Prepare history log entry
                    k_num = (history_df['khatam_number'].max() if not history_df.empty else 0)
                    if progress == 29: k_num += 1 # If this is the last one, it's a new Khatam
                    
                    log = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'user': selected_user,
                        'chapter': ch_num,
                        'khatam_number': k_num if progress < 30 else k_num + 1
                    }
                    safe_update(df, log)
            else:
                col2.error(f"👤 {assigned_user}")
                col3.write("🔒 Reserved")
                
        elif status == "Completed":
            col2.success(f"✅ {assigned_user}")
            col3.write("Finished")
        
        st.divider()