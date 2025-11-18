# 🍔 ZomatoAI Manager

An intelligent food recommendation system with personalized memory management. This Streamlit app showcases AI-powered food discovery using multi-agent orchestration and contextual memory.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized AI agents work together to provide personalized recommendations
- **Smart Memory System**: Tracks user preferences and order history
- **Natural Language Queries**: Ask for food recommendations in plain English
- **Personalized Results**: Gets smarter with each interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd zomatoai-app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Run the app:**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
zomatoai-app/
├── app.py                 # Main Streamlit application
├── agent_system.py        # Multi-agent orchestration system
├── food_database.py       # Food database management
├── memory_system.py       # User memory and preference tracking
├── food_database.csv      # Sample food data
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── user_data/            # User memory storage
└── README.md             # This file
```

## 🎨 Usage

1. **Ask for recommendations**: Type natural language queries like:
   - "Show me vegetarian dishes under ₹200"
   - "I want something spicy"
   - "What are the best rated Chinese dishes?"

2. **Provide feedback**: Rate dishes and provide feedback to improve future recommendations

3. **View your preferences**: Check the Memory tab to see what the system has learned about you

## 🏗️ Architecture

- **Query Handler Agent**: Analyzes user queries and decides when to search the database
- **Database Filter**: Filters dishes based on user criteria
- **Memory System**: Maintains active and permanent memory of user preferences
- **Recommendation Agent**: Generates personalized top 5 recommendations

## 📝 Notes

- The app uses a sample food database. In production, this would connect to Zomato's API
- User memory is stored locally in JSON files
- The system learns from user feedback to improve recommendations over time

## 🔧 Configuration

Edit `.env` to configure:
- `GEMINI_API_KEY`: Your Google Gemini API key

## 📄 License

Built for demonstration purposes.

