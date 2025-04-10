from flask import Flask, request
from urllib.parse import urlparse
import threading
import time
from datetime import datetime
import productivity_analyzer as analyze
import eyes as vision

from flask_cors import CORS




# Create the Flask app instance
app = Flask(__name__)
CORS(app)
CORS(app, origins=["http://localhost:3000"], methods=["DELETE"], supports_credentials=True)
tracker = vision.EyeTracker()

# Store all domain names with timestamps
domain_history = {}
current_url = "unknown"
current_domain = "unknown"

def get_domain_root(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

@app.route('/track', methods=['POST'])
def track_url():
    global current_url, current_domain, domain_history
    print("Track endpoint called!")  # Debug: confirms the endpoint is hit
    data = request.get_json()
    print("Data received:", data)      # Debug: shows raw JSON data

    # If no data is received, log that and return an error response
    if not data:
        print("No data received!")
        return {"status": "error", "message": "No data received"}, 400

    url = data.get('url', 'unknown')
    print("URL extracted:", url)       # Debug: confirms URL extraction
    domain = get_domain_root(url)
    print("Domain extracted:", domain)   # Debug: shows extracted domain

    current_url = url
    current_domain = domain

    # Update domain history
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
    
    print(f"[TRACKED] {domain}")        # Confirmation message
    return {"status": "ok"}

@app.route('/domains', methods=['GET'])
def get_domains():
    serializable_history = {}
    for domain, data in domain_history.items():
        serializable_history[domain] = {
            'first_seen': data['first_seen'].strftime('%Y-%m-%d %H:%M:%S'),
            'last_seen': data['last_seen'].strftime('%Y-%m-%d %H:%M:%S'),
            'count': data['count']
        }
    #Wipe the domain_history dict here to allow the server to permarun - assumes u only get when u need to delete too
    #domain_history = {}
    return serializable_history

@app.route('/domains', methods=['DELETE'])
def delete_domains():
    global domain_history
    domain_history= {}
    print(f"DELETE: Total Domains Tracked: {len(domain_history)}")
    return {"status": "ok"}

@app.route('/domains/analyze', methods=['GET'])
def analyze_domains():
    counts = analyze.main()
    delete_domains()
    return {"status": "ok", "productive": counts[0], "unproductive": counts[1]}

@app.route('/vision/start', methods=['POST'])
def start_vision():
    tracker.start()
    return {"status": "ok"}

@app.route('/vision/step', methods=['POST'])
def step_vision():
    tracker.step()
    return {"status": "ok"}

@app.route('/vision/stop', methods=['POST'])
def stop_vision():
    score = tracker.stop()
    return {"focus_score": score}

def run_server():
    app.run(port=5001)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    
    while True:
        print(f"Current Domain: {current_domain}")
        print(f"Total Domains Tracked: {len(domain_history)}")
        time.sleep(3)
