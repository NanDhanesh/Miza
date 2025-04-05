import os
import google.generativeai as genai
import matplotlib.pyplot as plt
import requests

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
        print(f"Error configuring Gemini API: {str(e)}")
        _analyzer_enabled = False
        return False

def is_analyzer_enabled():
    """Check if the productivity analyzer is enabled"""
    return _analyzer_enabled

def analyze_productivity(domain):
    """Use Gemini API to determine if a domain is productive for studying"""
    if not _analyzer_enabled:
        # Try to set up analyzer one more time
        if not setup_analyzer():
            return "unknown"
    
    try:
        # Use the updated model name 'gemini-2.0-flash-lite'
        model_name = 'gemini-2.0-flash-lite'
        model = genai.GenerativeModel(model_name)
        
        # Craft the prompt for a single domain
        prompt = f"""Based on the list of websites the user has visited during a study session, 
determine whether each one is either productive or unproductive for a study session. 
Make a strict binary determination.

Website: {domain}

Respond with only the word 'productive' or 'unproductive'."""
        
        # Get response from Gemini
        response = model.generate_content(prompt)
        
        # Process the response
        result = response.text.strip().lower()
        
        # Ensure we only get 'productive' or 'unproductive'
        if result in ['productive', 'unproductive']:
            return result
        else:
            print(f"Unexpected Gemini response for {domain}: {result}")
            return "unknown"
            
    except Exception as e:
        print(f"Error analyzing productivity for {domain}: {str(e)}")
        return "unknown"

def list_available_models():
    """Optional: List available models for the Gemini API"""
    try:
        models = genai.list_models()
        print("Available models:", models)
    except Exception as e:
        print("Error listing available models:", str(e))

# Initialize the analyzer when the module is imported
setup_analyzer()

if __name__ == "__main__":
    # Uncomment the next line to list available models if needed
    # list_available_models()

    # Retrieve the list of tracked domains from the tracking server
    try:
        response = requests.get("http://localhost:5001/domains")
        response.raise_for_status()
        domain_history = response.json()  # domain_history is a dict with domain keys
        sample_domains = list(domain_history.keys())
        if not sample_domains:
            print("No domains tracked yet.")
    except Exception as e:
        print(f"Error fetching domain history: {str(e)}")
        sample_domains = []
    
    # Dictionary to count outcomes
    results = {"productive": 0, "unproductive": 0}
    
    # Analyze each domain and accumulate the results
    for domain in sample_domains:
        result = analyze_productivity(domain)
        results[result] += 1
        print(f"{domain}: {result}")
    
    print("Analysis results:", results)

    statuses = list(results.keys())
    counts = list(results.values())

    plt.figure(figsize=(6,4))
    plt.bar(statuses, counts, color=['green', 'red'])
    plt.title("Website Visit Analysis")
    plt.xlabel("Category")
    plt.ylabel("Number of Visits")
    plt.show()

    

