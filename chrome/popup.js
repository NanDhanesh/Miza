fetch("http://127.0.0.1:5001/domains")
  .then(res => res.json())
  .then(data => {
    document.getElementById("status").textContent = "Running";
    document.getElementById("status").className = "connected";
    // Use the most recently visited domain (last_seen)
    const domains = Object.keys(data);
    if (domains.length > 0) {
      const latestDomain = domains.reduce((a, b) =>
        data[a].last_seen > data[b].last_seen ? a : b
      );
      document.getElementById("domain").textContent = latestDomain || "unknown";
    } else {
      document.getElementById("domain").textContent = "none tracked yet";
    }
  })
  .catch(() => {
    document.getElementById("status").textContent = "Not Connected";
    document.getElementById("status").className = "disconnected";
    document.getElementById("domain").textContent = "N/A";
  });