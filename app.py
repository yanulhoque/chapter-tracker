import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
from datetime import datetime
import streamlit.components.v1 as components

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
        gap: 1rem !important; 
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
        padding: 10px !important; 
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
            
    /* Vertical Centering */
    [data-testid="stColumn"] > div {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%; 
    }

    /* Extra safety */
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

    /* Sidebar Button Styling */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: white !important;
        color: #1E3A8A !important;
        border: 1px solid white !important;
        font-weight: bold !important;
        margin-top: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f0f2f6 !important;
        color: #1E3A8A !important;
        border: 1px solid #f0f2f6 !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.3);
    }
  
    </style>
    """, unsafe_allow_html=True)


st.title("Team 37 Chapter Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONFETTI FUNCTION ---
def local_confetti():
    components.html(
        """
        <script>
            (function() {
                var parentDoc = window.parent.document;
                var scriptId = 'confetti-script';
                if (!parentDoc.getElementById(scriptId)) {
                    var script = parentDoc.createElement('script');
                    script.id = scriptId;
                    script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js';
                    parentDoc.head.appendChild(script);
                    script.onload = function() {
                        window.parent.confetti({particleCount: 150, spread: 70, origin: { y: 0.6 }, zIndex: 99999});
                    };
                } else {
                    window.parent.confetti({particleCount: 150, spread: 70, origin: { y: 0.6 }, zIndex: 99999});
                }
            })();
        </script>
        """,
        height=0,
    )

# 1. Load data with Caching
def get_all_data():
    try:
        df = conn.read(worksheet="Sheet1", ttl=10)
        if 'khatam_no' not in df.columns:
            df['khatam_no'] = 1
            
        df['chapter'] = pd.to_numeric(df['chapter'], errors='coerce').fillna(0).astype(int)
        df['khatam_no'] = pd.to_numeric(df['khatam_no'], errors='coerce').fillna(1).astype(int)
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

# --- 3. SIDEBAR STATS (WITH MEDALS) ---
if not history_df.empty:
    khatam_counts = history_df['khatam_number'].value_counts()
    full_khatams = (khatam_counts >= 30).sum()
    
    st.sidebar.write("### 🏆 Top Readers")
    
    # Generate Leaderboard
    leaderboard = history_df['user'].value_counts().reset_index()
    leaderboard.columns = ['Name', 'Juz Completed']
    
    # Add Medals to the top 3
    def assign_medal(index, name):
        if index == 0: return f"🥇 {name}"
        if index == 1: return f"🥈 {name}"
        if index == 2: return f"🥉 {name}"
        return name

    leaderboard['Name'] = [assign_medal(i, name) for i, name in enumerate(leaderboard['Name'])]
    
    leaderboard.index = leaderboard.index + 1
    st.sidebar.table(leaderboard)
    st.sidebar.write(f"**Total Khatams Completed:** {int(full_khatams)}")
else:
    st.sidebar.write("No history recorded yet.")

# Latest Khatam Progress
latest_k_no = df['khatam_no'].max()
completed_in_latest = len(df[(df['khatam_no'] == latest_k_no) & (df['status'] == 'Completed')])
st.sidebar.write(f"**Latest Khatam Progress:** {completed_in_latest} / 30")

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

# --- 5. START NEW KHATAM BUTTON ---
available_anywhere = df[df['status'].isin(["Available", "nan", "None", "", "nan"])]

if available_anywhere.empty:
    st.sidebar.success("🎉 All Juz have been claimed!")
    
    if st.sidebar.button("Start Additional Khatam", use_container_width=True):
        if user_is_identified:
            next_k_no = int(df['khatam_no'].max() + 1)
            new_rows = pd.DataFrame({
                'chapter': list(range(1, 31)),
                'status': ['Available'] * 30,
                'user': [''] * 30,
                'khatam_no': [next_k_no] * 30
            })
            updated_df = pd.concat([df, new_rows], ignore_index=True)
            safe_update(updated_df)
        else:
            st.sidebar.error("Select your name first!")

# --- 6. DISPLAY CHAPTERS (HYBRID VIEW) ---
# Logic: Find the absolute next Juz to read across all batches
available_rows = df[df['status'].isin(["Available", "nan", "None", "", "nan"])]
next_up_idx = available_rows.index.min() if not available_rows.empty else None

for k_num in sorted(df['khatam_no'].unique()):
    khatam_subset = df[df['khatam_no'] == k_num]
    
    # FILTER LOGIC:
    # If this is an OLD khatam, only show the Juz that are not 'Completed'
    # If this is the LATEST khatam, show everything.
    if k_num < latest_k_no:
        display_subset = khatam_subset[khatam_subset['status'] != 'Completed']
    else:
        display_subset = khatam_subset

    # Only show the section header if there are Juz to display
    if not display_subset.empty:
        st.write(f"### Khatam #{k_num}")

        for index, row in display_subset.iterrows():
            ch_num = int(row['chapter'])
            status = str(row['status']).strip()
            assigned_user = str(row['user']).strip()
            
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 2])
                col1.markdown(f"<a href='https://quran.com/juz/{ch_num}' target='_blank'><h3>Juz {ch_num} 🔗</h3></a>", unsafe_allow_html=True)
                
                if status in ["Available", "nan", "None", "", "nan"]:
                    if index == next_up_idx:
                        col2.info("✨ Available")
                        if col3.button("Reserve", key=f"res_{index}", use_container_width=True, disabled=not user_is_identified):
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
                        if btn_col1.button("Completed", key=f"done_{index}", use_container_width=True):
                            local_confetti()
                            df.at[index, 'status'] = 'Completed'
                            log = {
                                'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                                'user': selected_user,
                                'chapter': ch_num,
                                'khatam_number': k_num 
                            }
                            safe_update(df, log)
                        
                        if btn_col2.button("Unreserve", key=f"cancel_{index}", use_container_width=True):
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
