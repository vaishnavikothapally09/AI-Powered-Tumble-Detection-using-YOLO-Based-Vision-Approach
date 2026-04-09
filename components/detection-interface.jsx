"use client"

import { useState, useEffect } from "react"
import { Mail, AlertCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

export function DetectionInterface() {
  const [isDetecting, setIsDetecting] = useState(false)
  const [email, setEmail] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState("")

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (isDetecting) {
        stopDetection()
      }
    }
  }, [isDetecting])

  const startDetection = async () => {
    if (!email || !email.includes("@")) {
      setError("Please enter a valid email address")
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_BASE_URL}/api/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to start detection")
      }

      setIsDetecting(true)
      setStatus("Detection started successfully")
    } catch (err) {
      setError(err.message || "Failed to connect to backend server")
      console.error("Error starting detection:", err)
    } finally {
      setLoading(false)
    }
  }

  const stopDetection = async () => {
    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_BASE_URL}/api/stop`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to stop detection")
      }

      setIsDetecting(false)
      setStatus("Detection stopped")
      setEmail("")
    } catch (err) {
      setError(err.message || "Failed to stop detection")
      console.error("Error stopping detection:", err)
    } finally {
      setLoading(false)
    }
  }

  const testEmail = async () => {
    if (!email || !email.includes("@")) {
      setError("Please enter a valid email address")
      return
    }

    setLoading(true)
    setError("")

    try {
      const response = await fetch(`${API_BASE_URL}/api/test_email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Failed to send test email")
      }

      setStatus("Test email sent successfully! Please check your inbox.")
    } catch (err) {
      setError(err.message || "Failed to send test email")
      console.error("Error sending test email:", err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="max-w-4xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Real-time Tumble Detection</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {status && !error && (
              <Alert>
                <AlertDescription>{status}</AlertDescription>
              </Alert>
            )}

            {!isDetecting ? (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="caretaker-email">Caretaker Email ID</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="caretaker-email"
                      type="email"
                      placeholder="email@example.com"
                      className="pl-10"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                    />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Alerts will be sent to this email when a tumble is detected
                  </p>
                </div>

                <div className="flex gap-4">
                  <Button
                    className="flex-1"
                    onClick={startDetection}
                    disabled={loading || !email}
                  >
                    {loading ? "Starting..." : "Start Detection"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={testEmail}
                    disabled={loading || !email}
                  >
                    Test Email
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
                <div className="w-full bg-slate-200 rounded-lg overflow-hidden aspect-video">
                  <img
                    src={`${API_BASE_URL}/api/video_feed`}
                    alt="Live Camera Feed"
                    className="w-full h-full object-contain"
                  />
                </div>

                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div>
                    <p className="font-semibold">Detection Active</p>
                    <p className="text-sm text-muted-foreground">
                      Email alerts will be sent to: {email}
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    onClick={stopDetection}
                    disabled={loading}
                  >
                    {loading ? "Stopping..." : "Stop Detection"}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
