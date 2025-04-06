import cv2
import numpy as np
import time
from datetime import datetime
from flask import Flask, request, jsonify
from urllib.parse import urlparse
import threading
import os
import matplotlib.pyplot as plt
import requests
import google.generativeai as genai
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
# Combined functionality of eye tracker, Flask server, and Gemini analyzer

# --------------- Flask Server Setup ---------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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

@app.route('/track', methods=['POST', 'OPTIONS'])
def track_url():
    global current_url, current_domain, domain_history, domain_times
    
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_response("")
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
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

    # Ensure domain_times has an entry
    if domain not in domain_times:
        domain_times[domain] = 0.0

    print(f"[TRACKED] {domain}", flush=True)
    return {"status": "ok"}

@app.route('/domains', methods=['GET'])
def get_domains():
    try:
        serializable_history = {}
        for domain, data in domain_history.items():
            serializable_history[domain] = {
                'first_seen': data['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                'last_seen': data['last_seen'].strftime('%Y-%m-%d %H:%M:%S'),
                'count': data['count']
            }
        return serializable_history
    except Exception as e:
        print(f"Error in get_domains: {e}")
        return {"error": str(e)}, 500

def run_flask_server():
    print("Starting Flask server on http://127.0.0.1:5002", flush=True)
    app.run(host='127.0.0.1', port=5002, debug=False)

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
Respond with exactly one of these two words (no extra text):

productive
unproductive

Website: {domain}
"""
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    try:
        resp = model.generate_content(prompt)
        res = resp.text.strip().lower()
        return res if res in ("productive", "unproductive") else "productive"
    except:
        return "productive"

def list_available_models():
    try:
        models = genai.list_models()
        print("Available models:", models)
    except Exception as e:
        print("Error listing available models:", e)

# Initialize the analyzer when imported
setup_analyzer()

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
    last_print = start_time
    print_interval = 1.0  # seconds between prints
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
                    eye_center_x = x + ex + ew // 2
                    eye_center_y = y + ey + eh // 2
                    cv2.circle(heatmap, (eye_center_x, eye_center_y), 30, 0.1, -1)
                    eye_positions.append((eye_center_x, eye_center_y))
                    if len(eye_positions) > max_positions:
                        eye_positions.pop(0)
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    cv2.circle(display, (eye_center_x, eye_center_y), 2, (0, 0, 255), -1)

            if eyes_detected:
                focus_time += (time.time() - last_time)

            for i in range(1, len(eye_positions)):
                intensity = int(255 * (i / len(eye_positions)))
                cv2.line(display, eye_positions[i - 1], eye_positions[i],
                         (0, intensity, 255 - intensity), 1)

            hm_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
            hm_color = cv2.applyColorMap(np.uint8(hm_norm), cv2.COLORMAP_JET)
            hm_disp = cv2.addWeighted(frame, 0.6, hm_color, 0.4, 0)

            elapsed = time.time() - start_time
            pct = (focus_time / elapsed) * 100 if elapsed > 0 else 0
            cv2.putText(display, f"Focus: {pct:.1f}%", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Eye Tracking', display)
            cv2.imshow('Attention Heatmap', hm_disp)
            heatmap *= 0.99

            now = time.time()
            delta = now - last_time
            last_time = now
            domain_times[current_domain] = domain_times.get(current_domain, 0) + delta

            if now - last_print >= print_interval:
                print(f"Current Domain: {current_domain} ({domain_times.get(current_domain, 0):.1f}s) | Tracked Domains: {len(domain_history)}")
                last_print = now

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Ending session...")

    finally:
        cap.release()
        cv2.destroyAllWindows()

        elapsed = time.time() - start_time
        pct = (focus_time / elapsed) * 100 if elapsed > 0 else 0
        print("\n--- Session Summary ---")
        print(f"Session Duration: {elapsed:.2f} seconds")
        print(f"Focus Time: {focus_time:.2f} seconds")
        print(f"Focus Score: {pct:.2f}%")

        print("\n--- Domain History ---")
        if domain_history:
            for d, info in domain_history.items():
                print(f"{d}: count={info['count']}, first={info['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}, last={info['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
            domain_data = {d: {"count": info["count"]} for d, info in domain_history.items()}
        else:
            print("No domains were tracked.")
            domain_data = {}

        prod = {"productive": 0, "unproductive": 0}
        labels, times_list, colors = [], [], []
        print("\n--- Analyzing Productivity ---")
        for d in domain_data:
            lbl = analyze_productivity(d)
            dur = domain_times.get(d, 0)
            prod[lbl] += dur
            labels.append(d)
            times_list.append(dur)
            colors.append('#2ecc71' if lbl == 'productive' else '#e74c3c')
            print(f"{d}: {lbl} ({dur:.1f}s)")

        print("\n--- Generating Plots ---")
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 4), facecolor='black')  # Added ax3 for focus plot
        plt.style.use('dark_background')
        plt.rcParams['font.family'] = 'DejaVu Sans'

        # Plot 1: Time Spent Per Website
        ax1.barh(labels, times_list, color=colors)
        ax1.set_title("Time Spent Per Website", color='white')
        ax1.set_xlabel("Time (s)", color='white')
        ax1.tick_params(axis='y', colors='white')
        ax1.tick_params(axis='x', colors='white')

        # Plot 2: Productive vs Unproductive Time
        categories = list(prod.keys())
        values = list(prod.values())
        ax2.bar(categories, values, color=['#2ecc71', '#e74c3c'])
        ax2.set_title("Productive vs Unproductive", color='white')
        ax2.set_ylabel("Time (s)", color='white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')

        # Plot 3: Focus Breakdown
        focus_labels = ['Focused', 'Not Focused']
        focus_times = [focus_time, elapsed - focus_time]
        focus_colors = ['#2ecc71', '#e74c3c']
        bars = ax3.bar(focus_labels, focus_times, color=focus_colors, edgecolor='white', linewidth=1.2)
        ax3.set_title("Focus Breakdown", color='white')
        ax3.set_ylabel("Time (s)", color='white')
        ax3.tick_params(axis='x', colors='white')
        ax3.tick_params(axis='y', colors='white')
        for bar, yval in zip(bars, focus_times):
            ax3.text(bar.get_x() + bar.get_width()/2.0, yval / 2, f'{yval:.1f}s', 
                     ha='center', va='center', color='black', fontsize=10, fontweight='bold',
                     bbox=dict(facecolor='white', alpha=0.6, boxstyle='round,pad=0.3'))

        fig.tight_layout()
        plt.show(block=True)
        print("Plots displayed. Close the plot windows to exit.")

# --------------- Main Entry Point ---------------
if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask_server, daemon=True)
    server_thread.start()
    
    print("Waiting for server to start...", flush=True)
    time.sleep(2)
    
    run_eye_tracker()