"use client"

import { useSearchParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"

interface DashboardData {
  timer: number
  checklist: string[]
}



export default function DashboardPage() {
  const searchParams = useSearchParams()
  const resultRaw = searchParams.get("result")

  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [countdown, setCountdown] = useState(0)
  const [checklistState, setChecklistState] = useState<boolean[]>([])
  const [isRunning, setIsRunning] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [sessionSummary, setSessionSummary] = useState<{ productive: number; unproductive: number } | null>(null)

  //const searchParams = useSearchParams();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  //const [isRunning, setIsRunning] = useState<boolean>(false);
  const [checkedTasks, setCheckedTasks] = useState<boolean[]>([]);
  const [initialTime, setInitialTime] = useState<number>(0);


  // useEffect(() => {
  //   if (resultRaw) {
  //     try {
  //       const jsonString = resultRaw.replace(/```json|```/g, "").trim()
  //       const parsed: DashboardData = JSON.parse(jsonString)
  //       setDashboard(parsed)
  //       setCountdown(parsed.timer * 60)
  //       setChecklistState(new Array(parsed.checklist.length).fill(false))
  //     } catch (err) {
  //       console.error("Failed to parse dashboard result:", err)
  //     }
  //   }
  // }, [resultRaw])

  // Load and parse dashboard data
  useEffect(() => {
    const data = searchParams.get("data");
    if (data) {
      try {
        const decodedData = decodeURIComponent(data);
        const cleanedData = decodedData
          .replace(/```json/g, "")
          .replace(/```/g, "")
          .trim();
        const parsedData = JSON.parse(cleanedData);
        setDashboardData(parsedData);
        const totalSeconds = parsedData.timer * 60;
        setTimeLeft(totalSeconds);
        setInitialTime(totalSeconds);
        setCheckedTasks(new Array(parsedData.checklist.length).fill(false));
      } catch (error) {
        console.error("Failed to parse dashboard data:", error);
      }
    }
  }, [searchParams]);

  // useEffect(() => {
  //   if (!isRunning || isPaused || countdown <= 0) return

  //   const interval = setInterval(() => {
  //     setCountdown((prev) => prev - 1)
  //   }, 1000)

  //   return () => clearInterval(interval)
  // }, [isRunning, isPaused, countdown])

  // Timer countdown logic
  useEffect(() => {
    if (!isRunning || timeLeft <= 0) return;

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          setIsRunning(false);
          // Calculate checklist completion
          const completedTasks = checkedTasks.filter(Boolean).length;
          const totalTasks = checkedTasks.length;
          // Navigate to focus-wrapped page with checklist data
          router.push(
            `/focus-wrapped?completed=${completedTasks}&total=${totalTasks}`
          );
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, timeLeft, router, checkedTasks]);

  // const formatTime = (seconds: number) => {
  //   const mins = Math.floor(seconds / 60)
  //   const secs = seconds % 60
  //   return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  // }

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // const toggleChecklistItem = (index: number) => {
  //   setChecklistState((prev) => {
  //     const updated = [...prev]
  //     updated[index] = !updated[index]
  //     return updated
  //   })
  // }

  // Calculate the progress for the circle (0 to 1)
  const progress = timeLeft / initialTime;
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - progress);

  // Toggle checkbox state
  const handleCheckboxChange = (index: number) => {
    setCheckedTasks((prev) =>
      prev.map((checked, i) => (i === index ? !checked : checked))
    );
  };

  // Start/stop timer
  const toggleTimer = () => {
    setIsRunning((prev) => !prev);
  };

  if (!dashboardData) {
    return <div>Loading dashboard...</div>;
  }

  //------------------------------------//
  useEffect(() => {
    if (!isRunning || isPaused) return
  
    const interval = setInterval(() => {
      fetch("http://localhost:5001/vision/step", {
        method: "POST",
      }).catch((err) => {
        console.error("Failed to step vision:", err)
      })
    }, 1000) // every 1 second
  
    return () => clearInterval(interval)
  }, [isRunning, isPaused])

  const handleStart = async () => {
    try {
      const response = await fetch("http://localhost:5001/domains", {
        method: "DELETE",
      })

      const response2 = await fetch("http://localhost:5001/vision/start", {
        method: "POST",
      })
  
      const result = await response.json()
      const result2 = await response2.json()

      setIsRunning(true)
      setIsPaused(false)
      // if (result.status === "ok") {
      //   setIsRunning(true)
      //   setIsPaused(false)
      // } else {
      //   alert("Failed to start session: Server returned an error.")
      // }
    } catch (err) {
      console.error("Error connecting to Flask server:", err)
      alert("Failed to start session: Could not reach local server.")
    }
  }

  // const handleStart = () => {
  //   fetch("http://127.0.0.1:5001/track", {
  //       method: "POST",
  //       headers: { "Content-Type": "application/json" },
  //       body: JSON.stringify({ url: tab.url })
  //     })
  //     .then(response => response.json())
  //     .then(data => console.log("Server response:", data))
  //     .catch(err => console.error("Failed to send URL:", err));
  // }

  const handlePauseResume = () => {
    if (!isRunning) return
    setIsPaused((prev) => !prev)
  }

  // const handleEnd = () => {
  //   setIsRunning(false)
  //   setIsPaused(false)
  //   setCountdown(0)
  // }

  const handleEnd = async () => {
    try {
      const response = await fetch("http://localhost:5001/domains/analyze", {
        method: "GET",
      })

      const response2 = await fetch("http://localhost:5001/vision/stop", {
        method: "POST",
      })
  
      const result = await response.json()
      const result2 = await response2.json()

      setIsRunning(false)
      setIsPaused(false)
      setCountdown(0)
      if (result.status === "ok") {
        setSessionSummary({
          productive: result.productive,
          unproductive: result.unproductive,
        })
        alert(`🧠 Focus Score: ${result2.focus_score}`)
      }
      // if (result.status === "ok") {
      //   setIsRunning(true)
      //   setIsPaused(false)
      // } else {
      //   alert("Failed to start session: Server returned an error.")
      // }
    } catch (err) {
      console.error("Error connecting to Flask server:", err)
      alert("Failed to start session: Could not reach local server.")
    }
  }

  // const handleEnd = async () => {
  //   try {
  //     const response = await fetch("http://localhost:5001/vision/stop", {
  //       method: "GET",
  //     })
  
  //     const result = await response.json()
  
  //     setIsRunning(false)
  //     setIsPaused(false)
  //     setCountdown(0)
  
  //     if (result.status === "ok") {
  //       alert(`🧠 Focus Score: ${result.focus_score}`)
  //     }
  //   } catch (err) {
  //     console.error("Error connecting to Flask server:", err)
  //     alert("Failed to end session: Could not reach local server.")
  //   }
  // }

  //-------------------------------------------//

  // if (!dashboard) {
  //   return <p style={{ padding: "2rem" }}>Loading dashboard...</p>
  // }

  return (
    <div className="dashboard-container">
      <h1>Your Study Dashboard</h1>
      <div className="dashboard-content">
        <div className="timer-section">
          <div className="timer-circle">
            <svg width="140" height="140">
              <circle
                cx="70"
                cy="70"
                r={radius}
                stroke="#444"
                strokeWidth="10"
                fill="none"
              />
              <circle
                cx="70"
                cy="70"
                r={radius}
                stroke="#2ecc71"
                strokeWidth="10"
                fill="none"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="progress-circle"
              />
              <text
                x="50%"
                y="50%"
                dy=".3em"
                textAnchor="middle"
                fill="#ffffff"
                fontSize="20"
                transform="rotate(90, 70, 70)"
              >
                {formatTime(timeLeft)}
              </text>
            </svg>
          </div>
          <button onClick={toggleTimer}>
            {isRunning ? "Pause" : timeLeft === 0 ? "Finished" : "Start"}
          </button>
        </div>
        <h3>Checklist:</h3>
        <ul>
          {dashboardData.checklist.map((task: string, index: number) => (
            <li key={index} className="checklist-item">
              <input
                type="checkbox"
                checked={checkedTasks[index]}
                onChange={() => handleCheckboxChange(index)}
              />
              <span className={checkedTasks[index] ? "completed" : ""}>
                {task}
              </span>
            </li>
          ))}
        </ul>
        {dashboardData.notes && (
          <div>
            <h3>Notes:</h3>
            <p>{dashboardData.notes}</p>
          </div>
        )}
      </div>
      <button onClick={() => window.history.back()}>Back to Study App</button>
    </div>
  );
}

const buttonStyle: React.CSSProperties = {
  padding: "10px 16px",
  backgroundColor: "#3498db",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  fontWeight: "bold",
  cursor: "pointer",
  fontSize: "1rem",
}
