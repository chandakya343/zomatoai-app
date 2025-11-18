"""
Zomato Food Database
Contains sample data of available dishes across restaurants
"""

import pandas as pd
import json
from pathlib import Path

def create_food_database():
    """Create a pandas DataFrame with Zomato food data"""
    
    foods_data = [
        {
            "dish_id": "D001",
            "dish_name": "Butter Chicken",
            "restaurant": "Punjab Grill",
            "cuisine": "North Indian",
            "category": "Main Course",
            "price": 380,
            "rating": 4.5,
            "dietary": "Non-Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 25,
            "tags": ["Creamy", "Popular", "Rich"],
            "description": "Tender chicken in rich tomato-butter gravy"
        },
        {
            "dish_id": "D002",
            "dish_name": "Paneer Tikka Masala",
            "restaurant": "Punjab Grill",
            "cuisine": "North Indian",
            "category": "Main Course",
            "price": 320,
            "rating": 4.4,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 20,
            "tags": ["Creamy", "Popular", "Protein-Rich"],
            "description": "Grilled cottage cheese in spiced tomato gravy"
        },
        {
            "dish_id": "D003",
            "dish_name": "Margherita Pizza",
            "restaurant": "Pizza Hub",
            "cuisine": "Italian",
            "category": "Main Course",
            "price": 280,
            "rating": 4.3,
            "dietary": "Vegetarian",
            "spice_level": "None",
            "prep_time_mins": 18,
            "tags": ["Cheesy", "Classic", "Quick"],
            "description": "Classic pizza with mozzarella and basil"
        },
        {
            "dish_id": "D004",
            "dish_name": "Chicken Biryani",
            "restaurant": "Biryani Blues",
            "cuisine": "Hyderabadi",
            "category": "Main Course",
            "price": 350,
            "rating": 4.7,
            "dietary": "Non-Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 30,
            "tags": ["Aromatic", "Filling", "Traditional"],
            "description": "Fragrant basmati rice with tender chicken"
        },
        {
            "dish_id": "D005",
            "dish_name": "Veg Hakka Noodles",
            "restaurant": "Wok Express",
            "cuisine": "Chinese",
            "category": "Main Course",
            "price": 180,
            "rating": 4.2,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 15,
            "tags": ["Quick", "Light", "Stir-Fried"],
            "description": "Stir-fried noodles with vegetables"
        },
        {
            "dish_id": "D006",
            "dish_name": "Masala Dosa",
            "restaurant": "South Spice",
            "cuisine": "South Indian",
            "category": "Main Course",
            "price": 120,
            "rating": 4.6,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 20,
            "tags": ["Crispy", "Traditional", "Healthy"],
            "description": "Crispy rice crepe with spiced potato filling"
        },
        {
            "dish_id": "D007",
            "dish_name": "Chicken Fried Rice",
            "restaurant": "Wok Express",
            "cuisine": "Chinese",
            "category": "Main Course",
            "price": 220,
            "rating": 4.3,
            "dietary": "Non-Vegetarian",
            "spice_level": "Low",
            "prep_time_mins": 15,
            "tags": ["Quick", "Filling", "Savory"],
            "description": "Stir-fried rice with chicken and vegetables"
        },
        {
            "dish_id": "D008",
            "dish_name": "Chocolate Brownie",
            "restaurant": "Dessert Dreams",
            "cuisine": "Continental",
            "category": "Dessert",
            "price": 150,
            "rating": 4.5,
            "dietary": "Vegetarian",
            "spice_level": "None",
            "prep_time_mins": 10,
            "tags": ["Sweet", "Chocolatey", "Indulgent"],
            "description": "Rich chocolate brownie with ice cream"
        },
        {
            "dish_id": "D009",
            "dish_name": "Caesar Salad",
            "restaurant": "Healthy Bites",
            "cuisine": "Continental",
            "category": "Appetizer",
            "price": 200,
            "rating": 4.1,
            "dietary": "Non-Vegetarian",
            "spice_level": "None",
            "prep_time_mins": 10,
            "tags": ["Healthy", "Fresh", "Light"],
            "description": "Crisp romaine with Caesar dressing and chicken"
        },
        {
            "dish_id": "D010",
            "dish_name": "Gulab Jamun",
            "restaurant": "Sweet Tooth",
            "cuisine": "Indian",
            "category": "Dessert",
            "price": 80,
            "rating": 4.4,
            "dietary": "Vegetarian",
            "spice_level": "None",
            "prep_time_mins": 5,
            "tags": ["Sweet", "Traditional", "Popular"],
            "description": "Deep-fried milk balls in sugar syrup"
        },
        {
            "dish_id": "D011",
            "dish_name": "Fish Curry",
            "restaurant": "Coastal Kitchen",
            "cuisine": "Coastal",
            "category": "Main Course",
            "price": 400,
            "rating": 4.6,
            "dietary": "Non-Vegetarian",
            "spice_level": "High",
            "prep_time_mins": 25,
            "tags": ["Spicy", "Tangy", "Traditional"],
            "description": "Fresh fish in coconut-based spicy curry"
        },
        {
            "dish_id": "D012",
            "dish_name": "Veg Burger",
            "restaurant": "Burger Town",
            "cuisine": "American",
            "category": "Main Course",
            "price": 150,
            "rating": 4.0,
            "dietary": "Vegetarian",
            "spice_level": "Low",
            "prep_time_mins": 12,
            "tags": ["Quick", "Filling", "Casual"],
            "description": "Vegetable patty with fresh veggies and sauces"
        },
        {
            "dish_id": "D013",
            "dish_name": "Chole Bhature",
            "restaurant": "Punjabi Zaika",
            "cuisine": "North Indian",
            "category": "Main Course",
            "price": 140,
            "rating": 4.5,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 20,
            "tags": ["Filling", "Traditional", "Popular"],
            "description": "Spicy chickpea curry with fried bread"
        },
        {
            "dish_id": "D014",
            "dish_name": "Pad Thai",
            "restaurant": "Thai Basil",
            "cuisine": "Thai",
            "category": "Main Course",
            "price": 320,
            "rating": 4.4,
            "dietary": "Non-Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 20,
            "tags": ["Tangy", "Sweet", "Exotic"],
            "description": "Stir-fried rice noodles with shrimp and peanuts"
        },
        {
            "dish_id": "D015",
            "dish_name": "Idli Sambar",
            "restaurant": "South Spice",
            "cuisine": "South Indian",
            "category": "Main Course",
            "price": 100,
            "rating": 4.5,
            "dietary": "Vegetarian",
            "spice_level": "Low",
            "prep_time_mins": 15,
            "tags": ["Healthy", "Light", "Traditional"],
            "description": "Steamed rice cakes with lentil soup"
        },
        {
            "dish_id": "D016",
            "dish_name": "Chicken Wings",
            "restaurant": "Wings & Things",
            "cuisine": "American",
            "category": "Appetizer",
            "price": 280,
            "rating": 4.3,
            "dietary": "Non-Vegetarian",
            "spice_level": "High",
            "prep_time_mins": 18,
            "tags": ["Spicy", "Crispy", "Popular"],
            "description": "Crispy chicken wings with hot sauce"
        },
        {
            "dish_id": "D017",
            "dish_name": "Paneer Wrap",
            "restaurant": "Quick Bites",
            "cuisine": "Fusion",
            "category": "Main Course",
            "price": 160,
            "rating": 4.2,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 10,
            "tags": ["Quick", "Filling", "Portable"],
            "description": "Grilled paneer with veggies in wrap"
        },
        {
            "dish_id": "D018",
            "dish_name": "Mutton Rogan Josh",
            "restaurant": "Kashmir Kitchen",
            "cuisine": "Kashmiri",
            "category": "Main Course",
            "price": 450,
            "rating": 4.7,
            "dietary": "Non-Vegetarian",
            "spice_level": "High",
            "prep_time_mins": 35,
            "tags": ["Rich", "Aromatic", "Premium"],
            "description": "Tender mutton in aromatic red curry"
        },
        {
            "dish_id": "D019",
            "dish_name": "Mango Lassi",
            "restaurant": "Lassi Corner",
            "cuisine": "Indian",
            "category": "Beverage",
            "price": 80,
            "rating": 4.6,
            "dietary": "Vegetarian",
            "spice_level": "None",
            "prep_time_mins": 5,
            "tags": ["Refreshing", "Sweet", "Cooling"],
            "description": "Yogurt-based mango drink"
        },
        {
            "dish_id": "D020",
            "dish_name": "Veg Thali",
            "restaurant": "Rajdhani Thali",
            "cuisine": "Rajasthani",
            "category": "Main Course",
            "price": 300,
            "rating": 4.6,
            "dietary": "Vegetarian",
            "spice_level": "Medium",
            "prep_time_mins": 25,
            "tags": ["Complete Meal", "Variety", "Traditional"],
            "description": "Complete meal with dal, vegetables, roti, rice, dessert"
        }
    ]
    
    df = pd.DataFrame(foods_data)
    return df

def save_database_to_csv(df, filepath="food_database.csv"):
    """Save the database to CSV"""
    df.to_csv(filepath, index=False)
    print(f"Database saved to {filepath}")

def load_database_from_csv(filepath="food_database.csv"):
    """Load database from CSV"""
    return pd.read_csv(filepath)

def get_food_database():
    """Get the food database, creating it if it doesn't exist"""
    db_path = Path(__file__).parent / "food_database.csv"
    
    if db_path.exists():
        return load_database_from_csv(db_path)
    else:
        df = create_food_database()
        save_database_to_csv(df, db_path)
        return df

if __name__ == "__main__":
    # Create and save the database
    df = create_food_database()
    save_database_to_csv(df)
    print(f"\nCreated database with {len(df)} dishes")
    print(f"\nSample data:")
    print(df.head())
    print(f"\nColumns: {list(df.columns)}")

