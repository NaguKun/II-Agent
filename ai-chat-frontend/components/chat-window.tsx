"use client"

import { useState, useRef, useEffect } from "react"
import MessageList from "./message-list"
import ChatInput from "./chat-input"
import Sidebar from "./sidebar"
import { Button } from "@/components/ui/button"
import { Download, Lightbulb, Activity } from "lucide-react"
import { apiService, type ContextStats } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  image?: string
  csvData?: string
  visualization?: string // For generated visualizations from CSV analysis
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
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [contextStats, setContextStats] = useState<ContextStats | null>(null)
  const [showContextStats, setShowContextStats] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch context stats periodically
  useEffect(() => {
    if (!sessionId || messages.length === 0) return

    const fetchStats = async () => {
      try {
        const stats = await apiService.getContextStats(sessionId)
        setContextStats(stats)
      } catch (error) {
        console.error("Failed to fetch context stats:", error)
      }
    }

    // Fetch immediately and then every 5 messages
    if (messages.length % 5 === 0) {
      fetchStats()
    }
  }, [sessionId, messages.length])

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

  const handleRegenerateMessage = async (messageId: string) => {
    // Find the last user message before this assistant message
    const messageIndex = messages.findIndex((m) => m.id === messageId)
    if (messageIndex <= 0) return

    // Find the preceding user message
    let userMessageIndex = messageIndex - 1
    while (userMessageIndex >= 0 && messages[userMessageIndex].role !== "user") {
      userMessageIndex--
    }

    if (userMessageIndex < 0) return

    const userMessage = messages[userMessageIndex]

    // Remove the assistant message to regenerate
    setMessages((prev) => prev.filter((m) => m.id !== messageId))

    // Resend the user message
    await sendMessageInternal(userMessage.content, undefined, undefined)
  }

  const sendMessageInternal = async (content: string, imageFile?: File, csvFile?: File) => {
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
          visualization: response.visualization, // Add visualization if present
        }

        setMessages((prev) => [...prev, assistantMessage])

        // Set suggested questions if provided
        if (response.suggested_questions && response.suggested_questions.length > 0) {
          setSuggestedQuestions(response.suggested_questions)
        }
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

    await sendMessageInternal(content, imageFile, csvFile)
  }

  const handleExportConversation = async (format: 'json' | 'markdown' | 'text') => {
    if (!sessionId) {
      toast({
        title: "Error",
        description: "No active session to export",
        variant: "destructive",
      })
      return
    }

    try {
      const blob = await apiService.exportConversation(sessionId, format)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const extension = format === 'markdown' ? 'md' : format === 'text' ? 'txt' : 'json'
      a.download = `conversation_${sessionId}.${extension}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast({
        description: `Conversation exported as ${format}`,
        duration: 2000,
      })
    } catch (error) {
      toast({
        title: "Export failed",
        description: error instanceof Error ? error.message : "Failed to export conversation",
        variant: "destructive",
      })
    }
  }

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question, undefined, undefined)
    setSuggestedQuestions([]) // Clear suggestions after using one
  }

  return (
    <div className="flex h-full gap-0">
      <Sidebar
        mode={mode}
        setMode={setMode}
        modes={CHAT_MODES}
        isConnected={isConnected}
      />
      <div className="flex-1 flex flex-col relative lg:pl-0 max-w-5xl mx-auto w-full px-3 sm:px-4 md:px-6 lg:px-8">
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

        {/* Export button and Context Stats */}
        {messages.length > 0 && sessionId && (
          <div className="absolute top-4 left-4 z-10">
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExportConversation('markdown')}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                Export MD
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExportConversation('text')}
                className="text-xs"
              >
                <Download className="h-3 w-3 mr-1" />
                Export TXT
              </Button>

              {/* Context Window Indicator */}
              {contextStats && (
                <Button
                  variant={contextStats.within_limits ? "outline" : "destructive"}
                  size="sm"
                  onClick={() => setShowContextStats(!showContextStats)}
                  className="text-xs"
                  title="Context window status"
                >
                  <Activity className="h-3 w-3 mr-1" />
                  {contextStats.total_messages} msgs
                </Button>
              )}
            </div>

            {/* Context Stats Dropdown */}
            {showContextStats && contextStats && (
              <div className="absolute top-10 left-0 bg-card border rounded-lg shadow-lg p-3 text-xs w-64 animate-in fade-in slide-in-from-top-2">
                <div className="font-semibold mb-2 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Context Window Status
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Messages:</span>
                    <span className="font-medium">
                      {contextStats.total_messages} / {contextStats.max_messages}
                    </span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Tokens:</span>
                    <span className="font-medium">
                      ~{contextStats.total_tokens.toLocaleString()}
                    </span>
                  </div>

                  {/* Progress bars */}
                  <div className="space-y-1">
                    <div className="text-muted-foreground text-[10px]">Message usage</div>
                    <div className="w-full bg-muted rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full transition-all ${
                          contextStats.message_usage_percent > 80
                            ? "bg-red-500"
                            : contextStats.message_usage_percent > 60
                            ? "bg-yellow-500"
                            : "bg-green-500"
                        }`}
                        style={{ width: `${Math.min(100, contextStats.message_usage_percent)}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-muted-foreground">
                      {contextStats.message_usage_percent.toFixed(1)}%
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="text-muted-foreground text-[10px]">Token usage</div>
                    <div className="w-full bg-muted rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full transition-all ${
                          contextStats.token_usage_percent > 80
                            ? "bg-red-500"
                            : contextStats.token_usage_percent > 60
                            ? "bg-yellow-500"
                            : "bg-green-500"
                        }`}
                        style={{ width: `${Math.min(100, contextStats.token_usage_percent)}%` }}
                      />
                    </div>
                    <div className="text-[10px] text-muted-foreground">
                      {contextStats.token_usage_percent.toFixed(1)}%
                    </div>
                  </div>

                  {contextStats.sliding_window_enabled && (
                    <div className="pt-2 border-t">
                      <div className="text-[10px] text-green-600 dark:text-green-400">
                        ✓ Sliding window active
                      </div>
                      <div className="text-[10px] text-muted-foreground">
                        Keeping conversation within limits
                      </div>
                    </div>
                  )}

                  {!contextStats.within_limits && (
                    <div className="pt-2 border-t text-amber-600 dark:text-amber-400 text-[10px]">
                      ⚠ Context optimization in use
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Messages when conversation started */}
        {messages.length > 0 && (
          <MessageList
            messages={messages}
            isLoading={isLoading}
            onRegenerateMessage={handleRegenerateMessage}
            ref={messagesEndRef}
          />
        )}

        {/* Suggested questions for CSV */}
        {suggestedQuestions.length > 0 && (
          <div className="px-3 md:px-4 lg:px-6 pb-2">
            <div className="max-w-3xl mx-auto">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                <span className="text-sm font-medium text-muted-foreground">
                  Suggested questions:
                </span>
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestedQuestions.map((question, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestedQuestion(question)}
                    disabled={isLoading}
                    className="text-xs hover:bg-primary hover:text-primary-foreground transition-colors"
                  >
                    {question}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Chat Input at bottom */}
        <div className="p-2 sm:p-3 md:p-4 lg:p-6 pb-3 sm:pb-4 md:pb-6">
          <ChatInput onSendMessage={handleSendMessage} mode={mode} disabled={isLoading} />
        </div>
      </div>
    </div>
  )
}
