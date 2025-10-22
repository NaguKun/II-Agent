"use client"

import React, { forwardRef, useMemo } from "react"
import type { Message } from "./chat-window"
import MessageBubble from "./message-bubble"
import { Loader2 } from "lucide-react"

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  onRegenerateMessage?: (messageId: string) => void
}

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(({ messages, isLoading, onRegenerateMessage }, ref) => {
  // Memoize message elements to prevent recreation on every render
  const messageElements = useMemo(() => {
    return messages.map((message, index) => {
      // Only show regenerate for the last assistant message
      const isLastAssistantMessage =
        message.role === "assistant" &&
        index === messages.length - 1 &&
        !message.isStreaming

      return (
        <MessageBubble
          key={message.id}
          message={message}
          onRegenerate={
            isLastAssistantMessage && onRegenerateMessage
              ? () => onRegenerateMessage(message.id)
              : undefined
          }
        />
      )
    })
  }, [messages, onRegenerateMessage])

  return (
    <div className="flex-1 overflow-y-auto mb-4 space-y-4 md:space-y-5 py-4 custom-scrollbar">
      {messageElements}
      {isLoading && (
        <div className="flex justify-start animate-in fade-in slide-in-from-bottom-2 duration-500">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-accent/20 rounded-lg blur-md group-hover:blur-lg transition-all duration-300"></div>
            <div className="relative flex items-center gap-3 px-5 py-3 rounded-lg bg-gradient-to-br from-card via-card to-card/95 border-2 border-primary/20 shadow-lg backdrop-blur-sm">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <span className="text-sm font-medium bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent animate-gradient">
                AI is thinking...
              </span>
            </div>
          </div>
        </div>
      )}
      <div ref={ref} />
    </div>
  )
})

MessageList.displayName = "MessageList"

// Memoize the entire component to prevent unnecessary re-renders
export default React.memo(MessageList)
