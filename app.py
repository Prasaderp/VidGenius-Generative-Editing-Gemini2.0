import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai

import time
from pathlib import Path
import tempfile
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Page configuration with modern theme
st.set_page_config(
    page_title="VidGenius - GenAI Video Optimization",
    page_icon="✪", # Stylish alternative to scissors
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cache the agent initialization at the top level
@st.cache_resource
def initialize_editor_agent():
    return Agent(
        name="VidGenius Engine",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

# Initialize agent PROPERLY (this was missing in previous version)
video_editor_agent = initialize_editor_agent()

# Custom CSS for professional appearance
st.markdown(f"""
    <style>
    /* Main theme colors */
    :root {{
        --primary: #2b313e;
        --secondary: #3a4253;
        --accent: #5e81ff;
        --text: #f0f2f6;
    }}

    /* Base styling */
    .stApp {{
        background: linear-gradient(160deg, var(--primary) 0%, var(--secondary) 100%);
        color: var(--text);
    }}

    /* Header styling */
    h1 {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.8rem !important;
        margin-bottom: 0.5rem !important;
        background: linear-gradient(45deg, #5e81ff 30%, #8f7eff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* Uploader customization */
    .stFileUploader {{
        border: 2px dashed var(--accent) !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }}

    /* Button styling */
    .stButton>button {{
        border: none !important;
        background: var(--accent) !important;
        color: white !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }}

    .stButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(94, 129, 255, 0.3);
    }}

    /* Video preview styling */
    video {{
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        margin: 1.5rem 0;
        width: 100% !important;
        height: auto !important;
    }}

    /* Text area styling */
    .stTextArea textarea {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: var(--text) !important;
        border-radius: 8px;
        height: 140px !important;
    }}

    /* Results container */
    [data-testid="stExpander"] {{
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Main content layout
with st.container():
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.title("VidGenius")
        st.caption("GENAI-POWERED NARRATIVE OPTIMIZATION")
        st.markdown("---")
        
    with col2:
        st.header("", divider="rainbow")
        st.subheader("Video Analysis Engine - Powered by Gemini 2.0", anchor=False)

# File upload section
with st.container():
    st.markdown("### Step 1: Upload Media")
    uploaded_video = st.file_uploader(
        "Select video file (MP4, MOV, AVI):",
        type=['mp4', 'mov', 'avi'],
        label_visibility="collapsed"
    )

# Analysis section
if uploaded_video:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(uploaded_video.read())
        video_temp_path = temp_file.name

    with st.container():
        st.markdown("### Step 2: Video Preview")
        st.video(video_temp_path, format="video/mp4")

    with st.container():
        st.markdown("### Step 3: Objectives")
        editing_goal = st.text_area(
            "Specify your optimization goals:",
            help="Be specific about content priorities, and requirements.",
            label_visibility="collapsed"
        )

    # Analysis button
    if st.button("🚀 Start AI Analysis", use_container_width=True, type="primary"):
        if not editing_goal:
            st.warning("Please define optimization goals before analysis")
        else:
            try:
                with st.status("Analyzing content...", expanded=True) as status:
                    st.write("🔍 Initializing Gemini Vision model")
                    uploaded_video_data = upload_file(video_temp_path)
                    
                    st.write("⏳ Processing video frames (this may take 1-2 minutes)")
                    while uploaded_video_data.state.name == "PROCESSING":
                        time.sleep(1)
                        uploaded_video_data = get_file(uploaded_video_data.name)

                    st.write("🧠 Generating optimization strategy")
                    edit_request = f"""
                    As a professional video editor, analyze this video and provide:
                    1. Detailed timeline segmentation
                    2. Redundancy analysis with timestamps
                    3. Key narrative moments to enhance
                    4. Technical recommendations (cuts, transitions, aspect ratios)
                    
                    User goals: {editing_goal}
                    """
                    
                    edit_suggestions = video_editor_agent.run(
                        edit_request, videos=[uploaded_video_data]
                    )
                    status.update(label="Analysis complete", state="complete")

                # Display results in expandable sections
                if "## Detailed Analysis" in edit_suggestions.content:
                    parts = edit_suggestions.content.split("## Detailed Analysis")
                    summary = parts[0]
                    details = "## Detailed Analysis" + parts[1] if len(parts) > 1 else "No detailed analysis available."
                else:
                    summary = edit_suggestions.content
                    details = "Detailed analysis not found."

                # Display results
                with st.expander("📋 Executive Summary", expanded=True):
                    st.markdown(summary)

                with st.expander("🕒 Detailed Timeline Analysis"):
                    st.markdown(details)

            except Exception as e:
                st.error(f"Professional workflow error: {str(e)}")
            finally:
                Path(video_temp_path).unlink(missing_ok=True)

# Footer
st.markdown("---")
st.caption("© 2025 VidGenius Engine ∙ Generative AI Video Optimization System")