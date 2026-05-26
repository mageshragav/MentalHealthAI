"""
Streamlit Frontend for DSM-5 Psychological Analysis System
User interface with disclaimer and symptom analysis
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import get_settings


# Page configuration
st.set_page_config(
    page_title="DSM-5 Psychological Analysis System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load settings
settings = get_settings()
BACKEND_URL = settings.backend_url


# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .disclaimer-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .disclaimer-title {
        color: #856404;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .disclaimer-text {
        color: #856404;
        font-size: 1rem;
        line-height: 1.6;
    }
    .source-box {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .analysis-box {
        background-color: #e7f3ff;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health() -> bool:
    """Check if backend is accessible"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def show_disclaimer_page():
    """Display disclaimer page"""
    st.markdown('<div class="main-header">🧠 DSM-5 Psychological Analysis System</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚠️ IMPORTANT MEDICAL DISCLAIMER ⚠️</div>
        <div class="disclaimer-text">
            <p><strong>This system is NOT a substitute for professional medical advice, diagnosis, or treatment.</strong></p>
            
            <p>The analysis provided by this system is for <strong>informational and educational purposes only</strong>. 
            It is NOT intended to diagnose, treat, cure, or prevent any mental health condition.</p>
            
            <p><strong>You are NOT receiving medical advice from a licensed healthcare professional.</strong> 
            This system uses artificial intelligence to provide educational information about DSM-5 diagnostic criteria 
            based on your symptom description.</p>
            
            <p><strong>Always seek the advice of qualified mental health professionals</strong> with any questions 
            you may have regarding a medical or psychological condition. Never disregard professional medical advice 
            or delay in seeking it because of something you have read or received from this system.</p>
            
            <p><strong>If you are experiencing a mental health emergency, please contact:</strong></p>
            <ul>
                <li>Emergency Services: <strong>911</strong> (US)</li>
                <li>National Suicide Prevention Lifeline: <strong>988</strong></li>
                <li>Crisis Text Line: Text <strong>HOME</strong> to <strong>741741</strong></li>
                <li>International Association for Suicide Prevention: <a href="https://www.iasp.info/resources/Crisis_Centres/">Find a crisis center</a></li>
            </ul>
            
            <p><strong>By clicking "I Understand and Accept" below, you acknowledge that you have read, 
            understood, and accept these limitations and disclaimers.</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✓ I Understand and Accept", key="accept_disclaimer", use_container_width=True):
            st.session_state.disclaimer_accepted = True
            st.rerun()
        
        if st.button("✗ I Do Not Accept", key="decline_disclaimer", use_container_width=True):
            st.error("You must accept the disclaimer to use this system.")
            st.stop()


def show_analysis_page():
    """Display main analysis page"""
    # Header
    st.markdown('<div class="main-header">🧠 DSM-5 Symptom Analysis</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.info(
            "This system uses Retrieval-Augmented Generation (RAG) to analyze your symptoms "
            "against DSM-5 diagnostic criteria. It provides educational information only."
        )
        
        st.header("🔧 System Status")
        if check_backend_health():
            st.success("✓ Backend Connected")
        else:
            st.error("✗ Backend Unavailable")
            st.warning("Please ensure the FastAPI backend is running:\n```python backend/main.py```")
        
        st.header("📚 Resources")
        st.markdown("""
        - [SAMHSA National Helpline](https://www.samhsa.gov/find-help/national-helpline)
        - [NAMI (National Alliance on Mental Illness)](https://www.nami.org/)
        - [Mental Health America](https://www.mhanational.org/)
        """)
        
        if st.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    st.markdown("### 📝 Describe Your Symptoms")
    st.markdown("Please provide a detailed description of the psychological symptoms you're experiencing.")
    
    # Input form
    with st.form("symptom_form"):
        symptoms = st.text_area(
            "Symptoms Description *",
            height=200,
            placeholder="Example: I've been feeling very sad and hopeless for the past month. I have no energy, can't concentrate on work, and have lost interest in activities I used to enjoy. My sleep is disrupted...",
            help="Describe your symptoms in detail. The more information you provide, the better the analysis."
        )
        
        duration = st.text_input(
            "Duration (Optional)",
            placeholder="Example: 3 weeks, 2 months, etc.",
            help="How long have you been experiencing these symptoms?"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submit_button = st.form_submit_button("🔍 Analyze Symptoms", use_container_width=True)
    
    # Process submission
    if submit_button:
        if not symptoms or len(symptoms.strip()) < 10:
            st.error("Please provide a more detailed description of your symptoms (at least 10 characters).")
        else:
            analyze_symptoms(symptoms, duration)


def analyze_symptoms(symptoms: str, duration: Optional[str]):
    """Send symptoms to backend and display results"""
    with st.spinner("🔄 Analyzing your symptoms against DSM-5 criteria... This may take a moment."):
        try:
            # Prepare request
            payload = {
                "symptoms": symptoms,
                "duration": duration if duration else None
            }
            
            # Send request to backend
            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                display_results(data)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Please ensure the FastAPI server is running.")
            st.code("python backend/main.py", language="bash")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")


def display_results(data: dict):
    """Display analysis results"""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Analysis
    st.markdown('<div class="analysis-box">', unsafe_allow_html=True)
    st.markdown("### 🔍 AI Analysis")
    st.markdown(data["analysis"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sources
    if data.get("sources"):
        st.markdown("### 📚 Source Evidence from DSM-5")
        st.markdown("The following DSM-5 sections were used in the analysis:")
        
        for idx, source in enumerate(data["sources"], 1):
            with st.expander(f"📄 Source {idx}: {source.get('disorder_name', 'Unknown')} (Relevance: {source.get('relevance_score', 0):.1%})"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown("**Metadata:**")
                    if source.get("disorder_category"):
                        st.markdown(f"**Category:** {source['disorder_category']}")
                    if source.get("criteria_label"):
                        st.markdown(f"**Criteria:** {source['criteria_label']}")
                    if source.get("icd_code"):
                        st.markdown(f"**ICD Code:** {source['icd_code']}")
                    if source.get("page_number"):
                        st.markdown(f"**Page:** {source['page_number']}")
                
                with col2:
                    st.markdown("**Content:**")
                    st.markdown(f"```\n{source['content']}\n```")
    
    # Disclaimer reminder
    st.markdown("---")
    st.warning("⚠️ **REMINDER:** " + data.get("disclaimer", "This is not a medical diagnosis. Please consult a qualified healthcare professional."))
    
    # Metadata
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"🤖 Model: {data.get('model_used', 'Unknown')}")
    with col2:
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        st.caption(f"🕐 Generated: {timestamp}")


def main():
    """Main application"""
    # Initialize session state
    if 'disclaimer_accepted' not in st.session_state:
        st.session_state.disclaimer_accepted = False
    
    # Show appropriate page
    if not st.session_state.disclaimer_accepted:
        show_disclaimer_page()
    else:
        show_analysis_page()


if __name__ == "__main__":
    main()

# Made with Bob
