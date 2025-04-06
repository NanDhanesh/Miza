import cv2
import numpy as np
import time
from datetime import datetime
from flask import Flask, request
from urllib.parse import urlparse
import threading
import os
import matplotlib.pyplot as plt
import requests
import google.generativeai as genai
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()
# --------------- Flask Server Setup ---------------

app = Flask(__name__)
CORS(app)

current_url = "unknown"
current_domain = "unknown"
domain_history = {}
domain_times = {}
_analyzer_enabled = False

def get_domain_root(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

@app.route('/track', methods=['POST'])
def track_url():
    global current_url, current_domain, domain_history, domain_times
    data = request.get_json()
    if not data:
        return {"status": "error", "message": "No data received"}, 400

    url = data.get('url', 'unknown')
    domain = get_domain_root(url)
    current_url = url
    current_domain = domain

    now = datetime.now()
    if domain in domain_history:
        domain_history[domain]['count'] += 1
        domain_history[domain]['last_seen'] = now
    else:
        domain_history[domain] = {
            'first_seen': now,
            'last_seen': now,
            'count': 1
        }

    if domain not in domain_times:
        domain_times[domain] = 0.0

    print(f"[TRACKED] {domain}")
    return {"status": "ok"}

@app.route('/status', methods=['GET'])
def get_status():
    return {"status": "running", "domain": current_domain}

@app.route('/domains', methods=['GET'])
def get_domains():
    serializable_history = {}
    for domain, data in domain_history.items():
        serializable_history[domain] = {
            'first_seen': data['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': data['last_seen'].strftime('%Y-%m-%d %H:%M:%S'),
            'count': data['count']
        }
    return serializable_history

def run_flask_server():
    app.run(port=5000)

# --------------- Gemini Analyzer ---------------

def setup_analyzer():
    global _analyzer_enabled
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        try:
            with open('.api_key', 'r') as key_file:
                api_key = key_file.read().strip()
        except FileNotFoundError:
            _analyzer_enabled = False
            return False
    try:
        genai.configure(api_key=api_key)
        _analyzer_enabled = True
        return True
    except Exception:
        _analyzer_enabled = False
        return False

def analyze_productivity(domain):
    if not _analyzer_enabled and not setup_analyzer():
        return "productive"
    prompt = f"""You are an assistant helping students stay on task.
Given a single website domain, decide whether it is productive or unproductive for a typical study session.
Make a clear binary choice and respond with exactly one of these two words:

productive
unproductive

For reference, this is for a college student. So websites like youtube, twitter, etc. are most likely unproductive.
Website: {domain}
"""
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    try:
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        return result if result in ("productive", "unproductive") else "productive"
    except:
        return "productive"

# --------------- Eye Tracker ---------------

def run_eye_tracker():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    eye_positions = []
    max_positions = 30
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture initial frame")
        return

    heatmap = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.float32)
    start_time = time.time()
    focus_time = 0
    last_time = start_time

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            display = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            eyes_detected = False

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = display[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                if len(eyes) > 0:
                    eyes_detected = True
                for (ex, ey, ew, eh) in eyes:
                    eye_center_x = x + ex + ew//2
                    eye_center_y = y + ey + eh//2
                    cv2.circle(heatmap, (eye_center_x, eye_center_y), 30, 0.1, -1)
                    eye_positions.append((eye_center_x, eye_center_y))
                    if len(eye_positions) > max_positions:
                        eye_positions.pop(0)
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                    cv2.circle(display, (eye_center_x, eye_center_y), 2, (0, 0, 255), -1)

            if eyes_detected:
                focus_time += 1 / 30.0

            for i in range(1, len(eye_positions)):
                intensity = int(255 * (i / len(eye_positions)))
                cv2.line(display, eye_positions[i-1], eye_positions[i], (0, intensity, 255-intensity), 1)

            heatmap_normalized = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_color = cv2.applyColorMap(np.uint8(heatmap_normalized), cv2.COLORMAP_JET)
            heatmap_display = cv2.addWeighted(frame, 0.6, heatmap_color, 0.4, 0)

            elapsed_time = time.time() - start_time
            focus_percentage = (focus_time / elapsed_time) * 100 if elapsed_time > 0 else 0
            cv2.putText(display, f"Focus: {focus_percentage:.1f}%", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow('Eye Tracking', display)
            cv2.imshow('Attention Heatmap', heatmap_display)
            heatmap *= 0.99

            now = time.time()
            delta = now - last_time
            last_time = now

            if current_domain not in domain_times:
                domain_times[current_domain] = 0
            domain_times[current_domain] += delta
            print(f"Current Domain: {current_domain} ({domain_times[current_domain]:.1f}s)")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Ending session...")

    finally:
        cap.release()
        cv2.destroyAllWindows()

        print("\n--- Session Summary ---")
        print(f"Session Duration: {elapsed_time:.2f} seconds")
        print(f"Focus Time: {focus_time:.2f} seconds")
        print(f"Focus Score: {focus_percentage:.2f}%")

        unfocused_time = elapsed_time - focus_time
        labels = ['Focused', 'Not Focused']
        times = [focus_time, unfocused_time]
        colors = ['#2ecc71', '#e74c3c']

        plt.style.use('dark_background')
        plt.rcParams['font.family'] = 'DejaVu Sans'
        fig, ax = plt.subplots(figsize=(6, 4), facecolor='black')
        glow_rect = plt.Rectangle((-0.5, -1), 2, max(times)+3, linewidth=0, edgecolor=None, facecolor='white', alpha=0.03, zorder=0)
        ax.add_patch(glow_rect)
        bars = ax.bar(labels, times, color=colors, edgecolor='white', linewidth=1.2, zorder=2)
        ax.set_ylim(bottom=0)
        for bar, yval in zip(bars, times):
            ax.text(bar.get_x() + bar.get_width()/2.0, yval / 2, f'{yval:.1f}s', ha='center', va='center', color='black',
                    fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.3'))
        ax.set_title('Focus Breakdown', fontsize=14, color='white', pad=15)
        ax.set_ylabel('Time (seconds)', fontsize=12, color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        fig.tight_layout()
        plt.show()

        try:
            response = requests.get("http://localhost:5000/domains")
            response.raise_for_status()
            domain_data = response.json()
        except Exception as e:
            print("Failed to fetch domain history:", e)
            domain_data = {}

        productivity = {"productive": 0, "unproductive": 0}
        domain_labels = []
        domain_times_sorted = []
        domain_colors = []

        for domain in domain_data:
            label = analyze_productivity(domain)
            duration = domain_times.get(domain, 0)
            productivity[label] += duration
            domain_labels.append(domain)
            domain_times_sorted.append(duration)
            domain_colors.append('#2ecc71' if label == 'productive' else '#e74c3c')
            print(f"{domain}: {label} ({duration:.1f}s)")

        # Show both domain bar chart and productivity summary side-by-side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), facecolor='black')
        plt.style.use('dark_background')
        plt.rcParams['font.family'] = 'DejaVu Sans'

        ax1.barh(domain_labels, domain_times_sorted, color=domain_colors)
        ax1.set_title("Time Spent Per Website", color='white')
        ax1.set_xlabel("Time (s)", color='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.tick_params(axis='x', colors='white')

        categories = list(productivity.keys())
        values = list(productivity.values())
        ax2.bar(categories, values, color=['#2ecc71', '#e74c3c'])
        ax2.set_title("Productive vs Unproductive Time", color='white')
        ax2.set_ylabel("Time (s)", color='white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')

        fig.tight_layout()
        plt.show()

# --------------- Main Entry Point ---------------

if __name__ == "__main__":
    threading.Thread(target=run_flask_server, daemon=True).start()
    run_eye_tracker()
