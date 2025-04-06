console.log("Background script loaded");

// Test tabs API access
chrome.tabs.query({}, (tabs) => {
  console.log("Tabs available:", tabs.length);
});

function sendTabURLToPython(tab) {
  if (tab && tab.url) {
    console.log("Sending URL:", tab.url); // Debug
    fetch("http://127.0.0.1:5001/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url })
    })
    .then(response => response.json())
    .then(data => console.log("Server response:", data))
    .catch(err => console.error("Failed to send URL:", err));
  } else {
    console.log("No valid tab or URL:", tab);
  }
}

chrome.tabs.onActivated.addListener(activeInfo => {
  console.log("Tab activated:", activeInfo); // Debug
  chrome.tabs.get(activeInfo.tabId, sendTabURLToPython);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  console.log("Tab updated:", changeInfo, tabId); // Debug
  if (changeInfo.status === "complete") {
    sendTabURLToPython(tab);
  }
});