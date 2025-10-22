"use client"

import React, { useState } from "react"
import type { Message } from "./chat-window"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import ReactMarkdown from "react-markdown"
import { format } from "date-fns"
import { Bot, User, Copy, Check, RotateCcw } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface MessageBubbleProps {
  message: Message
  onRegenerate?: () => void
}

function MessageBubble({ message, onRegenerate }: MessageBubbleProps) {
  const isUser = message.role === "user"
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      toast({
        description: "Message copied to clipboard",
        duration: 2000,
      })
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast({
        description: "Failed to copy message",
        variant: "destructive",
        duration: 2000,
      })
    }
  }

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-3 duration-500 zoom-in-95`}>
      {/* Avatar */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg ring-2 ring-primary/50 ring-offset-2 ring-offset-background animate-in zoom-in-50 duration-300">
          <Bot className="h-4 w-4 md:h-5 md:w-5 text-white" />
        </div>
      )}

      {/* Message Content */}
      <div className={`max-w-sm md:max-w-md lg:max-w-2xl ${isUser ? "order-2" : "order-1"} group`}>
        <div className="relative">
          {!isUser && (
            <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-accent/20 rounded-lg blur-lg opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
          )}
          <Card
            className={`relative px-3 py-2.5 md:px-4 md:py-3 rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl transform hover:-translate-y-0.5 ${
              isUser
                ? "bg-gradient-to-br from-primary via-primary to-primary text-primary-foreground rounded-br-none border-none shadow-primary/30"
                : "bg-gradient-to-br from-card via-card to-card/95 border-2 border-primary/20 rounded-bl-none backdrop-blur-sm"
            }`}
          >
          {message.image && (
            <div className="mb-3 relative group/image">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg blur-md group-hover/image:blur-lg transition-all duration-300"></div>
              <div className={`relative rounded-lg overflow-hidden border-2 shadow-xl ring-2 ring-offset-2 ring-offset-background ${
                isUser
                  ? "border-white/30 ring-white/20"
                  : "border-primary/30 ring-primary/30"
              }`}>
                <img src={message.image || "/placeholder.svg"} alt="Uploaded" className="w-full h-auto object-cover max-h-56 transform group-hover/image:scale-105 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover/image:opacity-100 transition-opacity duration-300"></div>
              </div>
            </div>
          )}

          {message.csvData && (
            <div className="mb-3 relative group/csv">
              <div className="absolute inset-0 bg-gradient-to-br from-secondary/20 via-accent/20 to-primary/20 rounded-lg blur-md group-hover/csv:blur-lg transition-all duration-300"></div>
              <div className={`relative p-3 rounded-lg border-2 text-xs font-mono overflow-x-auto max-h-32 backdrop-blur-sm shadow-lg ring-2 ring-offset-2 ring-offset-background ${
                isUser
                  ? "bg-white/20 border-white/30 ring-white/20"
                  : "bg-muted/50 border-secondary/40 ring-secondary/30"
              }`}>
                <div className={`flex items-center gap-2 mb-2 font-bold ${
                  isUser ? "text-white" : "text-secondary-foreground"
                }`}>
                  <svg className="w-4 h-4 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  CSV Data
                </div>
                <pre className={`whitespace-pre-wrap break-words leading-relaxed ${
                  isUser ? "text-white/90" : "text-gray-700 dark:text-gray-300"
                }`}>
                  {message.csvData.split("\n").slice(0, 5).join("\n")}
                  {message.csvData.split("\n").length > 5 && "\n..."}
                </pre>
              </div>
            </div>
          )}

          {message.visualization && (
            <div className="mb-3 relative group/viz">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-pink-500/20 rounded-lg blur-md group-hover/viz:blur-lg transition-all duration-300"></div>
              <div className={`relative rounded-lg overflow-hidden border-2 shadow-xl ring-2 ring-offset-2 ring-offset-background ${
                isUser
                  ? "border-white/30 ring-white/20"
                  : "border-blue-500/30 ring-blue-500/30"
              }`}>
                <div className={`flex items-center gap-2 px-3 py-2 font-semibold text-sm border-b ${
                  isUser
                    ? "bg-white/10 border-white/20 text-white"
                    : "bg-blue-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400"
                }`}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Data Visualization
                </div>
                <img
                  src={message.visualization}
                  alt="Data Visualization"
                  className="w-full h-auto object-contain bg-white dark:bg-gray-900 transform group-hover/viz:scale-[1.02] transition-transform duration-500"
                />
              </div>
            </div>
          )}

          <div className={`prose prose-sm max-w-none dark:prose-invert ${!isUser && 'bg-gradient-to-br from-transparent via-primary/5 to-accent/5 rounded-lg p-0.5'}`}>
            {message.isStreaming && !message.content ? (
              // Typing indicator when streaming starts
              <div className="flex gap-1.5 py-3 px-1">
                <div className="w-2.5 h-2.5 bg-gradient-to-br from-primary to-accent rounded-full animate-bounce shadow-lg" style={{ animationDelay: "0ms" }} />
                <div className="w-2.5 h-2.5 bg-gradient-to-br from-primary to-primary/70 rounded-full animate-bounce shadow-lg" style={{ animationDelay: "150ms" }} />
                <div className="w-2.5 h-2.5 bg-gradient-to-br from-accent to-primary rounded-full animate-bounce shadow-lg" style={{ animationDelay: "300ms" }} />
              </div>
            ) : (
              <ReactMarkdown
                components={{
                  p: ({ ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                  ul: ({ ...props }) => <ul className="list-disc list-inside mb-2" {...props} />,
                  ol: ({ ...props }) => <ol className="list-decimal list-inside mb-2" {...props} />,
                  code: ({ inline, ...props }: any) =>
                    inline ? (
                      <code
                        className={`px-1.5 py-0.5 rounded text-xs font-mono ${
                          isUser ? "bg-primary-foreground/20" : "bg-muted"
                        }`}
                        {...props}
                      />
                    ) : (
                      <code
                        className={`block p-3 rounded text-xs font-mono overflow-x-auto mb-2 ${
                          isUser ? "bg-primary-foreground/20" : "bg-muted"
                        }`}
                        {...props}
                      />
                    ),
                  pre: ({ ...props }) => (
                    <pre
                      className={`p-3 rounded overflow-x-auto mb-2 ${
                        isUser ? "bg-primary-foreground/20" : "bg-muted"
                      }`}
                      {...props}
                    />
                  ),
                  a: ({ ...props }) => (
                    <a className={`underline hover:opacity-80 ${isUser ? "text-primary-foreground" : "text-accent"}`} {...props} />
                  ),
                  strong: ({ ...props }) => <strong className="font-semibold" {...props} />,
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>
          </Card>
        </div>

        <div className={`flex items-center gap-2 mt-1 ${isUser ? "justify-end" : "justify-start"}`}>
          <div className="text-xs text-muted-foreground">
            {message.timestamp instanceof Date && !isNaN(message.timestamp.getTime())
              ? format(message.timestamp, "HH:mm")
              : format(new Date(), "HH:mm")}
            {message.isStreaming && <span className="ml-1 italic">• typing...</span>}
          </div>

          {/* Action buttons for assistant messages */}
          {!isUser && !message.isStreaming && message.content && (
            <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6 hover:bg-muted"
                onClick={handleCopy}
                title="Copy message"
              >
                {copied ? (
                  <Check className="h-3 w-3 text-green-500" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </Button>
              {onRegenerate && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 hover:bg-muted"
                  onClick={onRegenerate}
                  title="Regenerate response"
                >
                  <RotateCcw className="h-3 w-3" />
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-primary via-primary to-primary flex items-center justify-center shadow-lg ring-2 ring-primary/50 ring-offset-2 ring-offset-background animate-in zoom-in-50 duration-300">
          <User className="h-4 w-4 md:h-5 md:w-5 text-white" />
        </div>
      )}
    </div>
  )
}

// Memoize to prevent re-renders when message hasn't changed
export default React.memo(MessageBubble, (prevProps, nextProps) => {
  // Only re-render if message content, streaming status, visualization, or timestamp changed
  return (
    prevProps.message.id === nextProps.message.id &&
    prevProps.message.content === nextProps.message.content &&
    prevProps.message.isStreaming === nextProps.message.isStreaming &&
    prevProps.message.visualization === nextProps.message.visualization
  )
})
