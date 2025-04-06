console.log("Background script loaded");

// Query and log available tabs
chrome.tabs.query({}, (tabs) => {
  console.log("Tabs available:", tabs.length);
});

// Immediately send the active tab once on load:
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0]) {
    console.log("Initial send of active tab:", tabs[0].url);
    sendTabURLToPython(tabs[0]);
  }
});

function sendTabURLToPython(tab) {
  if (tab && tab.url) {
    console.log("Sending URL:", tab.url);
    fetch("http://127.0.0.1:5002/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url })
    })
    .then(response => {
      console.log("Response status:", response.status);
      return response.json();
    })
    .then(data => console.log("Server response:", data))
    .catch(err => {
      console.error("Failed to send URL:", err);
      console.log("Trying alternate URL...");
      fetch("http://localhost:5002/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: tab.url })
      })
      .then(response => {
        console.log("Alternate response status:", response.status);
        return response.json();
      })
      .then(data => console.log("Server response (alternate):", data))
      .catch(altErr => console.error("All connection attempts failed:", altErr));
    });
  } else {
    console.log("No valid tab or URL:", tab);
  }
}

chrome.tabs.onActivated.addListener(activeInfo => {
  console.log("Tab activated:", activeInfo);
  chrome.tabs.get(activeInfo.tabId, sendTabURLToPython);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  console.log("Tab updated:", changeInfo, tabId);
  if (changeInfo.status === "complete") {
    sendTabURLToPython(tab);
  }
});
