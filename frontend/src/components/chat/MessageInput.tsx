'use client'

import { useState, KeyboardEvent, useRef } from 'react'
import { Send, Paperclip } from 'lucide-react'

interface MessageInputProps {
  onSend: (message: string) => void
  onFileUpload?: (file: File) => void
  disabled?: boolean
}

export default function MessageInput({ onSend, onFileUpload, disabled = false }: MessageInputProps) {
  const [input, setInput] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim())
      setInput('')
    }
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && onFileUpload) {
      onFileUpload(file)
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="border-t border-border bg-card p-4">
      <div className="container mx-auto max-w-4xl">
        <div className="relative flex items-end gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.csv,.xlsx,.xls,.mp3,.wav"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="relative flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your humanitarian operations..."
              disabled={disabled}
              rows={3}
              className="w-full resize-none rounded-lg border border-input bg-background pl-12 pr-4 py-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            />
            <button
              onClick={handleFileClick}
              disabled={disabled}
              className="absolute left-3 bottom-3 p-1.5 rounded-md hover:bg-accent hover:text-accent-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Upload file"
            >
              <Paperclip className="w-5 h-5" />
            </button>
          </div>
          <button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            className="h-12 w-12 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
