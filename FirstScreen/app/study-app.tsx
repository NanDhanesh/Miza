"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Mic, Square } from "lucide-react"
import "./styles.css"

export default function StudyApp() {
  const [isRecording, setIsRecording] = useState(false)
  const [greeting, setGreeting] = useState("Good Morning User")
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>(0)
  const recognitionRef = useRef<any>(null) //<n>
  const [transcript, setTranscript] = useState("") //NEW


  useEffect(() => {
    // Update greeting based on time of day
    const hours = new Date().getHours()
    if (hours >= 5 && hours < 12) {
      setGreeting("Good Morning User")
    } else if (hours >= 12 && hours < 18) {
      setGreeting("Good Afternoon User")
    } else {
      setGreeting("Good Evening User")
    }

    // Initialize audio waves
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const resizeCanvas = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    resizeCanvas()
    window.addEventListener("resize", resizeCanvas)

    // Audio wave animation
    const waves = Array.from({ length: 5 }, (_, i) => ({
      amplitude: 20 + i * 5,
      frequency: 0.01 - i * 0.002,
      speed: 0.02 + i * 0.005,
      offset: Math.random() * Math.PI * 2,
      color: `rgba(100, 150, 200, ${0.1 - i * 0.015})`,
    }))

    const animate = () => {
      if (!ctx || !canvas) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      waves.forEach((wave) => {
        ctx.beginPath()
        ctx.moveTo(0, canvas.height / 2)

        for (let x = 0; x < canvas.width; x++) {
          const y =
            canvas.height / 2 + Math.sin(x * wave.frequency + wave.offset) * wave.amplitude * (isRecording ? 1.5 : 1)
          ctx.lineTo(x, y)
        }

        ctx.strokeStyle = wave.color
        ctx.lineWidth = 2
        ctx.stroke()

        // Update wave offset for animation
        wave.offset += wave.speed
      })

      animationRef.current = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", resizeCanvas)
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isRecording])

  // const toggleRecording = () => {
  //   setIsRecording(!isRecording)
  // }

  const toggleRecording = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      alert("Speech Recognition not supported in this browser.")
      return
    }

    if (!recognitionRef.current) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = "en-US"

      recognition.onresult = (event: any) => {
        const text = Array.from(event.results)
          .map((res: any) => res[0].transcript)
          .join("")
        setTranscript(text)
      }
      

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error", event.error)
      }

      recognitionRef.current = recognition
    }

    if (!isRecording) {
      recognitionRef.current.start()
    } else {
      recognitionRef.current.stop()
    }

    setIsRecording(!isRecording)
  }

  const router = useRouter()

  const handleSubmitTranscript = async (text: string) => {
    console.log("Submitting transcript:", text)
  
    try {
      const response = await fetch("/api/generate-dashboard", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: text }),
      })
  
      const data = await response.json()
      console.log("LLM response:", data)
  
      const encodedResult = encodeURIComponent(data.result || "")
      router.push(`/dashboard?result=${encodedResult}`)
      
    } catch (error) {
      console.error("Submission failed", error)
    }
  }
  

  return (
    <div className="app-container">
      <canvas ref={canvasRef} className="wave-canvas"></canvas>
      <div className="content">
        <h1 className="greeting">{greeting}</h1>
        <button className={`recording-button ${isRecording ? "recording" : ""}`} onClick={toggleRecording}>
          {isRecording ? (
            <>
              <Square className="button-icon" />
              Stop Recording
            </>
          ) : (
            <>
              <Mic className="button-icon" />
              Start Recording
            </>
          )}
        </button>
  
        {/* Editable Transcript Section */}
        <label className="transcript-label">Edit your study goals:</label>
        <textarea
          className="transcript-box"
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          rows={6}
        />
        <button className="submit-transcript" onClick={() => handleSubmitTranscript(transcript)}>
          Generate Study Dashboard
        </button>
      </div>
    </div>
  )
  
}

