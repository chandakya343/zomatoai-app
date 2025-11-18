"""
ZomatoAI Manager - Streamlit Web Application
Personalized food recommendation system with memory management
"""

import streamlit as st
import os
from datetime import datetime
import json
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from food_database import get_food_database
from memory_system import MemorySystem, create_sample_user
from agent_system import AgentSystem


# Page configuration
st.set_page_config(
    page_title="ZomatoAI Manager",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Swiss Design Aesthetic CSS
st.markdown("""
<style>
    /* Swiss Design Principles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Clean, minimalist layout */
    .main {
        background-color: #ffffff;
    }
    
    /* Typography - Swiss style hierarchy */
    h1 {
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -0.02em;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-weight: 600;
        font-size: 1.5rem;
        letter-spacing: -0.01em;
        color: #1a1a1a;
        margin-top: 2rem;
    }
    
    h3 {
        font-weight: 600;
        font-size: 1.125rem;
        color: #2a2a2a;
    }
    
    /* Clean tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background-color: transparent;
        border: none;
        font-weight: 500;
        color: #666;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #000;
        border-bottom: 2px solid #000;
    }
    
    /* Clean input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        padding: 0.75rem;
        font-size: 0.95rem;
    }
    
    /* Swiss-style buttons */
    .stButton > button {
        background-color: #DC2626;
        color: #ffffff;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 0.95rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        border-radius: 4px;
        transition: all 0.2s;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #B91C1C;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    
    /* Recommendation cards */
    .recommendation-card {
        background: #f8f8f8;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.2s;
    }
    
    .recommendation-card:hover {
        border-color: #DC2626;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Dish card for selection */
    .dish-card {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .dish-card:hover {
        border-color: #DC2626;
        transform: translateY(-2px);
    }
    
    .dish-card.selected {
        border-color: #DC2626;
        background-color: #fff5f5;
    }
    
    /* Metric cards */
    .metric-card {
        background: #f8f8f8;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background-color: #f0f8f0;
        border-left: 3px solid #2d7a2d;
        border-radius: 4px;
    }
    
    .stInfo {
        background-color: #f0f4f8;
        border-left: 3px solid #1a5490;
        border-radius: 4px;
    }
    
    /* Hide sidebar by default */
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_system' not in st.session_state:
    st.session_state.agent_system = None
if 'memory_system' not in st.session_state:
    st.session_state.memory_system = None
if 'food_df' not in st.session_state:
    st.session_state.food_df = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = "user_demo_001"
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def load_system():
    """Load the agent system and food database"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in environment variables!")
        st.info("Please set your GEMINI_API_KEY in the Streamlit Cloud secrets or .env file")
        return False
    
    try:
        logger.info("🔧 Loading ZomatoAI system...")
        with st.spinner("Loading ZomatoAI system..."):
            # Load food database
            food_df = get_food_database()
            st.session_state.food_df = food_df
            
            # Initialize agent system
            agent_system = AgentSystem(api_key=api_key, food_df=food_df)
            st.session_state.agent_system = agent_system
            
            # Initialize memory system
            memory_system = MemorySystem(user_id=st.session_state.user_id)
            st.session_state.memory_system = memory_system
            
            # Create sample user if doesn't exist
            if not memory_system.user_exists():
                create_sample_user(st.session_state.user_id)
                memory_system = MemorySystem(user_id=st.session_state.user_id)
                st.session_state.memory_system = memory_system
            
        st.success("✅ System loaded successfully!")
        return True
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        logger.error(f"Error loading system: {str(e)}")
        return False

# Main app
def main():
    # Load system on first run
    if st.session_state.agent_system is None:
        if not load_system():
            st.stop()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🍔 Ask ZomatoAI", "📊 Memory", "📈 Analytics"])
    
    with tab1:
        st.header("🍔 Ask ZomatoAI")
        st.markdown("Ask for food recommendations in natural language!")
        
        # Query input
        user_query = st.text_input(
            "What are you craving?",
            placeholder="e.g., Show me vegetarian dishes under ₹200",
            key="query_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_button = st.button("Get Recommendations", type="primary", use_container_width=True)
        
        if submit_button and user_query:
            if st.session_state.agent_system is None:
                st.error("System not loaded. Please refresh the page.")
                st.stop()
            
            with st.spinner("🤖 ZomatoAI is thinking..."):
                try:
                    # Get recommendations
                    recommendations = st.session_state.agent_system.get_recommendations(
                        user_query=user_query,
                        memory_system=st.session_state.memory_system
                    )
                    
                    st.session_state.recommendations = recommendations
                    st.session_state.query_history.append({
                        'query': user_query,
                        'timestamp': datetime.now().isoformat(),
                        'recommendations_count': len(recommendations)
                    })
                    
                    st.success(f"✅ Found {len(recommendations)} recommendations!")
                    
                except Exception as e:
                    st.error(f"❌ Error getting recommendations: {str(e)}")
                    logger.error(f"Error: {str(e)}")
        
        # Display recommendations
        if st.session_state.recommendations:
            st.markdown("---")
            st.subheader("🎯 Top Recommendations")
            
            for idx, rec in enumerate(st.session_state.recommendations, 1):
                with st.container():
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h3>#{idx} {rec['dish_name']}</h3>
                        <p><strong>Restaurant:</strong> {rec['restaurant']}</p>
                        <p><strong>Price:</strong> ₹{rec['price']}</p>
                        <p><strong>Rating:</strong> {rec['rating']}⭐</p>
                        <p><strong>Why:</strong> {rec['explanation']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Feedback buttons
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        if st.button("👍", key=f"like_{idx}", use_container_width=True):
                            st.session_state.memory_system.add_feedback(
                                dish_id=rec['dish_id'],
                                rating=5,
                                feedback="Liked"
                            )
                            st.success("Feedback recorded!")
                            st.rerun()
                    with col2:
                        if st.button("👎", key=f"dislike_{idx}", use_container_width=True):
                            st.session_state.memory_system.add_feedback(
                                dish_id=rec['dish_id'],
                                rating=1,
                                feedback="Disliked"
                            )
                            st.success("Feedback recorded!")
                            st.rerun()
                    with col3:
                        if st.button("⭐", key=f"star_{idx}", use_container_width=True):
                            st.session_state.memory_system.add_feedback(
                                dish_id=rec['dish_id'],
                                rating=4,
                                feedback="Favorited"
                            )
                            st.success("Feedback recorded!")
                            st.rerun()
                    
                    st.markdown("---")
    
    with tab2:
        st.header("📊 Your Memory")
        st.markdown("What ZomatoAI knows about you")
        
        if st.session_state.memory_system:
            memory = st.session_state.memory_system.get_memory()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🧠 Active Memory")
                st.markdown("**Recent feedback (last 10):**")
                if memory['active_memory']:
                    for feedback in memory['active_memory']:
                        st.markdown(f"""
                        - **{feedback['dish_name']}**: {feedback['rating']}⭐ - {feedback['feedback']}
                        """)
                else:
                    st.info("No recent feedback yet.")
            
            with col2:
                st.subheader("💾 Permanent Memory")
                st.markdown("**Consolidated patterns:**")
                if memory['permanent_memory']:
                    st.markdown(memory['permanent_memory'])
                else:
                    st.info("No patterns learned yet.")
            
            st.markdown("---")
            st.subheader("📜 Complete Order History")
            if memory['order_history']:
                df = pd.DataFrame(memory['order_history'])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No order history yet.")
    
    with tab3:
        st.header("📈 Analytics")
        
        if st.session_state.query_history:
            st.subheader("Query History")
            history_df = pd.DataFrame(st.session_state.query_history)
            st.dataframe(history_df, use_container_width=True)
            
            st.subheader("Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Queries", len(st.session_state.query_history))
            with col2:
                avg_recs = sum(h['recommendations_count'] for h in st.session_state.query_history) / len(st.session_state.query_history) if st.session_state.query_history else 0
                st.metric("Avg Recommendations", f"{avg_recs:.1f}")
            with col3:
                st.metric("Total Dishes", len(st.session_state.food_df) if st.session_state.food_df is not None else 0)
        else:
            st.info("No queries yet. Start asking for recommendations!")

if __name__ == "__main__":
    main()

