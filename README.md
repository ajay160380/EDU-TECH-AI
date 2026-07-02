# 🎓 EduTech AI - AI-Powered Interactive Course & Learning Workspace

<p align="center">
  <img src="static/images/logo_e3.png" alt="EduTech AI Logo" width="120" style="border-radius: 50%; box-shadow: 0 10px 30px rgba(0,0,0,0.3); border: 3px solid #2563eb;" />
</p>

<h3 align="center">Distraction-Free Video Classrooms • Intelligent AI Tutoring • Zen Focus Pomodoros • Dynamic Credentials</h3>

<p align="center">
  <a href="https://github.com/ajay160380/Edu-Tech-AI"><img src="https://img.shields.io/badge/Django-6.0.5-092e20?style=for-the-badge&logo=django" alt="Django" /></a>
  <a href="https://github.com/ajay160380/Edu-Tech-AI"><img src="https://img.shields.io/badge/Python-3.12+-3776ab?style=for-the-badge&logo=python" alt="Python" /></a>
  <a href="https://edu-tech-ai-vk2e.onrender.com"><img src="https://img.shields.io/badge/Live_Deploy-Render-success?style=for-the-badge&logo=render&color=00c2cb" alt="Render" /></a>
</p>

***

### 🌐 Live Websites: 
- **Render (🔥 MAIN PRODUCTION)**: [edu-tech-ai-vk2e.onrender.com](https://edu-tech-ai-vk2e.onrender.com)
  *(This is the official live website. It is securely connected to our permanent cloud Neon PostgreSQL Database.)*
- **PythonAnywhere (🧪 TESTING ONLY)**: [ajay160380.pythonanywhere.com](https://ajay160380.pythonanywhere.com/)
  *(This link is used for testing features locally on a temporary SQLite database. Data here is not synced with the main production server.)*

**EduTech AI** is a premium, high-fidelity EdTech SaaS platform that turns standard YouTube educational playlists into comprehensive, interactive virtual classrooms. Utilizing advanced Language Models and interactive UI overlays, it acts as an automated study companion, offering textbook-level summaries, custom-tailored study plans, smart interactive quizzes, a focused Pomodoro study room, and automated grading systems with dynamic PDF certificate generation on exam completion.

---

## ⚡ 🌟 Key System Features

### 🎬 1. Dynamic Course Syllabus Parser
*   **Zero-Overhead Parsing**: Simply supply any public YouTube playlist URL or ID; the platform instantly grabs metadata, thumbnail assets, and video configurations.
*   **Scalability Optimized**: Handles complex, high-volume playlists (supporting **500+ videos** seamlessly via pagination and responsive scrolling).
*   **Procedural Mock Fallback**: If YouTube APIs are unreachable or offline, the platform triggers a procedural mock engine that generates rich study curricula instantly.

### 🤖 2. Advanced AI Study Buddy & Lecture Summarizer
*   **Llama-3.1-8B Powered**: Connects to the Groq API to compile textbook-level study summaries, architectural flowcharts, and custom code blueprints.
*   **Multi-Tier Customization**: Tailors the complexity and details of the summaries and quizzes dynamically according to the user's active tier (`Free`, `Pro`, or `Ultra`).
*   **Resilient Fallbacks**: If API limits or credentials fail, it gracefully shifts to Pollinations AI or a keyword-matched Smart Offline NLP Mock.

### 🗣️ 3. Conversational Hinglish Tutor
*   **Natural Understanding**: Uses a custom translation module to convert complex academic topics into natural, highly engaging **Hinglish** (Hindi written in Roman script) for better comprehension and conceptual grounding.
*   **Plan Exclusive**: Made dynamically accessible for Ultra Tier subscribers to ensure highly premium localized learning.

### ⏱️ 4. AI Focus Room & Draggable Zen Bar
*   **Integrated Pomodoro Timer**: A completely distraction-free, beautifully animated study environment with customizable focus periods and real-time study session logging.
*   **Draggable Zen Glassmorphism Overlay**: A custom tactile HUD with viewport collision boundary detection, active drag transition suppression, and local-storage coordinate persistence.
*   **High-Score Streaks**: Bumps user streaks dynamically on session completions to gamify consistent study habits.

### 📜 5. Verified Credentials & Public Gateway
*   **Dynamic Certification Engine**: Renders elegant, high-fidelity PDF graduation certificates with customized completion details and verification IDs.
*   **Public Verification Gateway (`/certificate/verify/<credential_id>/`)**: A fully public gateway that allows recruiters or external organizations to verify the student's mastery badge, complete with guest sign-up banners and shareable links for LinkedIn.

### 💳 6. Sandbox Razorpay Payments
*   **Multi-Tier Subscription Portal**: Free, Pro, and Ultra plan selections with Razorpay REST SDK payment callback verification.
*   **Simulated Checkout Fallback**: Automatically activates a secure mock payment flow if API credentials are in sandbox/dummy mode to ensure uninterrupted onboarding testing.

---

## 🛠️ Advanced Tech Stack

| Technology Layer | Tool / Library Used |
| :--- | :--- |
| **Backend Framework** | Django 6.0.5 (Python 3.12+) |
| **Database** | SQLite3 (Fully migrated and optimized with django signals) |
| **AI Processing** | Groq Llama-3.1-8B-Instant API (with Pollinations AI fallbacks) |
| **Authentication** | Firebase Frontend SDK & Firebase Admin SDK (OAuth 2.0 with Google) |
| **Static Assets** | WhiteNoise Middleware (Compressed & cached static assets serving) |
| **Styling & UI** | Vanilla CSS3 (Custom theme variables, Cyberpunk neon designs, glassmorphism HUDs) |
| **Client Logic** | Modern ES6+ JavaScript (Fetch API, WebGL backgrounds, draggable canvas, Pomodoro logic) |

---

## 📁 Repository Structure Map

```text
├── courses/                      # Main App Module
│   ├── migrations/               # Database Migrations
│   ├── models.py                 # Relational schemas (UserProfile, Course, Video, Progress, StudySession)
│   ├── urls.py                   # App level routes and dynamic endpoints
│   ├── utils.py                  # Core Logic (API aggregators, Mock generators, LLM connectors)
│   └── views.py                  # Controller logic (Auth, dashboard, player, pricing, payment callback)
├── focustube/                    # Root configuration module
│   ├── settings.py               # Django configuration (variables, security policy, CORS)
│   ├── urls.py                   # Core URL dispatcher
│   └── wsgi.py / asgi.py         # Deployment connectors
├── static/                       # Static Asset Directory
│   ├── css/
│   │   └── styles.css            # Dark mode, Glassmorphic component styles
│   └── js/
│       └── main.js               # Async player controllers, chat integrations, timer scripts
├── templates/courses/            # UI Templates
│   ├── base.html                 # Navigation & Base HTML Shell
│   ├── home.html                 # Landing Page
│   ├── pricing.html              # Subscription tiers and Razorpay triggers
│   ├── dashboard.html            # User Course Syllabus Hub & learning analytics
│   ├── learn.html                # Interactive main course player & AI chat study portal
│   ├── focus_room.html           # Pomodoro focused study portal
│   └── certificate.html          # Custom digital graduation certificate
```

---

## ⚙️ Quick Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ajay160380/Edu-Tech-AI.git
cd Edu-Tech-AI
```

### 2. Configure Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Secrets
Create a `.env` file in the root directory and populate it:
```env
# Django Settings
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_DEBUG=True

# External APIs
YOUTUBE_API_KEY=your_youtube_data_api_v3_key
GROQ_API_KEY=your_groq_llama_3.1_api_key

# Firebase Credentials
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_CREDENTIALS_JSON=your_raw_firebase_key_json_string

# Razorpay Configuration (Sandbox Keys)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### 5. Run Migrations & Startup
```bash
python manage.py migrate
python manage.py runserver
```
Visit the local server in your browser at `http://127.0.0.1:8000/`.

---

## 🧪 Automated Testing
To validate core system functions, AI integration, and the payment gateway, you can run the included automation test scripts:
```bash
python test_notes_workspace.py     # Validates workspace actions
python test_customizer_features.py # Validates AI tutor chatbot and summaries
```

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more details.
