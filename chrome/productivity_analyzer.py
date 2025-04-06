import os
import google.generativeai as genai
import matplotlib
matplotlib.use('Agg')  # Use a backend that doesn't require a display
import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv

load_dotenv()

# Track if the analyzer is properly configured
_analyzer_enabled = False

def setup_analyzer():
    """Initialize the productivity analyzer with the API key"""
    global _analyzer_enabled

    # Try to get API key from environment variable
    api_key = os.environ.get("GEMINI_API_KEY")

    # If not in environment, try to load from config file
    if not api_key:
        try:
            with open('.api_key', 'r') as key_file:
                api_key = key_file.read().strip()
        except FileNotFoundError:
            print("WARNING: GEMINI_API_KEY not found in environment or .api_key file")
            _analyzer_enabled = False
            return False

    # Configure Gemini with the API key
    try:
        genai.configure(api_key=api_key)
        _analyzer_enabled = True
        print("Productivity analyzer successfully configured")
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        _analyzer_enabled = False
        return False

def analyze_productivity(domain):
    """Use Gemini API to determine if a domain is productive for studying"""
    if not _analyzer_enabled:
        if not setup_analyzer():
            return "productive"  # fallback if setup fails

    prompt = f"""You are an assistant helping students stay on task.
Given a single website domain, decide whether it is productive or unproductive for a typical study session.
Make a clear binary choice and respond with exactly one of these two words (no punctuation, no extra text):

productive
unproductive

Website: {domain}
"""

    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    try:
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        if result in ("productive", "unproductive"):
            return result
        else:
            print(f"Unexpected response for {domain!r}: {result!r}. Defaulting to productive.")
            return "productive"
    except Exception as e:
        print(f"Error analyzing productivity for {domain!r}: {e}. Defaulting to productive.")
        return "productive"

def list_available_models():
    """Optional: List available models for the Gemini API"""
    try:
        models = genai.list_models()
        print("Available models:", models)
    except Exception as e:
        print("Error listing available models:", e)

# Initialize the analyzer on import
setup_analyzer()

def main():
    try:
        response = requests.get("http://localhost:5001/domains")
        del_response = requests.delete("http://localhost:5001/domains")
        response.raise_for_status()
        domain_history = response.json()
        sample_domains = list(domain_history.keys())
        if not sample_domains:
            print("No domains tracked yet.")
    except Exception as e:
        print(f"Error fetching domain history: {e}")
        sample_domains = []

    # Tally results
    results = {"productive": 0, "unproductive": 0}

    for domain in sample_domains:
        label = analyze_productivity(domain)
        results[label] += 1
        print(f"{domain}: {label}")

    print("Analysis results:", results)

    # Plot the results
    statuses = list(results.keys())
    counts   = list(results.values())

    return counts

    # plt.figure(figsize=(6,4))
    # plt.bar(statuses, counts, color=['green', 'red'])
    # plt.title("Website Visit Analysis")
    # plt.xlabel("Category")
    # plt.ylabel("Number of Visits")
    # plt.savefig("analysis_result.png")
    #plt.show()

# if __name__ == "__main__":
#     # Uncomment to debug model names
#     # list_available_models()

#     # Fetch tracked domains from the server
#     try:
#         response = requests.get("http://localhost:5001/domains")
#         del_response = requests.delete("http://localhost:5001/domains")
#         response.raise_for_status()
#         domain_history = response.json()
#         sample_domains = list(domain_history.keys())
#         if not sample_domains:
#             print("No domains tracked yet.")
#     except Exception as e:
#         print(f"Error fetching domain history: {e}")
#         sample_domains = []

#     # Tally results
#     results = {"productive": 0, "unproductive": 0}

#     for domain in sample_domains:
#         label = analyze_productivity(domain)
#         results[label] += 1
#         print(f"{domain}: {label}")

#     print("Analysis results:", results)

#     # Plot the results
#     statuses = list(results.keys())
#     counts   = list(results.values())

#     plt.figure(figsize=(6,4))
#     plt.bar(statuses, counts, color=['green', 'red'])
#     plt.title("Website Visit Analysis")
#     plt.xlabel("Category")
#     plt.ylabel("Number of Visits")
#     plt.savefig("analysis_result.png")
#     #plt.show()
