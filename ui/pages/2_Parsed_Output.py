import streamlit as st
import os
from PIL import Image
from navigation import make_navbar

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "animations", "M-PARSER.png")

try:
    img = Image.open(logo_path)
except Exception:
    # Fallback to a string emoji if the path is wrong so the app doesn't crash
    img = "📂"

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Parsed Output | M-PARSER",
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded"
)

make_navbar()

# --- CSS ---
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #2F069C 0%, #C5B1FC 100%);
    }

    .section-header {
        color: #e5e4e2;
        font-size: 32px;
        font-weight: 700;
        margin: 20px 0px 10px 0px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    div.stButton button[kind="primary"] {
        background: linear-gradient(135deg, #a74ac7 0%, #3B82F6 100%);
        color: white;
        border: none;
        padding: 22px 60px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 20px;
        transition: all 0.3s ease;
    }

    div.stButton button[kind="secondary"] {
        background: #342d7e;
        color: #ffffff;
        padding: 22px 60px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 20px;
        border: none;
    }

    div.stButton > button:first-child:hover {
        box-shadow: 0 10px 20px rgba(30, 58, 138, 0.2);
        transform: translateY(-2px);
    }

    div[data-testid="stDownloadButton"] button {
        background-color: #28a745;
        color: white;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background-color: #28a745 !important;  /* force same color */
        color: white !important;
        opacity: 1 !important;  
        box-shadow: 0 10px 20px rgba(40, 167, 69, 0.3);
        transform: translateY(-2px);
    }

    /* TAB CONTAINER */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }

    /* INACTIVE TAB */
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
        border-radius: 12px;
        padding: 10px 18px;
        font-weight: 600;
    }

    /* ACTIVE TAB */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3ea055 0%, #b2c248 100%);
        color: white;
        border-radius: 12px;
    }

    /* TAB HOVER */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.25);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #b2c248 !important;  /* your desired color */
        height: 3px;  /* thickness of the line */
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
OUTPUT_DIR = os.path.join(project_root, "app", "final_json_output")

# --- SESSION CHECK ---
if 'selected_file' not in st.session_state:
    st.markdown('<div class="section-header"><i class="fa-solid fa-circle-xmark"></i> No Selection</div>', unsafe_allow_html=True)
    
    # Custom Warning Box
    st.markdown("""
        <div style="
            background-color: rgba(255, 193, 7, 0.1);
            color: #ffca28;
            padding: 1rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 193, 7, 0.3);
            margin-bottom: 20px;
            font-size: 19px;
            font-weight: 400;
            display: flex;
            align-items: center;
            gap: 10px;
        ">
            <i class="fa-solid fa-triangle-exclamation"></i> 
            No file has been selected for analysis. Please return to the upload page.
        </div>
    """, unsafe_allow_html=True)

    if st.button("Return",type="secondary"):
        st.switch_page("pages/1_Upload_and_Process.py")
    st.stop()

selected_name = st.session_state['selected_file']
base_name = os.path.splitext(selected_name)[0]

current_latency = "N/A"
if 'files' in st.session_state:
    for f in st.session_state.files:
        if f['name'] == selected_name:
            current_latency = f.get('latency', 'N/A')
            break
            
# --- LOAD DATA ---
json_content, braille_content = None, None

if os.path.exists(OUTPUT_DIR):
    files = os.listdir(OUTPUT_DIR)

    json_file = next((f for f in files if f.startswith(base_name) and f.endswith(".json")), None)
    braille_file = next((f for f in files if f.startswith(base_name) and f.endswith(".txt")), None)

    if json_file:
        with open(os.path.join(OUTPUT_DIR, json_file), "r", encoding="utf-8") as f:
            json_content = f.read()

    if braille_file:
        with open(os.path.join(OUTPUT_DIR, braille_file), "r", encoding="utf-8") as f:
            braille_content = f.read()

# --- HEADER ---
st.markdown('<div class="section-header"><i class="fa-solid fa-square-poll-vertical"></i> Analysis Results</div>', unsafe_allow_html=True)

# --- FILE INFO ---
c1, c2 = st.columns([4, 1])

with c1:
    st.markdown(
        f"<h3 style='color:#e5e4e2;'>{selected_name}</h3>",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(f"""
        <div style="display: flex; align-items: center; height: 100%; padding-top: 5px;">
            <div style="display: flex; border-radius: 8px; overflow: hidden; border: 1px solid #151b54;">
                <div style="background-color: #151b54; color: white; padding: 8px 12px; font-weight: 500; font-size: 0.85rem; display: flex; align-items: center; gap: 6px;">
                    <i class="fa-solid fa-stopwatch"></i> LATENCY
                </div>
                <div style="background-color: #ffffff; color: #151b54; padding: 8px 15px; font-weight: 700; font-size: 1.1rem;">
                    {current_latency}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- RESULT TABS ---
tab1, tab2 = st.tabs(["JSON Intelligence", "Braille Output"])

with tab1:
    if json_content:
        st.json(json_content)
        # Use st.download_button, NOT st.button
        st.download_button(
            label=" Download JSON",
            data=json_content,
            file_name=f"{base_name}.json",
            mime="application/json",
            icon=":material/download:"
        )
    else:
        st.warning("JSON not found")

with tab2:
    if braille_content:
        st.code(braille_content, language=None)
        # Use st.download_button, NOT st.button
        st.download_button(
            label=" Download Braille",
            data=braille_content,
            file_name=f"{base_name}_braille.txt",
            icon=":material/download:"
        )
    else:
        st.warning("Braille file not found")