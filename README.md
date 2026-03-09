# Miza — AI-Powered Study Focus Tracker

Miza is a productivity app built for students who want to take control of their study sessions. You describe what you want to study, and Miza builds a personalized dashboard — then watches over your session using eye tracking and browser tab monitoring to give you honest feedback when it's done.

---

## What It Does

1. **Voice-to-Dashboard** — Speak (or type) your study goals. Gemini AI parses your input and generates a custom study dashboard with a countdown timer and a task checklist tailored to your session.

2. **Real-Time Focus Tracking** — During your session, two systems run in parallel:
   - **Eye tracking** (via OpenCV + webcam) monitors whether you're looking at the screen.
   - **Browser tab monitoring** (via a Chrome extension) logs every domain you visit and classifies it as productive or unproductive using Gemini AI.

3. **Session Wrapped** — When you end the session, you get a visual summary — Spotify Wrapped style — showing your productivity ratio, tasks completed, and an eye-tracking focus score.

---

## How It Works

```
┌─────────────────────────────────────────────────────┐
│  Landing Page (Next.js)                             │
│  Voice input → Gemini API → JSON dashboard data     │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│  Study Dashboard (Next.js)                          │
│  Countdown timer + interactive checklist            │
│  Polls Python backend every second during session   │
└──────────┬──────────────────────────────────────────┘
           │
    ┌──────▼───────┐          ┌──────────────────────┐
    │ Flask Backend │◄────────│ Chrome Extension     │
    │ (combined.py) │         │ Reports visited URLs │
    │               │         └──────────────────────┘
    │ Eye tracking  │
    │ (OpenCV/cv2)  │
    │               │
    │ Tab analysis  │
    │ (Gemini AI)   │
    └──────┬────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│  Focus Wrapped (Next.js)                            │
│  Productivity %, Tasks completed, Visual focus score│
└─────────────────────────────────────────────────────┘
```

### Components

| Component | Location | Description |
|---|---|---|
| Next.js frontend | `FirstScreen/` | Landing page, dashboard, and session summary |
| Gemini dashboard API | `FirstScreen/app/api/generate-dashboard/` | Converts voice transcript to timer + checklist JSON |
| Python backend | `combined.py` | Flask server handling eye tracking and tab analysis |
| Chrome extension | `chrome/` | Tracks browser tabs and reports domains to the backend |

---

## How to Run

### Prerequisites

- Node.js 18+
- Python 3.9+
- A webcam (for eye tracking)
- Google Chrome
- A Gemini API key

---

### 1. Start the Python Backend

```bash
cd wildhacks
pip install flask flask-cors opencv-python numpy matplotlib google-generativeai python-dotenv requests
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Then run:

```bash
python combined.py
```

The Flask server starts on `http://localhost:5001`.

---

### 2. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked** and select the `chrome/` folder
4. The extension will start reporting visited tabs to the backend automatically

---

### 3. Start the Next.js Frontend

```bash
cd FirstScreen
npm install
```

Create a `.env.local` file inside `FirstScreen/`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Then run:

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

---

### 4. Run a Study Session

1. On the landing page, click **Start Recording** and describe your study goals out loud (e.g. *"I need to study for my biology midterm — review cell division and finish my practice problems"*)
2. Click **Generate Study Dashboard** — Gemini will create a personalized timer and checklist
3. On the dashboard, click **Start** to begin tracking
4. Study as normal — the eye tracker and tab monitor run in the background
5. Click **End** when you're done to view your **Focus Wrapped** summary

---

## Built With

- [Next.js 15](https://nextjs.org/) — Frontend framework
- [Google Gemini API](https://ai.google.dev/) — Dashboard generation and tab classification
- [OpenCV](https://opencv.org/) — Webcam-based eye tracking
- [Flask](https://flask.palletsprojects.com/) — Python backend server
- Chrome Extensions API — Browser tab monitoring
