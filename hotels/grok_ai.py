import os
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ✅ Load .env (works locally and on Render)
load_dotenv()

def initialize_groq():
    """Initialize Groq AI configuration from environment variables."""
    return {
        "api_key": os.getenv("GROQ_API_KEY"),
        "model": os.getenv("GROQ_MODEL_NAME", "llama-3.1-8b-instant"),
        "url": os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    }

def generate_trip_plan(destination, duration, activities, companions, start_date,
                       origin_location=None, transportation_mode=None):
    """Generate a personalized trip plan using Groq AI."""
    config = initialize_groq()

    # ✅ Check API key before calling
    if not config["api_key"]:
        raise Exception("GROQ_API_KEY not found. Please set it in Render Environment Variables.")

    # ✅ Format trip duration
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = start + timedelta(days=duration - 1)
    end_date = end.strftime('%Y-%m-%d')

    # ✅ Optional travel info
    travel_info = ""
    if origin_location and transportation_mode:
        travel_info = f"""
        Travel Information:
        - Starting from: {origin_location}
        - Transportation mode: {transportation_mode}
        """

    # ✅ Prompt to send to Groq API
    prompt = f"""
    Create a personalized {duration}-day travel plan for {destination} 
    from {start_date} to {end_date} for a {companions} trip.

    Focus on these activities: {activities}.
    {travel_info}

    Please include:
    1. A short introduction about {destination}.
    2. A detailed day-by-day itinerary (Morning, Afternoon, Evening).
    3. Top attractions (at least 3) with brief descriptions.
    4. Restaurant recommendations.
    5. Travel tips (at least 2 practical suggestions).
    6. Cost Estimation section:
       - Estimated travel cost, food, stay, and activities.
       - Format cost section in <div class="cost-estimation">.
    Use HTML tags (<h1>, <h2>, <ul>, <p>) for clean display.
    """

    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.7
    }

    # ✅ Function to call Groq API
    def call_api():
        try:
            response = requests.post(
                config["url"],
                headers=headers,
                json=payload,
                timeout=40
            )
            response.raise_for_status()
            result = response.json()

            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"]

            raise Exception("No response content received from Groq API")

        except requests.exceptions.RequestException as e:
            print(f"[Groq API] Request Error: {e}")
            raise Exception(f"Groq API request failed: {str(e)}")

        except Exception as e:
            print(f"[Groq API] Error: {e}")
            raise

    # ✅ Use thread executor for timeout handling
    with ThreadPoolExecutor() as executor:
        try:
            future = executor.submit(call_api)
            return future.result(timeout=45)
        except TimeoutError:
            raise TimeoutError("Groq API call timed out after 45 seconds")
        except Exception as e:
            print(f"[Groq API] Unexpected Error: {e}")
            raise
