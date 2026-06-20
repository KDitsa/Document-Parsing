import streamlit as st
import os
from PIL import Image
from navigation import make_navbar

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "pages", "animations", "M-PARSER.png")
work_gif_path = os.path.join(current_dir, "pages", "animations", "loader.gif")
pic_path = os.path.join(current_dir, "pages", "animations", "pic.png")
try:
    img = Image.open(logo_path)
except Exception:
    # Fallback to a string emoji if the path is wrong so the app doesn't crash
    img = "📂"

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="M-PARSER | Multimodal Intelligence",
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded"
)

make_navbar()

# --- 2. REFINED BLUE CSS ---
st.markdown("""
    <!-- Load Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Reduce default Streamlit top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }

    .stApp {
        background: linear-gradient(180deg, #2F069C 0%, #C5B1FC 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 1. HERO SECTION: Reduced top margin to fix "big space" */
    .hero-section {
        position: relative;
        background: linear-gradient(135deg, #6c2dc7 0%, #e6a9ec 40%, #dbeafe 100%);
        border: 1px solid #e2e8f0;
        padding: 60px;
        margin-top: 10px; 
        margin-bottom: 40px;
        text-align: center;

        width: 100%;
        max-width: 100;
        margin-left: 200px;
        margin-right: -350px;

        border-radius: 40px;

        -webkit-mask-image: radial-gradient(circle at right center, 
                            transparent 200px, black 201px);
        mask-image: radial-gradient(circle at right center, 
                            transparent 200px, black 201px);
    }

    .header-title {
        color: #1E3A8A;
        font-size: 72px;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 24px;
    }

    /* 2. ACTION BAR CENTERING */
    .action-subtext {
        color: #fefcff !important;
        font-size: 20px !important;
        font-weight: 600 !important;
        line-height: 1.1 !important;
        display: flex !important;
        align-items: center !important; /* Vertically centers text with the GIF */
        height: 100%; /* Important for vertical centering */
        margin: 0 !important;
    }

    .pipeline-container {
        display: flex;
        justify-content: center;
        width: 100%;
        margin-top: 40px;
    }

    .pipeline {
        text-align: center;
        color: #1E3A8A;
        font-weight: 600;
        font-size: 18px;
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 50px;
        padding: 15px 45px;
        box-shadow: 0 4px 15px rgba(30, 58, 138, 0.08);
    }

    /* Icon Coloring Logic */
    .icon-blue-dark { color: #1E3A8A; }
    .icon-blue-bright { color: #3B82F6; }

    /* 3. FEATURE CARDS */
    .feature-card {
        background: linear-gradient(135deg, #e6a9ec 0%, #fdeef4 40%, #dbeafe 100%);
        padding: 40px;
        border-radius: 24px;
        border: 1px solid #e5e7eb;
        transition: all 0.4s ease;
        height: 100%;
        margin-bottom: 20px;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        border-color: #504a4b;
        box-shadow: 0 20px 40px rgba(30, 58, 138, 0.08);
    }

    /* 4. BUTTON STYLING */
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
        background: #ffffff;
        color: #ffffff;
        border: 2px solid #ffffff;
        padding: 22px 60px;
        border-radius: 16px;
        font-weight: 600;
        font-size: 20px;
    }

    div.stButton > button:first-child:hover {
        box-shadow: 0 10px 20px rgba(30, 58, 138, 0.2);
        transform: translateY(-2px);
    }

    /* Metric highlights */
    .metric-box {
        text-align: center;
        padding: 40px 20px;
        border-top: 1px solid #e2e8f0;
        font-size: 20px
    }
    .metric-num {
        color: #151b54;
        font-size: 42px;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(255,255,255,1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HERO SECTION ---
col1, col2 = st.columns([3, 1],gap="small")  # Adjust ratio as needed

with col1:
    st.markdown("""
        <div class="hero-section">
            <div class="header-title">M-PARSER</div>
            <p style="font-size: 24px; color: #2B292E; max-width: 800px; margin: 0 auto; line-height: 1.6; text-align: left;">
                    Turn chaos into structure. Instantly.<br>
                    <span style="color: #250F91; font-weight: 600;">AI that understands documents like humans do — but faster.</span>
                </p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    # This centers the robot image within its (now stacked) column space
    st.markdown('<div style="margin-top: 20px; text-align: center;">', unsafe_allow_html=True)
    # Re-using your original circular image path 'pic_path'
    st.image(pic_path, width=360)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. ACTION BAR ---
# Centered text using wrapper
c1, c2, c3, c4 = st.columns([1.8, 0.5, 1.5, 1.7])
with c2:
    st.image(work_gif_path)
with c3:
    st.markdown('<div><p class="action-subtext"><br><br>Try it on your own files in seconds</p></div>', unsafe_allow_html=True)

c_left, c_mid, c_right = st.columns([1, 1.5, 1])
with c_mid:
    if st.button("Enter Processing Suite", icon=":material/bolt:", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Upload_and_Process.py")

# Pipeline with Professional Colored Icons
st.markdown(f"""
    <div class="pipeline-container">
        <div class="pipeline">
            <i class="fa-solid fa-cloud-arrow-up icon-blue-dark"></i> Upload &nbsp; &bull; &nbsp; 
            <i class="fa-solid fa-microchip icon-blue-bright"></i> Analyze &nbsp; &bull; &nbsp; 
            <i class="fa-solid fa-brain icon-blue-dark"></i> Understand &nbsp; &bull; &nbsp; 
            <i class="fa-solid fa-table-list icon-blue-bright"></i> Structure &nbsp; &bull; &nbsp; 
            <i class="fa-solid fa-file-export icon-blue-bright"></i> Export
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)

# --- 5. FEATURE GRID ---
cols = st.columns(3)
features = [
    {"icon": "fa-layer-group", "title": "Visual Reconstruction", "text": "Advanced layout analysis (PP-StructureV3) maintains the integrity of complex tables and document hierarchies."},
    {"icon": "fa-file-waveform", "title": "Acoustic Intelligence", "text": "Speaker diarization and Whisper-powered transcription turn audio noise into actionable meeting insights."},
    {"icon": "fa-universal-access", "title": "Inclusive Design", "text": "Integrated Braille Engine converts complex digital assets into accessible formats for universal data consumption."}
]

for i, col in enumerate(cols):
    with col:
        st.markdown(f"""
            <div class="feature-card">
                <div style="font-size: 40px; margin-bottom: 20px;">
                    <i class="fa-solid {features[i]['icon']} icon-blue-dark"></i>
                </div>
                <h3 style="color: #1E3A8A; margin-bottom: 15px;">{features[i]['title']}</h3>
                <p style="color: #504a4b; font-size: 16px; line-height: 1.6;">{features[i]['text']}</p>
            </div>
            """, unsafe_allow_html=True)

# --- 6. USE CASE SECTION (Maintained as requested) ---
st.markdown("<div style='margin-top: 120px;'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #fefcff;'>Industry Use Cases</h2>", unsafe_allow_html=True)
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    st.markdown("""
        <div style="background: linear-gradient(130deg, #FFB5B5 0%, #fdeef4 40%, #FFD1D1 100%); padding: 30px; border-radius: 20px; border-left: 5px solid #3d3c3a; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h4 style="color: #1E3A8A;">Enterprise Knowledge Mining</h4>
            <p style="color: #504a4b;">Convert decades of legacy PDF reports and internal memos into a searchable, structured vector database for RAG-based AI systems.</p>
        </div>
    """, unsafe_allow_html=True)
with u2:
    st.markdown("""
        <div style="background: linear-gradient(130deg, #FFB5B5 0%, #fdeef4 40%, #FFD1D1 100%); padding: 30px; border-radius: 20px; border-left: 5px solid #3d3c3a; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <h4 style="color: #1E3A8A;">Automated Media Cataloging</h4>
            <p style="color: #504a4b;">Process video archives to extract spoken text, identify visual cues, and generate structured metadata for broadcast libraries.</p>
        </div>
    """, unsafe_allow_html=True)

# --- 7. METRICS & FOOTER (Maintained as requested) ---
st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown('<div class="metric-box"><div class="metric-num">4</div><p style="color:#ffffff;">Modalities Unified</p></div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-box"><div class="metric-num">13+</div><p style="color:#ffffff;">Formats Supported</p></div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-box"><div class="metric-num">Real-Time</div><p style="color:#ffffff;">Processing Pipeline</p></div>', unsafe_allow_html=True)

st.markdown(
    """
    <div style="margin-top: 60px; text-align:center; color:#ffffff; font-size:15px; padding-bottom: 50px;">
        M-Parser v1.0 • Built for Multimodal Document Parsing • 2026
    </div>
    """, unsafe_allow_html=True)