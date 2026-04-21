import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Quran Tracker", page_icon="📖")
# Custom CSS for a cleaner UI
st.markdown("""
    <style>
    /* Change the background of the whole app */
    .stApp {
        background: linear-gradient(to bottom, #f0f2f6, #ffffff);
    }
    
    /* Make the Sidebar look distinct */
    [data-testid="stSidebar"] {
        background-color: #1E3A8A;
        color: white;
        
        p {
            color: white;
        }
    }
    
    /* Style the metrics */
    [data-testid="stMetricValue"] {
        color: #1E3A8A;
        font-weight: bold;
    }

    /* Style every 'card' container */
    div[data-testid="stVerticalBlock"] > div:has(div.stColumn):first-of-type {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #ccc;
    }
            
    /* Style the Stats Table in the Sidebar */
section[data-testid="stSidebar"] .stTable {
    border-radius: 10px;
    overflow: hidden; /* Ensures corners stay rounded */
    border: 1px solid #e0e0e0;
    background-color: rgba(255,255,255,0.1)!important;
}

/* Header styling */
section[data-testid="stSidebar"] thead th {
    color: white !important;
    text-align: left !important;
    font-size: 0.8rem;
    text-transform: uppercase;
}

/* Row styling */
section[data-testid="stSidebar"] td {
    color: #333 !important;
    font-size: 0.9rem;
    padding: 10px !important;
    text-align: left !important;
}
    </style>
    """, unsafe_allow_html=True)

st.title("Team 37 Chapter Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# 1. Load data with Caching
def get_all_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=10)
        df['chapter'] = pd.to_numeric(df['chapter'], errors='coerce').fillna(0).astype(int)
        df['status'] = df['status'].astype(str)
        df['user'] = df['user'].astype(str)
        
        try:
            history_df = conn.read(worksheet="History", ttl=60)
        except:
            history_df = pd.DataFrame(columns=['date', 'user', 'chapter', 'khatam_number'])
            
        return df, history_df
    except Exception as e:
        if "429" in str(e):
            st.warning("⚠️ Google is busy. Retrying in 10 seconds...")
            time.sleep(10)
            st.rerun()
        else:
            st.error(f"Error reaching Google Sheets: {e}")
            st.stop()

df, history_df = get_all_data()

# 2. Sidebar Stats & Selection
users_list = ["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"]
users_list.sort()

options = ["-- Select your name --"] + users_list
selected_user = st.sidebar.selectbox("Identify yourself:", options)
user_is_identified = selected_user != "-- Select your name --"

st.sidebar.divider()
st.sidebar.subheader("📊 Stats")

if not history_df.empty:
    total_khatams = history_df['khatam_number'].max() if 'khatam_number' in history_df.columns else 0
    st.sidebar.write(f"**Total Khatams:** {int(total_khatams)}")
    st.sidebar.write("**Leaderboard:**")
    leaderboard = history_df['user'].value_counts().head(5)
    st.sidebar.table(leaderboard)
else:
    st.sidebar.write("No history recorded yet.")

completed_chapters = df[df['status'].str.contains('Completed', na=False)]
progress = len(completed_chapters)
st.sidebar.metric("Current progress", f"{progress} / 30")

# 3. Update Function
def safe_update(main_df, log_entry=None):
    try:
        with st.spinner("Updating status..."):
            conn.update(worksheet="Sheet1", data=main_df)
            if log_entry is not None:
                global history_df
                new_history = pd.concat([history_df, pd.DataFrame([log_entry])], ignore_index=True)
                conn.update(worksheet="History", data=new_history)
            st.cache_data.clear()
            time.sleep(1) 
            st.rerun()
    except Exception as e:
        st.error(f"Update failed: {e}")

# 4. Reset Logic
if progress == 30:
    st.balloons()
    if st.sidebar.button("Khatam finished Alhamdulillah. Start another one!"):
        if user_is_identified:
            df['status'] = 'Available'
            df['user'] = ''
            safe_update(df)
        else:
            st.sidebar.error("Please select your name first!")

#st.write("### Juz list")

if not user_is_identified:
    st.warning("⚠️ Please select your name in the sidebar to reserve or complete a Juz.")
else:
    st.info(f"Welcome **{selected_user}**. Page auto-refreshes every 2 mins.")

# 5. Display Chapters
# Find the FIRST available chapter number
try:
    available_chapters = df[df['status'].isin(["Available", "nan", "None", "", "nan"])]
    # Ensure it's treated as a number for the min() function
    next_up_chapter = pd.to_numeric(available_chapters['chapter']).min()
except:
    next_up_chapter = None

for index, row in df.iterrows():
    ch_num = int(row['chapter'])
    status = str(row['status']).strip()
    assigned_user = str(row['user']).strip()
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 2])
        col1.write(f"**Juz {ch_num}**")
        
        if status in ["Available", "nan", "None", "", "nan"]:
            if ch_num == next_up_chapter:
                # This part is NOT disabled - it stays bright/visible
                col2.info("✨ **Available**")
                
                # ONLY the button is disabled based on name selection
                if col3.button("Reserve", key=f"res_{ch_num}", use_container_width=True, disabled=not user_is_identified):
                    df.at[index, 'status'] = 'Reserved'
                    df.at[index, 'user'] = selected_user
                    safe_update(df)
            else:
                col2.caption("⚪ Unavailable")
                col3.write("")
                
        elif status == "Reserved":
            if assigned_user == selected_user:
                col2.warning("🕒 Reading")
                
                # Create two sub-columns for the "Complete" and "Cancel" buttons
                btn_col1, btn_col2 = col3.columns(2)
                
                if btn_col1.button("Complete", key=f"done_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Completed'
                    k_num = (history_df['khatam_number'].max() if not history_df.empty else 0)
                    log = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'user': selected_user,
                        'chapter': ch_num,
                        'khatam_number': k_num if progress < 29 else k_num + 1
                    }
                    safe_update(df, log)
                
                if btn_col2.button("Cancel", key=f"cancel_{ch_num}", use_container_width=True):
                    # Reset back to available and clear user
                    df.at[index, 'status'] = 'Available'
                    df.at[index, 'user'] = ''
                    safe_update(df)
                    
            else:
                col2.error(f"👤 {assigned_user}")
                col3.write("🔒 Reserved")
                
        elif status == "Completed":
            col2.success(f"✅ {assigned_user}")
            col3.write("Completed")
        
        #st.divider()

# --- FIXED AUTO REFRESH ---
# Use st.markdown with the correct parameter: unsafe_allow_html=True
st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)
