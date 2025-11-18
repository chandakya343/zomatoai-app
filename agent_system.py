"""
ZomatoAI Agent Orchestration System
Uses XML-based function calling for agent coordination
"""

import google.generativeai as genai
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
import re
import os
import logging

# Get logger (no basicConfig - let Streamlit handle it)
logger = logging.getLogger(__name__)


class AgentSystem:
    """Orchestrates multiple AI agents for personalized food recommendations"""
    
    def __init__(self, api_key: str, food_df: pd.DataFrame):
        genai.configure(api_key=api_key)
        self.food_df = food_df
        
        # Initialize agents
        self.query_handler = self._create_query_handler()
        self.pandas_agent = self._create_pandas_agent()
        self.recommendation_agent = self._create_recommendation_agent()
    
    def _create_query_handler(self):
        """Create the main query handler agent"""
        system_prompt = """You are the Main Query Handler for ZomatoAI, a food recommendation system.

Your job is to analyze user queries and decide if we need to search the food database.

**When to search the database:**
- User asks about available dishes, restaurants, or cuisines
- User wants to explore new options
- User asks about specific types of food (e.g., "show me Chinese food", "what desserts do you have")
- User asks about price ranges, ratings, or dietary options
- User wants recommendations from the full menu

**When NOT to search database:**
- User is asking about their own order history or past feedback
- User is giving feedback on something they ordered
- General conversation or clarification questions
- User is asking about their preferences

**Output Format:**
If database search is needed, output a pandas query inside XML tags:
<pandas_query>
# Your pandas query here to filter the food_df DataFrame
# Use proper pandas syntax, available columns: dish_id, dish_name, restaurant, cuisine, category, price, rating, dietary, spice_level, prep_time_mins, tags, description
</pandas_query>

If NO database search needed, output:
<no_database_needed>
Proceed with user query and memory context only.
</no_database_needed>

**Available DataFrame columns:**
- dish_id, dish_name, restaurant, cuisine, category, price, rating, dietary, spice_level, prep_time_mins, tags, description

**Example queries you might generate:**
- food_df[food_df['cuisine'] == 'Chinese']
- food_df[(food_df['price'] < 200) & (food_df['dietary'] == 'Vegetarian')]
- food_df[food_df['category'] == 'Dessert'].nlargest(5, 'rating')
- food_df[food_df['spice_level'] == 'High']

Be concise and only output the XML tag with your decision."""

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 1024,
            },
        )
        
        chat = model.start_chat(history=[])
        chat.send_message(system_prompt)
        
        return chat
    
    def _create_pandas_agent(self):
        """Create the pandas query execution agent"""
        # This is more of a utility than a chat agent
        return None
    
    def _create_recommendation_agent(self):
        """Create the final recommendation agent"""
        system_prompt = """You are the Final Recommendation Agent for ZomatoAI.

Your role is to provide personalized food recommendations based on:
1. User's query/request
2. User's memory (order history, feedback, preferences)
3. Filtered food options (if database was searched)
4. Current time and context

**IMPORTANT: Always provide exactly TOP 5 recommendations ranked by relevance.**

**Format for each recommendation:**
1. **Dish Name - Restaurant (₹Price)**
   Brief explanation why this is recommended (1-2 sentences)

**Guidelines:**
- Be conversational and friendly
- Explain WHY you're recommending each dish based on their history
- Reference their past feedback when relevant
- If they liked/disliked something before, acknowledge it
- Consider their preferences and dietary restrictions
- ALWAYS suggest exactly 5 specific dishes (or all available if less than 5)
- Rank them by relevance (most relevant first)
- Mention price and restaurant name for each
- Encourage them to provide feedback after ordering

**Tone:**
- Warm and helpful
- Personal (use their history to make it feel customized)
- Enthusiastic but not pushy

Always end by encouraging feedback: "Let me know how you like it! The more feedback you share, the better I can personalize recommendations for you."

Keep responses well-structured with numbered list of 5 recommendations."""

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash-lite",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 2048,
            },
        )
        
        chat = model.start_chat(history=[])
        chat.send_message(system_prompt)
        
        return chat
    
    def _extract_xml_content(self, text: str, tag: str) -> Optional[str]:
        """Extract content from XML tags"""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        
        start_idx = text.find(start_tag)
        end_idx = text.find(end_tag)
        
        if start_idx != -1 and end_idx != -1:
            start_idx += len(start_tag)
            return text[start_idx:end_idx].strip()
        
        return None
    
    def _execute_pandas_query(self, query: str) -> pd.DataFrame:
        """Execute a pandas query safely"""
        try:
            # Create a safe execution environment
            food_df = self.food_df
            
            # Clean up the query
            query = query.strip()
            if query.startswith('#'):
                # Remove comment lines
                query = '\n'.join([line for line in query.split('\n') if not line.strip().startswith('#')])
            
            # Execute the query
            result = eval(query, {"food_df": food_df, "pd": pd})
            
            if isinstance(result, pd.DataFrame):
                return result
            else:
                # If result is not a DataFrame, return empty
                return pd.DataFrame()
        
        except Exception as e:
            print(f"Error executing pandas query: {e}")
            print(f"Query was: {query}")
            return pd.DataFrame()
    
    def _format_filtered_data(self, df: pd.DataFrame) -> str:
        """Format filtered DataFrame for LLM context"""
        if df.empty:
            return "No matching dishes found in database."
        
        formatted = f"Found {len(df)} matching dishes:\n\n"
        
        for idx, row in df.iterrows():
            formatted += f"**{row['dish_name']}** - {row['restaurant']}\n"
            formatted += f"  Cuisine: {row['cuisine']} | Category: {row['category']}\n"
            formatted += f"  Price: ₹{row['price']} | Rating: {row['rating']}/5\n"
            formatted += f"  Dietary: {row['dietary']} | Spice: {row['spice_level']}\n"
            formatted += f"  Description: {row['description']}\n"
            formatted += f"  Tags: {', '.join(eval(row['tags']) if isinstance(row['tags'], str) else row['tags'])}\n\n"
        
        return formatted
    
    def process_query(self, user_query: str, memory_context: str) -> Tuple[str, Dict[str, Any]]:
        """
        Main orchestration method
        Returns: (final_response, debug_info)
        """
        logger.info("="*80)
        logger.info("🚀 PROCESSING NEW QUERY")
        logger.info("="*80)
        logger.info(f"📝 User Query: {user_query}")
        
        debug_info = {
            "query": user_query,
            "timestamp": datetime.now().isoformat(),
            "database_searched": False,
            "filtered_dishes_count": 0
        }
        
        # Step 1: Query Handler decides if we need database
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        handler_input = f"""Current Time: {current_time}

User Query: {user_query}

User Memory Context:
{memory_context}

Analyze the query and decide if we need to search the food database."""

        logger.info("🤖 Sending to Query Handler Agent...")
        try:
            handler_response = self.query_handler.send_message(handler_input)
            # Validate response
            if handler_response is None or not hasattr(handler_response, 'text'):
                logger.error("❌ API returned invalid response")
                return "Sorry, I couldn't process your query. Please try again.", debug_info
            
            handler_text = handler_response.text
            logger.info("✅ Query Handler Response:")
            logger.info(f"   {handler_text[:200]}...")
        except Exception as e:
            logger.error(f"❌ Query Handler Error: {e}")
            return f"Sorry, an error occurred: {str(e)}", debug_info
        
        debug_info["handler_response"] = handler_text
        
        # Step 2: Check if we need database search
        pandas_query = self._extract_xml_content(handler_text, "pandas_query")
        no_db_needed = self._extract_xml_content(handler_text, "no_database_needed")
        
        logger.info("🔍 Checking for database search...")
        
        filtered_data_context = ""
        
        if pandas_query:
            logger.info("✅ Database search needed!")
            logger.info(f"🐼 Pandas Query: {pandas_query}")
            
            # Execute pandas query
            debug_info["database_searched"] = True
            debug_info["pandas_query"] = pandas_query
            
            filtered_df = self._execute_pandas_query(pandas_query)
            debug_info["filtered_dishes_count"] = len(filtered_df)
            
            logger.info(f"📊 Found {len(filtered_df)} matching dishes")
            
            filtered_data_context = self._format_filtered_data(filtered_df)
            debug_info["filtered_data_preview"] = filtered_data_context[:500]
        else:
            logger.info("⏭️  No database search needed (using memory only)")
        
        # Step 3: Generate final recommendation
        recommendation_input = f"""Current Time: {current_time}

User Query: {user_query}

User Memory Context:
{memory_context}

"""
        
        if filtered_data_context:
            recommendation_input += f"\nAvailable Dishes (from database search):\n{filtered_data_context}"
        
        recommendation_input += "\n\nProvide your personalized recommendation:"
        
        logger.info("🎯 Sending to Recommendation Agent...")
        logger.info(f"   Input length: {len(recommendation_input)} chars")
        
        try:
            final_response = self.recommendation_agent.send_message(recommendation_input)
            # Validate response
            if final_response is None or not hasattr(final_response, 'text'):
                logger.error("❌ API returned invalid response")
                return "Sorry, I couldn't generate recommendations at this moment. Please try again.", debug_info
            
            final_text = final_response.text
            logger.info("✅ Recommendation Agent Response:")
            logger.info(f"   Response length: {len(final_text)} chars")
            logger.info(f"   First 200 chars: {final_text[:200]}...")
        except Exception as e:
            logger.error(f"❌ Recommendation Agent Error: {e}")
            return f"Sorry, an error occurred: {str(e)}", debug_info
        
        debug_info["final_response"] = final_text
        
        logger.info("="*80)
        logger.info("✅ QUERY PROCESSING COMPLETE")
        logger.info("="*80)
        
        return final_text, debug_info


def test_agent_system():
    """Test the agent system"""
    import os
    from food_database import get_food_database
    from memory_system import create_sample_user
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Please set GEMINI_API_KEY environment variable")
        return
    
    # Load data
    food_df = get_food_database()
    memory = create_sample_user()
    
    # Create agent system
    agent_system = AgentSystem(api_key, food_df)
    
    # Test queries
    test_queries = [
        "What vegetarian dishes do you have under ₹200?",
        "I'm craving something spicy today",
        "Show me all desserts",
    ]
    
    for query in test_queries:
        print("\n" + "="*60)
        print(f"QUERY: {query}")
        print("="*60)
        
        response, debug = agent_system.process_query(
            query,
            memory.get_memory_context()
        )
        
        print(f"\nRESPONSE:\n{response}")
        print(f"\nDatabase searched: {debug['database_searched']}")
        if debug['database_searched']:
            print(f"Found {debug['filtered_dishes_count']} dishes")


if __name__ == "__main__":
    test_agent_system()

