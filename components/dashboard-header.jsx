"use client"

import Link from "next/link"
import { ShieldCheck, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"

export function DashboardHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold tracking-tight">QuantumGuard AI</span>
        </div>

        <nav className="hidden md:flex items-center gap-6">
          <Link href="/" className="text-sm font-medium transition-colors hover:text-primary">
            Overview
          </Link>
          <Link href="/detection" className="text-sm font-medium text-primary">
            Detection
          </Link>
        </nav>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm font-medium text-emerald-600 dark:text-emerald-400">
            <Activity className="h-4 w-4 animate-pulse" />
            <span>System Active</span>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link href="/">Back to Home</Link>
          </Button>
        </div>
      </div>
    </header>
  )
}
