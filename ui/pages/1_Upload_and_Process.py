import streamlit as st
import os
from PIL import Image
import datetime
import sys
import time
from navigation import make_navbar
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "animations", "M-PARSER.png")

try:
    img = Image.open(logo_path)
except Exception:
    # Fallback to a string emoji if the path is wrong so the app doesn't crash
    img = "📂"

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Upload & Process | M-PARSER",
    page_icon=img,
    layout="wide",
    initial_sidebar_state="expanded"
)

make_navbar()

# --- 2. REFINED BLUE CSS ---
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

    /* Target only the immediate container of the marker */
    div[data-testid="stVerticalBlock"] > div:has(.file-row-marker) {
        background: #342d7e;
        padding: 0px 5px;
        border-radius: 16px;
        transition: all 0.3s ease;
    }


    .badge {
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 15px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .status-uploaded { background: #dbeafe; color: #1e40af; }
    .status-processed { background: #dcfce7; color: #166534; }
    .status-error { background: #fee2e2; color: #991b1b; }
    .status-processing { background: #fef9c3; color: #854d0e; }

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

    [data-testid="stFileUploader"] label{
        color: #ffffff !important;
        font-size: 20px !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DIRECTORY SETUP & IMPORTS ---
current_dir = os.path.dirname(__file__)
app_dir = os.path.dirname(os.path.dirname(current_dir))
UPLOAD_DIR = os.path.join(app_dir, "app", "user_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 4. SESSION STATE ---
if 'files' not in st.session_state: st.session_state.files = []
if 'is_processing' not in st.session_state: st.session_state.is_processing = False
if 'uploader_key' not in st.session_state: st.session_state.uploader_key = 0

is_actually_working = any(f['status'] == "Processing" for f in st.session_state.files)

# If the state says we are processing, but no file has that status, UNLOCK.
if not is_actually_working:
    st.session_state.is_processing = False
else:
    st.session_state.is_processing = True

# --- 5. MAIN UI ---
st.markdown('<div class="section-header"><i class="fa-solid fa-file-import"></i> Document Ingestion</div>', unsafe_allow_html=True)

# Upload Area
with st.container():
    uploaded_file = st.file_uploader(
        "Upload documents or media files for structured intelligence extraction",
        type=["pdf", "txt", "docx", "png", "jpg", "jpeg", "wav", "mp3", "flac", "m4a", "mp4", "mov", "mkv"],
        disabled=st.session_state.is_processing,
        key=f"uploader_{st.session_state.uploader_key}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Handle file saving
if uploaded_file is not None and not st.session_state.is_processing:
    existing_names = [f['name'] for f in st.session_state.files]
    
    if uploaded_file.name not in existing_names:
        save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.files.append({
            "name": uploaded_file.name,
            "type": uploaded_file.type.split('/')[-1].upper(),
            "status": "Uploaded",
            "time": datetime.datetime.now().strftime("%H:%M"),
            "path": save_path
        })
        st.session_state.uploader_key += 1
        st.rerun()

# --- 6. DATA TABLE ---
import threading

# 1. Define the worker function outside the UI
def background_worker(file_obj):
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
        from app.core.processor import process_file
        # Perform the heavy lifting
        result = process_file(file_obj["path"])
        
        if result.get("success"):
            file_obj["status"] = "Processed"
            file_obj["latency"] = result.get("time", "N/A")
        else:
            file_obj["status"] = "Error"
    except Exception as e:
        file_obj["status"] = "Error"
        print(f"Thread Error: {e}")

if st.session_state.files:
    st.markdown("### <i class='fa-solid fa-layer-group' style='color:#e5e4e2'></i> <span style='color:#e5e4e2'> Processing Queue</span>", unsafe_allow_html=True)
    st.divider()
    # --- CENTERED HEADERS ---
    h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 2, 2])
    
    header_style = "color: #ffffff; font-size: 1.2rem; margin-bottom: 0; text-align: center; font-weight: bold;"
    
    h1.markdown(f"<p style='{header_style}'>FILENAME</p>", unsafe_allow_html=True)
    h2.markdown(f"<p style='{header_style}'>TYPE</p>", unsafe_allow_html=True)
    h3.markdown(f"<p style='{header_style}'>ADDED</p>", unsafe_allow_html=True)
    h4.markdown(f"<p style='{header_style}'>STATUS</p>", unsafe_allow_html=True)
    h5.markdown(f"<p style='{header_style}'>ACTION</p>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    for idx, file in enumerate(st.session_state.files):
        with st.container():
            # This marker triggers your custom CSS for the white card & hover effect
            st.markdown('<span class="file-row-marker"></span>', unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 2])
            
            # Common style for centering content vertically and horizontally
            cell_style = "color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; text-align: center; padding-top:25px;"
            cell_style_1 = "font-size: 1.5rem; display: flex; align-items: center; justify-content: center; text-align: center; padding-top:25px;"
            
            # 1. Filename (Now Centered)
            c1.markdown(f"<div style='{cell_style}'><strong>{file['name']}</strong></div>", unsafe_allow_html=True)
            
            # 2. Type (Centered)
            c2.markdown(f"<div style='{cell_style_1}'><code>{file['type']}</code></div>", unsafe_allow_html=True)
            
            # 3. Added Time (Centered)
            c3.markdown(f"<div style='{cell_style}'>{file['time']}</div>", unsafe_allow_html=True)
            
            # 4. Status Badge (Centered)
            s_map = {"Uploaded": "status-uploaded", "Processed": "status-processed", "Processing": "status-processing", "Error": "status-error"}
            current_status = file['status']
            c4.markdown(f"""
                <div style='{cell_style}'>
                    <span class="badge {s_map.get(current_status, "")}">{current_status}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 5. Action Button
            with c5:
                st.markdown(
                    """
                    <div style="
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        height:100%;
                    ">
                    """,unsafe_allow_html=True)
                # 1. TRIGGER: Start the background thread
                if file["status"] in ["Uploaded", "Error"]:
                    if st.button("Run Parser", key=f"run_{idx}", use_container_width=True, icon=":material/play_arrow:", type="primary"):
                        file["status"] = "Processing"
                        # Start the background thread
                        t = threading.Thread(target=background_worker, args=(file,))
                        st.session_state[f"thread_{idx}"] = t
                        t.start()
                        st.rerun()

                # 2. MONITOR: Check thread status while busy
                elif file["status"] == "Processing":
                    st.button("Analyzing...", key=f"busy_{idx}", disabled=True, use_container_width=True, icon=":material/document_search:", type="primary")
                    
                    thread_key = f"thread_{idx}"
                    if thread_key in st.session_state:
                        # If the thread finished its work in the background
                        if not st.session_state[thread_key].is_alive():
                            del st.session_state[thread_key]
                            st.rerun() # Refresh to show the "View Output" button
                        else:
                            # Still working? Refresh every 2 seconds to check again
                            time.sleep(2)
                            st.rerun()

                # 3. SUCCESS: Show the view button
                elif file["status"] == "Processed":
                    if st.button("View Output", key=f"view_{idx}", use_container_width=True, icon=":material/visibility:", type="primary"):
                        st.session_state.selected_file = file["name"]
                        st.switch_page("pages/2_Parsed_Output.py")
                st.markdown("</div>", unsafe_allow_html=True)
else:
    # Empty State
    st.markdown("""
        <div style="text-align: center; padding: 100px; background: #ffffff; border-radius: 24px; border: 2px dashed #cbd5e1; margin-top: 20px;">
            <i class="fa-solid fa-folder-plus" style="font-size: 48px; color: #cbd5e1; margin-bottom: 20px;"></i>
            <h3 style="color: #64748b; font-weight: 600;">No files currently in queue</h3>
            <p style="color: #94a3b8;">Your uploaded files will appear here for processing.</p>
        </div>
    """, unsafe_allow_html=True)