// app/dashboard/page.tsx
"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [checkedTasks, setCheckedTasks] = useState<boolean[]>([]);
  const [initialTime, setInitialTime] = useState<number>(0);

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
  }, [isRunning, timeLeft, router, checkedTasks]); // Removed focusSeconds and initialTime from dependencies

  // Format time as MM:SS
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

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