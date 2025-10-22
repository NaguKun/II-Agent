"use client"

import { useState, useEffect } from "react"
import ChatWindow from "@/components/chat-window"
import ThemeToggle from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"

export default function Home() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="flex flex-col h-screen bg-background text-foreground">
      {/* Close button in top right corner */}
      <div className="absolute top-4 right-4 z-50 flex items-center gap-2">
        <ThemeToggle />
        <Button
          variant="ghost"
          size="icon"
          className="rounded-full hover:bg-muted"
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      <main className="flex-1 overflow-hidden">
        <ChatWindow />
      </main>
    </div>
  )
}
