"use client"

import { DashboardHeader } from "@/components/dashboard-header"
import { DetectionInterface } from "@/components/detection-interface"

export default function DetectionPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <DashboardHeader />
      <main className="container mx-auto py-8">
        <DetectionInterface />
      </main>
    </div>
  )
}
