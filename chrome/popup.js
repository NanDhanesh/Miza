fetch("http://127.0.0.1:5000/status")
  .then(res => res.json())
  .then(data => {
    document.getElementById("status").textContent = "Running";
    document.getElementById("status").className = "connected";
    document.getElementById("domain").textContent = data.domain || "unknown";
  })
  .catch(() => {
    document.getElementById("status").textContent = "Not Connected";
    document.getElementById("status").className = "disconnected";
    document.getElementById("domain").textContent = "N/A";
  });
