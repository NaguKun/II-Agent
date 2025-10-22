"use client"

import { useState, useRef, useEffect } from "react"
import MessageList from "./message-list"
import ChatInput from "./chat-input"
import Sidebar from "./sidebar"
import { apiService } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  image?: string
  csvData?: string
  isStreaming?: boolean
}

export interface ChatMode {
  type: "text" | "image" | "csv"
  label: string
}

const CHAT_MODES: ChatMode[] = [
  { type: "text", label: "Chat" },
  { type: "image", label: "Image" },
  { type: "csv", label: "CSV" },
]

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([])
  const [mode, setMode] = useState<"text" | "image" | "csv">("text")
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        // Check API health
        const healthy = await apiService.healthCheck()
        if (!healthy) {
          toast({
            title: "Connection Error",
            description: "Unable to connect to backend. Using offline mode.",
            variant: "destructive",
          })
          return
        }

        // Create session
        const response = await apiService.createSession()
        setSessionId(response.session_id)
        setIsConnected(true)

        toast({
          title: "Connected",
          description: "Successfully connected to AI backend.",
        })
      } catch (error) {
        console.error("Failed to initialize session:", error)
        toast({
          title: "Session Error",
          description: "Failed to create session. Some features may be limited.",
          variant: "destructive",
        })
      }
    }

    initSession()
  }, [toast])

  const handleSendMessage = async (content: string, imageFile?: File, csvFile?: File) => {
    if (!content.trim()) return

    // Add user message with file preview
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
      image: imageFile ? URL.createObjectURL(imageFile) : undefined,
      csvData: csvFile ? `📄 ${csvFile.name}` : undefined,
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      if (!sessionId || !isConnected) {
        throw new Error("Not connected to backend")
      }

      if (imageFile) {
        // Handle image upload
        const response = await apiService.sendImageMessage(sessionId, content, imageFile)

        const assistantMessage: Message = {
          id: response.message_id,
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else if (csvFile) {
        // Handle CSV upload
        const response = await apiService.sendCsvMessage(sessionId, content, csvFile)

        const assistantMessage: Message = {
          id: response.message_id,
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
      } else {
        // Handle text message with streaming
        const streamingMessageId = `streaming-${Date.now()}`
        const streamingMessage: Message = {
          id: streamingMessageId,
          role: "assistant",
          content: "",
          timestamp: new Date(),
          isStreaming: true,
        }

        setMessages((prev) => [...prev, streamingMessage])

        await apiService.sendMessageStream(
          sessionId,
          content,
          // On chunk received
          (chunk: string) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === streamingMessageId
                  ? { ...msg, content: msg.content + chunk }
                  : msg
              )
            )
          },
          // On complete
          (messageId: string) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === streamingMessageId
                  ? { ...msg, id: messageId, isStreaming: false }
                  : msg
              )
            )
          },
          // On error
          (error: string) => {
            toast({
              title: "Error",
              description: error,
              variant: "destructive",
            })
            setMessages((prev) => prev.filter((msg) => msg.id !== streamingMessageId))
          }
        )
      }
    } catch (error) {
      console.error("Failed to send message:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to send message",
        variant: "destructive",
      })

      // Fallback response for demo purposes
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm having trouble connecting to the backend. Please make sure the API server is running at http://localhost:8000",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-full gap-0">
      <Sidebar
        mode={mode}
        setMode={setMode}
        modes={CHAT_MODES}
        isConnected={isConnected}
      />
      <div className="flex-1 flex flex-col relative lg:pl-0 max-w-7xl mx-auto w-full px-4 md:px-6 lg:px-8">
        {/* Empty State with Greeting */}
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center p-4 md:p-6">
            <div className="text-center space-y-3 md:space-y-4 mb-8 max-w-2xl">
              <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Hello, Noah!
              </h1>
              <p className="text-sm md:text-base lg:text-lg text-muted-foreground">
                What can I do for you today?
              </p>
            </div>
          </div>
        )}

        {/* Messages when conversation started */}
        {messages.length > 0 && (
          <MessageList messages={messages} isLoading={isLoading} ref={messagesEndRef} />
        )}

        {/* Chat Input at bottom */}
        <div className="p-3 md:p-4 lg:p-6 pb-4 md:pb-6">
          <ChatInput onSendMessage={handleSendMessage} mode={mode} disabled={isLoading} />
        </div>
      </div>
    </div>
  )
}
