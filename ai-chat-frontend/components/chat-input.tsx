"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Send, Upload, X, Image, FileText, Video, Presentation, Globe, Code } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (content: string, imageFile?: File, csvFile?: File) => void
  mode: "text" | "image" | "csv"
  disabled?: boolean
  selectedModel?: string
}

export default function ChatInput({ onSendMessage, mode, disabled, selectedModel = "claude-sonnet-4@20250514" }: ChatInputProps) {
  const [input, setInput] = useState("")
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [csvPreview, setCsvPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const csvInputRef = useRef<HTMLInputElement>(null)
  const generalFileInputRef = useRef<HTMLInputElement>(null)

  const actionButtons = [
    { icon: Image, label: "Generate Image / Video", variant: "outline" as const },
    { icon: Presentation, label: "Create Slide", variant: "outline" as const },
    { icon: Globe, label: "Create a Website", variant: "outline" as const },
    { icon: Code, label: "Codex", variant: "outline" as const },
  ]

  const handleSend = () => {
    if (!input.trim()) return
    onSendMessage(input, imageFile || undefined, csvFile || undefined)
    setInput("")
    setImageFile(null)
    setImagePreview(null)
    setCsvFile(null)
    setCsvPreview(null)
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleCsvUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setCsvFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setCsvPreview(event.target?.result as string)
      }
      reader.readAsText(file)
    }
  }

  const handleGeneralFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Check if it's an image
      if (file.type.startsWith('image/')) {
        setImageFile(file)
        const reader = new FileReader()
        reader.onload = (event) => {
          setImagePreview(event.target?.result as string)
        }
        reader.readAsDataURL(file)
      }
      // Check if it's a CSV
      else if (file.name.endsWith('.csv') || file.type === 'text/csv') {
        setCsvFile(file)
        const reader = new FileReader()
        reader.onload = (event) => {
          setCsvPreview(event.target?.result as string)
        }
        reader.readAsText(file)
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="space-y-3 md:space-y-4 w-full max-w-3xl mx-auto">
      {/* Model Selector */}
      <div className="flex justify-center">
        <div className="inline-flex items-center gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-primary text-primary-foreground rounded-full text-xs md:text-sm font-medium">
          <span className="truncate max-w-[200px] md:max-w-none">{selectedModel}</span>
          <Button variant="ghost" size="sm" className="h-4 w-4 md:h-5 md:w-5 p-0 rounded-full hover:bg-white/20">
            <X className="h-2.5 w-2.5 md:h-3 md:w-3" />
          </Button>
        </div>
      </div>

      <Card className="bg-card border-border p-3 md:p-4 space-y-3 shadow-lg">
        {/* Image Preview */}
        {imagePreview && (
          <div className="relative inline-block animate-in fade-in slide-in-from-bottom-4 duration-500 zoom-in-95">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-accent/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative">
                <img
                  src={imagePreview || "/placeholder.svg"}
                  alt="Preview"
                  className="max-h-32 md:max-h-40 rounded-lg border-2 border-primary/30 shadow-2xl transform group-hover:scale-[1.02] transition-all duration-300 ring-2 ring-primary/50 ring-offset-2 ring-offset-background"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              </div>
            </div>
            <button
              onClick={() => {
                setImageFile(null)
                setImagePreview(null)
              }}
              className="absolute -top-3 -right-3 bg-gradient-to-br from-destructive to-destructive text-destructive-foreground rounded-full p-1.5 hover:scale-110 hover:rotate-90 transition-all duration-300 shadow-lg ring-2 ring-destructive/50 hover:ring-destructive/70"
            >
              <X className="h-4 w-4 md:h-5 md:w-5" />
            </button>
          </div>
        )}

        {/* CSV Preview */}
        {csvPreview && (
          <div className="relative animate-in fade-in slide-in-from-bottom-4 duration-500 zoom-in-95">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-br from-secondary/20 via-accent/20 to-primary/20 rounded-lg blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative bg-muted/50 p-3 md:p-4 rounded-lg border-2 border-secondary/30 shadow-2xl max-h-24 md:max-h-32 overflow-y-auto backdrop-blur-sm ring-2 ring-secondary/50 ring-offset-2 ring-offset-background">
                <div className="flex items-center gap-2 mb-2 text-secondary-foreground font-bold">
                  <FileText className="h-4 w-4 animate-pulse" />
                  <span className="text-sm">CSV Data Preview</span>
                </div>
                <pre className="whitespace-pre-wrap break-words text-xs font-mono text-foreground leading-relaxed">
                  {csvPreview.split("\n").slice(0, 4).join("\n")}
                  {csvPreview.split("\n").length > 4 && "\n..."}
                </pre>
              </div>
            </div>
            <button
              onClick={() => {
                setCsvFile(null)
                setCsvPreview(null)
              }}
              className="absolute -top-3 -right-3 bg-gradient-to-br from-destructive to-destructive text-destructive-foreground rounded-full p-1.5 hover:scale-110 hover:rotate-90 transition-all duration-300 shadow-lg ring-2 ring-destructive/50 hover:ring-destructive/70"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Main Input */}
        <div className="flex gap-1.5 md:gap-2 items-start">
          {/* File upload buttons on the left */}
          <div className="flex gap-1">
            {mode === "image" && (
              <>
                <input ref={fileInputRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                  title="Upload image"
                  disabled={disabled}
                  className="hover:bg-primary/10 transition-colors h-8 w-8 md:h-10 md:w-10"
                >
                  <Upload className="h-3 w-3 md:h-4 md:w-4" />
                </Button>
              </>
            )}
            {mode === "csv" && !csvPreview && (
              <>
                <input ref={csvInputRef} type="file" accept=".csv" onChange={handleCsvUpload} className="hidden" />
                <Button
                  size="icon"
                  variant="outline"
                  onClick={() => csvInputRef.current?.click()}
                  title="Upload CSV"
                  disabled={disabled}
                  className="hover:bg-primary/10 transition-colors h-8 w-8 md:h-10 md:w-10"
                >
                  <Upload className="h-3 w-3 md:h-4 md:w-4" />
                </Button>
              </>
            )}
            <>
              <input
                ref={generalFileInputRef}
                type="file"
                accept="image/*,.csv"
                onChange={handleGeneralFileUpload}
                className="hidden"
              />
              <Button
                size="icon"
                variant="outline"
                onClick={() => generalFileInputRef.current?.click()}
                title="Attach file"
                disabled={disabled}
                className="hover:bg-primary/10 transition-colors h-8 w-8 md:h-10 md:w-10"
              >
                <FileText className="h-3 w-3 md:h-4 md:w-4" />
              </Button>
            </>
          </div>

          {/* Textarea */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="build me a"
            disabled={disabled}
            className="flex-1 px-3 md:px-4 py-2 md:py-3 rounded-lg border border-border bg-input text-foreground placeholder-muted-foreground text-xs md:text-sm resize-none min-h-[100px] md:min-h-[120px] focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow disabled:opacity-50"
          />

          {/* Send button on the right */}
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className="bg-primary hover:bg-primary/90 text-primary-foreground transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:hover:scale-100 h-8 w-8 md:h-10 md:w-10 rounded-full"
          >
            <Send className="h-3 w-3 md:h-4 md:w-4" />
          </Button>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-center gap-1.5 md:gap-2 lg:gap-3">
        {actionButtons.map((button, idx) => (
          <Button
            key={idx}
            variant={button.variant}
            className="gap-1.5 md:gap-2 text-xs md:text-sm px-2.5 md:px-4 py-1.5 md:py-2 border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <button.icon className="h-3 w-3 md:h-4 md:w-4" />
            <span className="hidden sm:inline">{button.label}</span>
            <span className="sm:hidden">{button.label.split(' ')[0]}</span>
          </Button>
        ))}
      </div>
    </div>
  )
}
