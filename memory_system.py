"""
Simplified Memory System for ZomatoAI Manager
Keeps last 10 feedbacks in detail and consolidates older ones
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import google.generativeai as genai


class MemorySystem:
    """Manages user order history, preferences, and feedback"""
    
    def __init__(self, user_id: str, data_dir: str = "user_data"):
        self.user_id = user_id
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.user_file = self.data_dir / f"{user_id}_memory.json"
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict[str, Any]:
        """Load user memory from file"""
        if self.user_file.exists():
            with open(self.user_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "user_id": self.user_id,
                "order_history": [],
                "recent_feedbacks": [],  # Last 10 feedbacks in detail
                "consolidated_feedback": "",  # Summary of older feedbacks
                "preferences": {},
                "created_at": datetime.now().isoformat()
            }
    
    def _save_memory(self):
        """Save memory to file"""
        with open(self.user_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def add_order(self, dish_id: str, dish_name: str, restaurant: str, 
                  price: float, timestamp: str = None):
        """Add an order to history"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        order = {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "restaurant": restaurant,
            "price": price,
            "timestamp": timestamp
        }
        
        self.memory["order_history"].append(order)
        self._save_memory()
    
    def add_feedback(self, dish_id: str, dish_name: str, feedback: str, 
                     rating: float, timestamp: str = None):
        """Add feedback and maintain last 10 feedbacks"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        feedback_entry = {
            "dish_id": dish_id,
            "dish_name": dish_name,
            "feedback": feedback,
            "rating": rating,
            "timestamp": timestamp
        }
        
        # Add to recent feedbacks
        self.memory["recent_feedbacks"].append(feedback_entry)
        
        # If we have more than 10, consolidate the oldest
        if len(self.memory["recent_feedbacks"]) > 10:
            self._consolidate_oldest_feedback()
        
        self._save_memory()
    
    def _consolidate_oldest_feedback(self):
        """Consolidate oldest feedback when we exceed 10"""
        # Remove the oldest feedback from recent
        oldest = self.memory["recent_feedbacks"].pop(0)
        
        # Add to consolidated summary
        summary_addition = (
            f"• {oldest['dish_name']}: {oldest['feedback']} "
            f"(Rating: {oldest['rating']}/5) - {oldest['timestamp'][:10]}"
        )
        
        if self.memory["consolidated_feedback"]:
            self.memory["consolidated_feedback"] += "\n" + summary_addition
        else:
            self.memory["consolidated_feedback"] = "Older Feedback Summary:\n" + summary_addition
    
    def get_memory_context(self) -> str:
        """Get formatted memory context for LLM"""
        context_parts = []
        
        # User preferences
        if self.memory.get("preferences"):
            context_parts.append("User Preferences:")
            for key, value in self.memory["preferences"].items():
                context_parts.append(f"  - {key}: {value}")
        
        # Order history summary
        if self.memory["order_history"]:
            context_parts.append(f"\nOrder History (Total: {len(self.memory['order_history'])} orders):")
            # Show last 5 orders
            recent_orders = self.memory["order_history"][-5:]
            for order in recent_orders:
                context_parts.append(
                    f"  - {order['dish_name']} from {order['restaurant']} "
                    f"on {order['timestamp'][:10]}"
                )
        
        # Recent feedbacks (last 10)
        if self.memory["recent_feedbacks"]:
            context_parts.append(f"\nRecent Feedback (Last {len(self.memory['recent_feedbacks'])} items):")
            for fb in self.memory["recent_feedbacks"]:
                context_parts.append(
                    f"  - {fb['dish_name']}: {fb['feedback']} "
                    f"(Rating: {fb['rating']}/5) - {fb['timestamp'][:10]}"
                )
        
        # Consolidated older feedback
        if self.memory["consolidated_feedback"]:
            context_parts.append(f"\n{self.memory['consolidated_feedback']}")
        
        return "\n".join(context_parts) if context_parts else "No previous history."
    
    def update_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences"""
        self.memory["preferences"].update(preferences)
        self._save_memory()
    
    def get_order_history(self) -> List[Dict]:
        """Get full order history"""
        return self.memory["order_history"]
    
    def get_recent_feedbacks(self) -> List[Dict]:
        """Get recent feedbacks"""
        return self.memory["recent_feedbacks"]


def create_sample_user():
    """Create a sample user with order history and feedback"""
    memory = MemorySystem("user_demo_001")
    
    # Add some sample orders and feedback
    sample_data = [
        {
            "dish_id": "D004",
            "dish_name": "Chicken Biryani",
            "restaurant": "Biryani Blues",
            "price": 350,
            "feedback": "Absolutely loved it! The spices were perfect and chicken was tender.",
            "rating": 5.0
        },
        {
            "dish_id": "D006",
            "dish_name": "Masala Dosa",
            "restaurant": "South Spice",
            "price": 120,
            "feedback": "Crispy and delicious, but could use more potato filling.",
            "rating": 4.0
        },
        {
            "dish_id": "D001",
            "dish_name": "Butter Chicken",
            "restaurant": "Punjab Grill",
            "price": 380,
            "feedback": "Too creamy for my taste, felt heavy.",
            "rating": 3.0
        },
        {
            "dish_id": "D005",
            "dish_name": "Veg Hakka Noodles",
            "restaurant": "Wok Express",
            "price": 180,
            "feedback": "Quick and tasty, perfect for a light meal.",
            "rating": 4.5
        },
        {
            "dish_id": "D008",
            "dish_name": "Chocolate Brownie",
            "restaurant": "Dessert Dreams",
            "price": 150,
            "feedback": "Rich and decadent! Perfect dessert.",
            "rating": 5.0
        },
    ]
    
    for item in sample_data:
        memory.add_order(
            item["dish_id"],
            item["dish_name"],
            item["restaurant"],
            item["price"]
        )
        memory.add_feedback(
            item["dish_id"],
            item["dish_name"],
            item["feedback"],
            item["rating"]
        )
    
    # Add preferences
    memory.update_preferences({
        "dietary": "Non-Vegetarian",
        "spice_preference": "Medium to High",
        "cuisine_favorites": ["Biryani", "South Indian", "Chinese"],
        "budget_range": "₹150-400 per dish"
    })
    
    return memory


if __name__ == "__main__":
    # Create sample user
    memory = create_sample_user()
    print("Sample user created!")
    print("\n" + "="*50)
    print("MEMORY CONTEXT:")
    print("="*50)
    print(memory.get_memory_context())

