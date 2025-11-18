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
        background-color: #000000;
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
        background-color: #2a2a2a;
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
        border-color: #000;
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
        border-color: #000;
        transform: translateY(-2px);
    }
    
    .dish-card.selected {
        border-color: #000;
        background-color: #f8f8f8;
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


def initialize_session_state():
    """Initialize session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user_id = "user_demo_001"
        st.session_state.conversation_history = []
        st.session_state.current_recommendations = []
        st.session_state.selected_dish = None
        st.session_state.show_feedback_form = False


def load_system():
    """Load all system components"""
    if 'system_loaded' not in st.session_state:
        logger.info("🔧 Loading ZomatoAI system...")
        
        with st.spinner("Loading ZomatoAI system..."):
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("❌ API key not found in environment")
                st.error("⚠️ API key not found. Please configure GEMINI_API_KEY in .env file")
                st.stop()
            
            logger.info(f"✅ API key loaded: {api_key[:10]}...{api_key[-5:]}")
            
            # Load food database
            st.session_state.food_df = get_food_database()
            logger.info(f"✅ Food database loaded: {len(st.session_state.food_df)} dishes")
            
            # Load or create user memory
            st.session_state.memory = MemorySystem(st.session_state.user_id)
            
            # Check if user exists, if not create sample user
            if len(st.session_state.memory.memory['order_history']) == 0:
                logger.info("📝 Creating sample user...")
                st.session_state.memory = create_sample_user()
            
            logger.info(f"✅ User memory loaded: {len(st.session_state.memory.memory['order_history'])} orders")
            
            # Initialize agents
            st.session_state.agents = AgentSystem(api_key, st.session_state.food_df)
            logger.info("✅ AI agents initialized")
            
            st.session_state.system_loaded = True
            logger.info("🎉 System loaded successfully!")


def parse_recommendations(response_text):
    """Parse recommendations from response text"""
    import re
    
    logger.info("🔍 Parsing recommendations from response...")
    logger.info(f"   Response length: {len(response_text)} chars")
    
    recommendations = []
    
    # Pattern to match: 1. **Dish Name - Restaurant (₹Price)**
    pattern = r'\d+\.\s+\*\*(.*?)\s+-\s+(.*?)\s+\(₹(\d+)\)\*\*'
    matches = re.findall(pattern, response_text)
    
    logger.info(f"   Found {len(matches)} regex matches")
    
    for dish_name, restaurant, price in matches:
        rec = {
            'dish_name': dish_name.strip(),
            'restaurant': restaurant.strip(),
            'price': int(price)
        }
        recommendations.append(rec)
        logger.info(f"   ✓ {rec['dish_name']} - {rec['restaurant']} (₹{rec['price']})")
    
    if not recommendations:
        logger.warning("⚠️  No recommendations parsed! Check response format.")
        logger.info(f"   Response preview: {response_text[:500]}")
    
    return recommendations


def show_recommendation_tab():
    """Main recommendation tab"""
    st.header("🍔 Ask ZomatoAI")
    
    # Query input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_query = st.text_area(
            "What would you like to eat?",
            placeholder="E.g., 'I want something spicy and under ₹300' or 'Show me vegetarian options'",
            height=100,
            key="query_input"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        submit_btn = st.button("🔍 Get Recommendations", key="submit_query")
    
    if submit_btn and user_query:
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 SUBMIT BUTTON CLICKED")
        logger.info(f"{'='*80}")
        logger.info(f"Query: {user_query}")
        
        with st.spinner("🤖 ZomatoAI is thinking..."):
            try:
                logger.info("🚀 Starting query processing...")
                
                # Process query
                response, debug_info = st.session_state.agents.process_query(
                    user_query,
                    st.session_state.memory.get_memory_context()
                )
                
                logger.info("✅ Query processed successfully!")
                logger.info(f"📝 Response length: {len(response)} chars")
                
                # Save to conversation history
                st.session_state.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "query": user_query,
                    "response": response,
                    "debug": debug_info
                })
                
                logger.info("💾 Saved to conversation history")
                
                # Parse recommendations
                recommendations = parse_recommendations(response)
                st.session_state.current_recommendations = recommendations
                
                logger.info(f"📊 Parsed {len(recommendations)} recommendations")
                
                # Display response
                st.markdown("### 🎯 Your Personalized Recommendations")
                st.markdown(f'<div class="recommendation-card">{response}</div>', unsafe_allow_html=True)
                
                logger.info("✅ Response displayed in UI")
                
                # Ask which one they chose
                if recommendations:
                    st.markdown("---")
                    st.markdown("### 🍽️ Which one did you choose?")
                    st.write("Click on the dish you ordered:")
                    
                    cols = st.columns(min(len(recommendations), 3))
                    for idx, rec in enumerate(recommendations):
                        with cols[idx % 3]:
                            if st.button(
                                f"✓ {rec['dish_name']}\n{rec['restaurant']} • ₹{rec['price']}",
                                key=f"choice_btn_{idx}",
                                use_container_width=True
                            ):
                                logger.info(f"🍽️  User selected dish: {rec['dish_name']}")
                                st.session_state.selected_dish = rec
                                st.session_state.show_feedback_form = True
                                st.rerun()
                else:
                    logger.warning("⚠️  No recommendations to display!")
            
            except Exception as e:
                logger.error(f"❌ ERROR: {e}", exc_info=True)
                st.error(f"Error processing query: {e}")
                st.error("Check terminal logs for details.")
    
    # Show feedback form if dish selected
    if st.session_state.show_feedback_form and st.session_state.selected_dish:
        st.markdown("---")
        show_feedback_form()


def show_feedback_form():
    """Show feedback form for selected dish"""
    dish = st.session_state.selected_dish
    
    st.markdown("---")
    st.markdown(f"### 📝 How was your {dish['dish_name']}?")
    st.write(f"**Restaurant:** {dish['restaurant']} | **Price:** ₹{dish['price']}")
    st.write("")
    
    with st.form("feedback_form_main", clear_on_submit=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            rating = st.slider("⭐ Rating", 1.0, 5.0, 4.0, 0.5)
        
        with col2:
            st.write("")  # Spacing
            stars_display = "⭐" * int(rating)
            st.markdown(f"### {stars_display}")
        
        feedback_text = st.text_area(
            "Tell us about your experience",
            placeholder="What did you love? What could be better?",
            height=120
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit = st.form_submit_button("✅ Submit Feedback", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        
        if submit and feedback_text:
            logger.info(f"💬 Saving feedback: {dish['dish_name']} - {rating}★")
            
            # Add feedback to memory
            st.session_state.memory.add_feedback(
                dish.get('dish_id', 'unknown'),
                dish['dish_name'],
                feedback_text,
                rating
            )
            
            # Also add to order history if not already there
            st.session_state.memory.add_order(
                dish.get('dish_id', 'unknown'),
                dish['dish_name'],
                dish['restaurant'],
                dish['price']
            )
            
            logger.info(f"✅ Feedback saved successfully!")
            
            st.success(f"✅ Thanks for your feedback! Rated {rating}★ - We'll use this to personalize future recommendations.")
            st.balloons()
            
            st.session_state.show_feedback_form = False
            st.session_state.selected_dish = None
            
            # Wait a moment before rerunning
            import time
            time.sleep(1)
            st.rerun()
        
        if cancel:
            logger.info("❌ Feedback cancelled")
            st.session_state.show_feedback_form = False
            st.session_state.selected_dish = None
            st.rerun()


def show_history_tab():
    """Order history and feedback tab"""
    st.header("📊 Your History")
    
    memory = st.session_state.memory
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🛒 Order History")
        orders = memory.get_order_history()
        
        if orders:
            for order in reversed(orders[-10:]):  # Last 10 orders
                st.markdown(f"""
                <div class="dish-card">
                    <strong>{order['dish_name']}</strong><br>
                    <small>{order['restaurant']} • ₹{order['price']}</small><br>
                    <small style="color: #666;">{order['timestamp'][:10]}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No orders yet. Start ordering to build your history!")
    
    with col2:
        st.markdown("### 💬 Recent Feedback")
        feedbacks = memory.get_recent_feedbacks()
        
        if feedbacks:
            for fb in reversed(feedbacks):
                stars = "⭐" * int(fb['rating'])
                st.markdown(f"""
                <div class="dish-card">
                    <strong>{fb['dish_name']}</strong> {stars}<br>
                    <small>"{fb['feedback']}"</small><br>
                    <small style="color: #666;">{fb['timestamp'][:10]}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No feedback yet. Rate your orders to help us learn!")
    
    # Show consolidated feedback if exists
    if memory.memory.get('consolidated_feedback'):
        st.markdown("---")
        st.markdown("### 📋 Older Feedback Summary")
        with st.expander("View consolidated feedback"):
            st.text(memory.memory['consolidated_feedback'])


def show_database_tab():
    """Food database tab"""
    st.header("🗃️ Food Database")
    
    food_df = st.session_state.food_df
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(food_df)}</h2>
            <p>Total Dishes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        veg_count = len(food_df[food_df['dietary'] == 'Vegetarian'])
        st.markdown(f"""
        <div class="metric-card">
            <h2>{veg_count}</h2>
            <p>Vegetarian</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        cuisines = food_df['cuisine'].nunique()
        st.markdown(f"""
        <div class="metric-card">
            <h2>{cuisines}</h2>
            <p>Cuisines</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_price = food_df['price'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h2>₹{int(avg_price)}</h2>
            <p>Avg Price</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cuisine_filter = st.multiselect(
            "Cuisine",
            options=food_df['cuisine'].unique(),
            key="cuisine_filter"
        )
    
    with col2:
        dietary_filter = st.multiselect(
            "Dietary",
            options=food_df['dietary'].unique(),
            key="dietary_filter"
        )
    
    with col3:
        price_range = st.slider(
            "Price Range",
            int(food_df['price'].min()),
            int(food_df['price'].max()),
            (int(food_df['price'].min()), int(food_df['price'].max())),
            key="price_filter"
        )
    
    # Filter dataframe
    filtered_df = food_df.copy()
    
    if cuisine_filter:
        filtered_df = filtered_df[filtered_df['cuisine'].isin(cuisine_filter)]
    
    if dietary_filter:
        filtered_df = filtered_df[filtered_df['dietary'].isin(dietary_filter)]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) & 
        (filtered_df['price'] <= price_range[1])
    ]
    
    # Display
    st.markdown(f"### Showing {len(filtered_df)} dishes")
    
    # Display as cards
    for idx, row in filtered_df.iterrows():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            <div class="dish-card">
                <strong style="font-size: 1.1rem;">{row['dish_name']}</strong><br>
                <small style="color: #666;">{row['restaurant']} • {row['cuisine']}</small><br>
                <small>{row['description']}</small><br>
                <small>⭐ {row['rating']} • {row['dietary']} • Spice: {row['spice_level']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding-top: 1rem;">
                <h3 style="margin: 0;">₹{row['price']}</h3>
                <small>{row['prep_time_mins']} mins</small>
            </div>
            """, unsafe_allow_html=True)


def show_profile_tab():
    """User profile tab"""
    st.header("👤 Your Profile")
    
    memory = st.session_state.memory
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📈 Your Stats")
        
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(memory.memory['order_history'])}</h2>
            <p>Total Orders</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h2>{len(memory.memory['recent_feedbacks'])}</h2>
            <p>Recent Feedbacks</p>
        </div>
        """, unsafe_allow_html=True)
        
        if memory.memory['order_history']:
            total_spent = sum(order['price'] for order in memory.memory['order_history'])
            st.markdown(f"""
            <div class="metric-card">
                <h2>₹{total_spent}</h2>
                <p>Total Spent</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🎯 Your Preferences")
        
        preferences = memory.memory.get('preferences', {})
        
        if preferences:
            for key, value in preferences.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
        else:
            st.info("No preferences set yet. Keep ordering and rating to help us learn!")
        
        st.markdown("---")
        st.markdown("### 🧠 Memory Context")
        
        with st.expander("View full memory context"):
            st.text(memory.get_memory_context())


def main():
    """Main application"""
    initialize_session_state()
    load_system()
    
    # Header
    st.title("🍔 ZomatoAI Manager")
    st.markdown("*Your personalized food recommendation assistant powered by AI*")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Recommendations",
        "📊 History & Feedback",
        "🗃️ Food Database",
        "👤 Profile"
    ])
    
    with tab1:
        show_recommendation_tab()
    
    with tab2:
        show_history_tab()
    
    with tab3:
        show_database_tab()
    
    with tab4:
        show_profile_tab()


if __name__ == "__main__":
    main()
