import streamlit as st
import os
from PIL import Image
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "pages", "animations", "main.png")

try:
    img = Image.open(logo_path)
except Exception:
    # Fallback to a string emoji if the path is wrong so the app doesn't crash
    img = "📂"

def make_navbar():
    # 1. CSS for the Top Bar and Button Styling
    st.markdown("""
        <style>
            /* Import a cursive font from Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@400..700&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');            /* Force remove the default Streamlit header */
            header[data-testid="stHeader"] {
                display: none !important;
            }

            /* Pull the main content up to meet the navbar */
            .block-container {
                padding-top: 2rem !important;
            }

            /* The Bar Container */
            .nav-wrapper {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 5% 10px 5%;
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 999999;
                height: 70px;
            }

            /* Logo Side */
            .logo-section {
                display: flex;
                align-items: center;
                gap: 10px;
                font-family: 'Inter', sans-serif;
            }

            .logo-text {
                color: #ffffff;
                /* Applied Dancing Script here */
                font-family: 'Dancing Script', cursive; 
                font-size: 32px; /* Dancing Script often needs to be a bit larger */
                font-weight: 700;
                /* A subtle glow to make the cursive pop against the purple */
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }

            /* Fix Streamlit Padding so content doesn't go under the nav */
            .block-container {
                padding-top: 50px !important;
            }
            
            [data-testid="stHeader"] {
                display: none;
            }

            /* Make Streamlit buttons look like clean nav links */
            div[data-testid="stHorizontalBlock"] button {
                min-width: 150px !important;
                padding-top: 10px !important;
                padding-bottom: 10px !important;

                background-color: transparent !important;
                border: none !important;
                color: #FFFFFF !important;
                font-weight: 500 !important;
                font-size: 16px !important;
            }
            
            div[data-testid="stHorizontalBlock"] button:hover {
                color: #FFFFFF !important;
                text-decoration: none !important;
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
                background: #ffffff;
                color: #ffffff;
                border: 2px solid #ffffff;
                padding: 22px 60px;
                border-radius: 16px;
                font-weight: 600;
                font-size: 20px;
            }
        </style>
    """, unsafe_allow_html=True)


    # 2. Creating the Navbar structure using Streamlit Columns
    # This places the Logo on the left and the nav items on the right
    
    # We use a container to act as our "Wrapper"
    with st.container():
        # Column setup: [Logo Space, Spacer, Nav Items]
        c1, c2, c3, c4 = st.columns([0.11, 0.18, 0.46, 0.6])
        
        with c1:
            st.image(img)
        with c2:
            st.markdown("""
                <div class="logo-section">
                    <span class="logo-text">M-Parser</span>
                </div>
            """, unsafe_allow_html=True)
            
        with c4:
            # We use an inner set of columns for the buttons to keep them horizontal
            sub1, sub2, sub3 = st.columns(3)
            with sub1:
                if st.button("Home",type="primary"):
                    st.switch_page("streamlit_app.py") # Change to your main file name
            with sub2:
                if st.button("Process",type="primary"):
                    st.switch_page("pages/1_Upload_and_Process.py")
            with sub3:
                if st.button("Result",type="primary"):
                    st.switch_page("pages/2_Parsed_Output.py")