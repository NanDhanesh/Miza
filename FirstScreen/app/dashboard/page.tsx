"use client"

import { useSearchParams } from "next/navigation"
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

  // Parse JSON and initialize timer + checklist
  useEffect(() => {
    if (resultRaw) {
      try {
        const jsonString = resultRaw.replace(/```json|```/g, "").trim()
        const parsed: DashboardData = JSON.parse(jsonString)
        setDashboard(parsed)
        setCountdown(parsed.timer * 60) // convert minutes to seconds
        setChecklistState(new Array(parsed.checklist.length).fill(false))
      } catch (err) {
        console.error("Failed to parse dashboard result:", err)
      }
    }
  }, [resultRaw])

  // Countdown effect
  useEffect(() => {
    if (countdown <= 0) return

    const interval = setInterval(() => {
      setCountdown((prev) => prev - 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [countdown])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const toggleChecklistItem = (index: number) => {
    setChecklistState((prev) => {
      const updated = [...prev]
      updated[index] = !updated[index]
      return updated
    })
  }

  if (!dashboard) {
    return <p style={{ padding: "2rem" }}>Loading dashboard...</p>
  }

  return (
    <div className="dashboard-light">
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "0 auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "2rem", marginBottom: "1rem" }}>🎯 Your Study Dashboard</h1>

      <div style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.5rem" }}>⏱ Focus Timer</h2>
        <div
          style={{
            fontSize: "2.5rem",
            fontWeight: "bold",
            marginTop: "0.5rem",
            color: countdown <= 60 ? "red" : "black",
          }}
        >
          {formatTime(countdown)}
        </div>
      </div>

      <div>
        <h3 style={{ fontSize: "1.3rem", marginBottom: "0.5rem" }}>✅ Checklist</h3>
        <ul style={{ listStyle: "none", padding: 0 }}>
          {dashboard.checklist.map((item, index) => (
            <li key={index} style={{ marginBottom: "10px", display: "flex", alignItems: "center" }}>
              <input
                type="checkbox"
                checked={checklistState[index]}
                onChange={() => toggleChecklistItem(index)}
                style={{ marginRight: "10px" }}
              />
              <span style={{ textDecoration: checklistState[index] ? "line-through" : "none" }}>{item}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
    </div>
  )
}

