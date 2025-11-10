🌍 AI Trip Planner & Hotel Booking System

An intelligent AI-powered travel planner and hotel booking web application built with Django, Groq AI, and Razorpay.
This platform allows users to plan personalized trips, book hotels, and get cost estimations with an AI-generated itinerary — all in one place.

🚀 Live Demo: https://ai-trip-planner-grok-farhan.onrender.com

🧠 Powered by: Groq AI (LLaMA 3.1 Model)
💳 Payment Gateway: Razorpay Integration
🗺️ Maps: Folium Interactive Maps
📦 Backend Framework: Django 5.2

🧩 Features
🌐 Core Functionality

✅ AI Trip Planning

Generates a personalized multi-day itinerary using Groq AI (LLaMA 3.1).

Includes attractions, restaurants, travel tips, and detailed cost estimation.

Supports parameters like:

Destination

Trip duration

Activities

Travel companions

Origin & transportation mode

✅ Hotel Booking

Browse hotels near each destination.

Book hotels securely using Razorpay Payment Gateway.

Auto-updates user’s booking history.

✅ User Authentication

Custom user login and registration system.

Travel history saved to user profile.

✅ Interactive Maps

Uses Folium + Leaflet.js to display:

Hotels near a place.

Transportation options.

Location maps for attractions.

✅ Dynamic Cost Estimation

AI estimates daily and total trip budgets.

Includes categories like stay, food, transport, and activities.

✅ AI Integration via Groq API

Uses LLaMA 3.1 model for fast, natural-language trip generation.

Environment variables securely configured via .env.

✅ Responsive Frontend

Built with Bootstrap.

Includes trip planning forms, maps, and modern UI.

🧠 Tech Stack
Category	Technology
Frontend	HTML5, CSS3, JavaScript, Bootstrap
Backend	Django 5.2 (Python 3.13)
AI Model	Groq LLaMA 3.1 via Groq API
Database	SQLite3
Payment Gateway	Razorpay
Maps & Geo	Folium (Leaflet.js)
Deployment	Render
Env Management	python-dotenv
REST API	Django REST Framework
⚙️ Installation Guide
1️⃣ Clone the Repository
git clone https://github.com/farhanAhmed113/AI-Trip-Planner-Grok-farhan.git
cd AI-Trip-Planner-Grok-farhan

2️⃣ Create and Activate Virtual Environment
python -m venv venv
venv\Scripts\activate   # For Windows
# or
source venv/bin/activate  # For Mac/Linux

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Create .env File (in project root)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL_NAME=llama-3.1-8b-instant
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions

RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

5️⃣ Run Database Migrations
python manage.py migrate

6️⃣ Start Development Server
python manage.py runserver


Visit → http://127.0.0.1:8000

🧾 Key Project Files
File	Description
TravelandHotelBooking/settings.py	Django project settings (loads .env variables securely)
hotels/grok_ai.py	Groq AI integration for generating personalized itineraries
hotels/views.py	Core logic for trip planning, hotel booking, Razorpay, etc.
templates/	Contains all HTML templates (home, trip planner, contact, etc.)
Procfile	Configures Render to run Gunicorn server
requirements.txt	Python dependencies for deployment
.env	Contains API keys (not pushed to GitHub)
🧭 Main URLs
Page	Description	Example
/	Home page showing destinations	🏠
/trip/	AI trip planner	✈️
/hotels/<id>/	Hotel details & booking page	🏨
/about/	About page	ℹ️
/contact/	Contact form	📬
🔐 Environment Variables
Variable	Description
GROQ_API_KEY	Your Groq API key
GROQ_MODEL_NAME	AI model (default: llama-3.1-8b-instant)
GROQ_API_URL	API endpoint
RAZORPAY_KEY_ID	Razorpay public key
RAZORPAY_KEY_SECRET	Razorpay secret key
🧮 AI Prompt Example

Example of how the AI generates the plan (in grok_ai.py):

prompt = f"""
Create a personalized {duration}-day trip itinerary for {destination}.
Include attractions, restaurants, local tips, and cost estimation.
Format the result in HTML with sections for each day.
"""

🧰 Deployment (Render)

Render Configuration:

Runtime: Python 3

Build Command:

pip install -r requirements.txt


Start Command:

gunicorn TravelandHotelBooking.wsgi


Environment Variables in Render:

GROQ_API_KEY=your_groq_key
GROQ_MODEL_NAME=llama-3.1-8b-instant
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

📸 Screenshots (optional to add)

🏠 Home Page

✈️ Trip Planner Form

🧭 AI Itinerary Output

💳 Razorpay Payment Page

🗺️ Map View with Hotels

👨‍💻 Author

👤 Farhan Ahmed
💼 Final Year Engineering Student | Full Stack Developer
📧 farhanfreefire10@gmail.com

🌐 GitHub Profile = https://github.com/farhanAhmed113

🏁 License

This project is licensed under the MIT License.
You’re free to use, modify, and distribute with proper credit.