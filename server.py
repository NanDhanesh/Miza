from flask import Flask, request
from urllib.parse import urlparse
import threading

# This script sets up a Flask server to track the current URL and domain.
# It uses a global variable to store the current URL and domain.
# Run this file, then run the chrome extension
# TO run chrome extension upload the files via "load unpacked" in chrome://extensions

current_url = "unknown"
current_domain = "unknown"

app = Flask(__name__)

def get_domain_root(url):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

@app.route('/track', methods=['POST'])
def track_url():
    global current_url, current_domain
    data = request.get_json()
    url = data.get('url', 'unknown')
    domain = get_domain_root(url)
    current_url = url
    current_domain = domain
    print(f"[TRACKED] {domain}")
    return {"status": "ok"}

@app.route('/status', methods=['GET'])
def get_status():
    return {
        "status": "running",
        "domain": current_domain
    }

def run_server():
    app.run(port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    import time
    while True:
        print(f"Current Domain: {current_domain}")
        time.sleep(3)
