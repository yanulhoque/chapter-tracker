import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Team 37 Chapter Tracker", page_icon="📖")

# --- CONSOLIDATED CUSTOM CSS ---
st.markdown("""
    <style>
        
    /* Main background */
    .stApp {
        background: linear-gradient(to bottom, #f0f2f6, #ffffff);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1E3A8A;
        color: white;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Stats Table in Sidebar */
    section[data-testid="stSidebar"] .stTable {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.2);
        background-color: rgba(255,255,255,0.1) !important;
    }
    section[data-testid="stSidebar"] thead th {
        color: white !important;
        text-align: left !important;
    }
    section[data-testid="stSidebar"] td {
        color: white !important;
        background-color: transparent !important;
        text-align: left !important;
    }

    /* CENTER EVERYTHING in the main Juz list */
    [data-testid="stVerticalBlockBorderWrapper"] {
        text-align: center !important;
    }
    .stButton {
        display: flex;
        justify-content: center;
    }
    
    /* Main Selectbox Centering */
    [data-testid="stSelectbox"] {
        
        margin: 0 auto;
    }

    /* Card Styling */
    div[data-testid="stVerticalBlock"] > div:has(div.stColumn) {
        background-color: white;
        border-radius: 5px;
        padding: 5px 10px 0 10px;
        /*box-shadow: 0 2px 4px rgba(0,0,0,0.05);*/
        margin-bottom: 0;
    }

    /* Metric Styling */
    [data-testid="stMetricValue"] {
        color: #1E3A8A;
        font-weight: bold;
    }
            
/* Hide the anchor link next to headings */
.st-emotion-cache-gi0tri {
    display: none !important;
}
    /* 1. Adjust the vertical gap between elements inside the same column */
    [data-testid="stVerticalBlock"] {
        gap: 1rem !important; /* Change this value to adjust spacing */
    }

    /* 2. Remove extra padding from the top of the columns */
    [data-testid="stVerticalBlock"] > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }

    /* 3. Adjust spacing specifically for the Alert (User name box) */
    .stAlert {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding: 10px !important; /* Makes the user name box more compact */
    }

    /* 4. Center the text within the Alert box to match the Juz number */
    [data-testid="stAlertContainer"] {
        padding: 10px 10px !important;
        min-height: auto !important;
    }
            
    /* 5. Center the Juz Header (h3) specifically */
    h3 {
        font-size: 1.5rem!important;
        display:flex;
        justify-content: center;
    }
            
        /* Vertical Centering: This aligns content to the middle of the card's height */
    [data-testid="stColumn"] > div {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%; /* Ensures the column takes up the full height of the card */
    }

    /* Extra safety: Ensure the vertical block inside also centers its children */
    [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
        justify-content: center !important;
        height: 100% !important;
    }    
            
    .stHorizontalBlock .stColumn:nth-child(3) p {
        text-align: center;
    }
     @media (max-width: 600px) {
        .stHorizontalBlock .stColumn:nth-child(3) p {
            padding-bottom:10px;
        }
    }     

    a {
        color: rgb(49, 51, 63) !important;
        text-decoration: none !important;
    }
    a:hover h3 {
        text-decoration:underline !important;
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

# --- 2. MAIN WINDOW USER SELECTION ---
users_list = sorted(["Ghazi", "Fatima", "Fatiha", "Rahima", "Shahi", "Kalshuma", "Farhad", "Shamil", "Amina", "Sayeed", "Raju", "Ujjal", "Yanul", "Kamrul", "Mitha", "Habiba", "Shumi", "Shahana", "Gumana", "Waseem", "Yaasir", "Zafir", "Zuhair", "Zahra", "Maryam", "Dawood", "Yusuf", "Aqeel", "Umair", "Adam"])

options = ["-- Select your name --"] + users_list
selected_user = st.selectbox(" ", options)
user_is_identified = selected_user != "-- Select your name --"

if not user_is_identified:
    st.warning("☝️ Please select your name above to reserve or complete a Juz.")
else:
    st.info(f"Assalamu Alaikum, **{selected_user}**! Page auto-refreshes every 2 mins.")

# --- 3. SIDEBAR STATS ---
if not history_df.empty:
    total_khatams = history_df['khatam_number'].max() if 'khatam_number' in history_df.columns else 0
    st.sidebar.write("### 🏆 Top Readers")
    leaderboard = history_df['user'].value_counts().reset_index()
    leaderboard.columns = ['Name', 'Juz Completed']
    leaderboard.index = leaderboard.index + 1
    st.sidebar.table(leaderboard)
    st.sidebar.write(f"**Total Khatams Completed:** {int(total_khatams)}")
else:
    st.sidebar.write("No history recorded yet.")

completed_chapters = df[df['status'].str.contains('Completed', na=False)]
progress = len(completed_chapters)
st.sidebar.write(f"**Current Khatam:** {progress} / 30 Juz")

# 4. Update Function
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

# 5. Reset Logic
if progress == 30:
    st.balloons()
    if st.sidebar.button("🎉 Start New Khatam"):
        if user_is_identified:
            df['status'] = 'Available'
            df['user'] = ''
            safe_update(df)
        else:
            st.sidebar.error("Select your name first!")

# 6. Display Chapters
try:
    available_chapters = df[df['status'].isin(["Available", "nan", "None", "", "nan"])]
    next_up_chapter = pd.to_numeric(available_chapters['chapter']).min()
except:
    next_up_chapter = None

for index, row in df.iterrows():
    ch_num = int(row['chapter'])
    status = str(row['status']).strip()
    assigned_user = str(row['user']).strip()
    
    with st.container():
        # Using equal ratios helps with centering on desktop
        col1, col2, col3 = st.columns([1, 2, 2])
        
        # Col 1: Chapter Number Link
        col1.markdown(f"<a href='https://quran.com/{ch_num}' target='_blank'><h3>Juz {ch_num} 🔗</h3></a>", unsafe_allow_html=True)
        
        # Col 2: Status Box
        if status in ["Available", "nan", "None", "", "nan"]:
            if ch_num == next_up_chapter:
                col2.info("✨ Available")
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
                btn_col1, btn_col2 = col3.columns(2)
                
                if btn_col1.button("Completed", key=f"done_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Completed'
                    k_num = (history_df['khatam_number'].max() if not history_df.empty else 0)
                    log = {
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'user': selected_user,
                        'chapter': ch_num,
                        'khatam_number': k_num if progress < 29 else k_num + 1
                    }
                    safe_update(df, log)
                
                if btn_col2.button("Unreserve", key=f"cancel_{ch_num}", use_container_width=True):
                    df.at[index, 'status'] = 'Available'
                    df.at[index, 'user'] = ''
                    safe_update(df)
            else:
                col2.error(f"👤 {assigned_user}")
                col3.write("🔒 Reserved")
                
        elif status == "Completed":
            col2.success(f"✅ {assigned_user}")
            col3.write("Completed")

# Auto Refresh
st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)
