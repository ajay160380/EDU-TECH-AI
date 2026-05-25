# 🎓 EduTech AI - AI-Powered Interactive Course & Learning Workspace

![Django](https://img.shields.io/badge/Django-6.0.4-092e20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.14-3776ab?style=for-the-badge&logo=python)

EduTech AI is a premium, high-fidelity EdTech SaaS platform built with Python (Django) that transforms standard YouTube playlists into comprehensive, interactive learning workspaces. Powered by advanced AI models, the platform acts as an automated study companion, offering textbook-level summaries, customized study plans, smart interactive quizzes, a focused Pomodoro study room, and automated grading systems with dynamic PDF certificate generation on exam completion.


---

## 🌟 Key Product Features

*   **🎬 Dynamic Course Syllabus Parser**: Parses any public YouTube playlist URL or ID, automatically imports metadata, processes high-volume playlists (supporting 500+ videos via pagination), and syncs exact video durations. It includes high-fidelity mock course fallbacks for seamless offline operations.
*   **🤖 AI Study Buddy & Dynamic Lecture Summarizer**: Leverages advanced LLMs (via Groq API with Llama-3.1-8b) to instantly generate lecture-specific summaries, coding blueprints, architectural charts, and interactive multiple-choice quizzes tailored to the specific user's tier.
*   **🗣️ Conversational Hinglish Tutor**: Features a smart translation module that converts complex educational concepts into warm, natural, and highly engaging Hinglish (Hindi written in Roman script) for easy understanding.
*   **⏱️ AI Focus Room & Draggable Zen Overlay**: A distraction-free Pomodoro study portal where users can select their active course, set structured study times, and log session durations to maintain high learning streaks. Includes a tactile, draggable glassmorphic Zen Bar overlay with viewport collision bounds, active drag transition suppression, and position coordinates persistence.
*   **✍️ Dynamic Quiz & Final Exam Module**: Features a comprehensive final exam with strict timers, automatic instant grading, cooling-off rules to prevent spamming, and dynamic progress validation.
*   **📜 Dynamic Digital Certificates & Public Verification**: Upon passing the final exam, the platform dynamically generates elegant, custom graduation certificates with personalized completion details and verification IDs. It features a fully public verification gateway (`/certificate/verify/<credential_id>/`) with guest sign-up banners and shareable links for LinkedIn.
*   **💳 Tier Subscription & Billing (Razorpay)**: Integrates three pricing tiers (`Free`, `Pro`, `Ultra`) connected directly to a sandbox Razorpay billing gateway with dynamic modal generation and callback signature verification.
*   **🔐 Firebase Authentication**: Seamless authentication using Email/Credentials combined with Firebase Google Popup Authentication for security and rapid login.

---

## 🛠️ Advanced Tech Stack

*   **Backend Framework**: Django 6.0.5 (Python 3.12+)
*   **Database Management**: SQLite3 (relational schema optimized with signals for auto-sync profile management)
*   **AI Integration**: Groq API (Llama 3.1 8B Instant) & Pollinations AI (as a robust free fallback)
*   **Video Delivery**: YouTube Data API v3 (metadata, playlist items, content details extraction)
*   **Billing Gateway**: Razorpay REST SDK
*   **Auth Integration**: Firebase Frontend Auth SDK (OAuth 2.0 with Google Identity Services)
*   **Styling & UI**: Vanilla CSS3 (Custom theme layouts, Cyberpunk glassmorphism design, vibrant dark mode transitions)
*   **Client Scripting**: Pure Vanilla ES6 JavaScript (Asynchronous fetch modules, YouTube API Player controls, dynamic state toggling)

---

## 📁 Repository Structure Map

```text
├── courses/                      # Main App Module
│   ├── migrations/               # Database Migrations
│   ├── admin.py                  # Custom admin interface
│   ├── apps.py                   # App configurations
│   ├── models.py                 # Relational schemas (UserProfile, Course, Video, Progress, StudySession)
│   ├── urls.py                   # App level routes and dynamic endpoints
│   ├── utils.py                  # Core logic (API aggregators, Mock generators, LLM connectors)
│   └── views.py                  # Controller logic (Auth, dashboard, player, pricing, payment callback)
├── focustube/                    # Root configuration module
│   ├── settings.py               # Django configuration (variables, security policy, CORS)
│   ├── urls.py                   # Core URL dispatcher
│   └── wsgi.py / asgi.py         # Deployment connectors
├── static/                       # Static Asset Directory
│   ├── css/
│   │   └── styles.css            # Dark mode, Glassmorphism, animations & component styles
│   └── js/
│       └── main.js               # Async player controllers, chat integrations, timer scripts
├── templates/courses/            # UI Templates
│   ├── base.html                 # Navigation & Base HTML Shell
│   ├── home.html                 # Landing Page
│   ├── pricing.html              # Subscription tiers and Razorpay triggers
│   ├── dashboard.html            # User Course Syllabus Hub & learning analytics
│   ├── learn.html                # Interactive main course player & AI chat study portal
│   ├── focus_room.html           # Pomodoro focused study portal
│   ├── final_exam.html           # Exam countdown and grading portal
│   ├── exam_results.html         # Scorecard, retry timer, and grading metrics
│   ├── certificate.html          # Custom digital graduation certificate
│   └── about.html                # Platform overview
├── manage.py                     # Django CLI
├── .gitignore                    # Excludes sensitive data (secrets, databases, images)
├── test_browser_payment.py      # E2E Test Suite for checkout/pricing pipelines
├── test_customizer_features.py   # AI features validation tests
├── test_notes_workspace.py       # Core Workspace action test scripts
└── diagnose_razorpay.py          # Diagnostic checking script for gateway configurations
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
# Create environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows PowerShell)
# .\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install django djangorestframework python-dotenv requests razorpay
```

### 4. Setup Environment Secrets
Create a `.env` file in the root directory (same folder as `manage.py`) and populate it with your API credentials:
```env
# Django Security Settings
DJANGO_SECRET_KEY=your_django_secret_key_here
DJANGO_DEBUG=True

# External Integrations
YOUTUBE_API_KEY=your_youtube_data_api_v3_key
GROQ_API_KEY=your_groq_llama_3.1_api_key

# Firebase Credentials
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id

# Razorpay Configuration (Sandbox Keys)
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```
*Note: If no API keys are supplied, the application automatically uses built-in high-fidelity procedural fallbacks to mock API operations seamlessly.*

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin Access)
```bash
python manage.py createsuperuser
```

### 7. Run Local Development Server
```bash
python manage.py runserver
```
Visit the local server in your browser at `http://127.0.0.1:8000/`.

---

## 🧪 Running Automated E2E Test Suites

To validate core system functions, AI integration, and the payment gateway, you can run the included automation test scripts:

```bash
# Validate workspace actions and note-taking mechanics
python test_notes_workspace.py

# Validate AI-tutor chatbots and summarizer engines
python test_customizer_features.py

# Run Razorpay configuration diagnostics
python diagnose_razorpay.py
```

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more details.
