console.log("Background script loaded");

function sendTabURLToPython(tab) {
  if (tab && tab.url) {
    fetch("http://127.0.0.1:5001/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: tab.url })
    })
    .catch(err => console.error("Failed to send URL:", err));
  }
}

chrome.tabs.onActivated.addListener(activeInfo => {
  chrome.tabs.get(activeInfo.tabId, sendTabURLToPython);
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    sendTabURLToPython(tab);
  }
});
