"use client"

import Link from "next/link"
import { ShieldCheck, ArrowRight, Activity, Brain, Users, Lightbulb } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Navigation */}
      <header className="px-4 lg:px-6 h-16 flex items-center border-b">
        <Link className="flex items-center justify-center gap-2" href="/">
          <ShieldCheck className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">QuantumGuard AI</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/detection">
            Detection
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#features">
            Features
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-slate-50">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  Real-Time Human Fall Detection
                </h1>
                <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                  Next-generation AI monitoring designed for healthcare and elderly monitoring. Detecting falls and
                  tumbles with quantum-enhanced precision.
                </p>
              </div>
              <div className="space-x-4">
                <Button size="lg" asChild>
                  <Link href="/detection">
                    Start Detection <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="w-full py-12 md:py-24 lg:py-32">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-3 lg:gap-12">
              <Card className="border-none shadow-none text-center">
                <CardHeader>
                  <div className="mx-auto bg-primary/10 p-3 rounded-full w-fit mb-4">
                    <Activity className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>System Architecture</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Modern neural network architecture optimized for real-time video stream processing and event
                    classification.
                  </p>
                </CardContent>
              </Card>
              <Card className="border-none shadow-none text-center">
                <CardHeader>
                  <div className="mx-auto bg-primary/10 p-3 rounded-full w-fit mb-4">
                    <Brain className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>Technologies Used</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Leveraging YOLO for computer vision, React for the frontend interface, and Flask for backend
                    processing.
                  </p>
                </CardContent>
              </Card>
              <Card className="border-none shadow-none text-center">
                <CardHeader>
                  <div className="mx-auto bg-primary/10 p-3 rounded-full w-fit mb-4">
                    <Users className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle>Applications</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Ideal for hospitals, assisted living facilities, and smart homes to provide immediate alert response
                    during emergencies.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Future Scope Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-slate-900 text-white">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="bg-white/10 p-2 rounded-lg mb-4">
                <Lightbulb className="h-8 w-8 text-yellow-400" />
              </div>
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Future Scope</h2>
              <p className="max-w-[800px] text-slate-300 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Integration with wearable IoT devices, multi-camera synchronized detection, and predictive behavior
                analysis to prevent falls before they happen.
              </p>
            </div>
          </div>
        </section>
      </main>

      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
        <p className="text-xs text-muted-foreground">© 2026 QuantumGuard AI. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Privacy Policy
          </Link>
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Contact Support
          </Link>
        </nav>
      </footer>
    </div>
  )
}
