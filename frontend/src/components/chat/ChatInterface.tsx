'use client'

import { useState, useEffect, useRef } from 'react'
import { WebSocketClient } from '@/lib/websocket'
import { Message, Citation, StreamChunk } from '@/types'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

interface ChatInterfaceProps {
  sessionId: string
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStreamContent, setCurrentStreamContent] = useState('')
  const [currentCitations, setCurrentCitations] = useState<Citation[]>([])
  const wsClientRef = useRef<WebSocketClient | null>(null)

  useEffect(() => {
    const handleMessage = (chunk: StreamChunk) => {
      if (chunk.type === 'context_retrieved') {
        setIsStreaming(true)
        setCurrentStreamContent('')
        setCurrentCitations([])
      } else if (chunk.type === 'citation' && chunk.citation) {
        setCurrentCitations((prev) => [...prev, chunk.citation!])
      } else if (chunk.type === 'stream_start') {
        setCurrentStreamContent('')
      } else if (chunk.type === 'token' && chunk.content) {
        setCurrentStreamContent((prev) => prev + chunk.content)
      } else if (chunk.type === 'stream_end') {
        const assistantMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: currentStreamContent,
          citations: currentCitations,
          timestamp: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, assistantMessage])
        setIsStreaming(false)
        setCurrentStreamContent('')
        setCurrentCitations([])
      } else if (chunk.type === 'error') {
        console.error('Stream error:', chunk.content)
        setIsStreaming(false)
        setCurrentStreamContent('')
      }
    }

    const handleError = (error: Event) => {
      console.error('WebSocket error:', error)
      setIsStreaming(false)
    }

    wsClientRef.current = new WebSocketClient(sessionId, handleMessage, handleError)
    wsClientRef.current.connect()

    return () => {
      wsClientRef.current?.disconnect()
    }
  }, [sessionId])

  const handleSendMessage = (content: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    wsClientRef.current?.sendMessage(content)
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        streamContent={currentStreamContent}
        streamCitations={currentCitations}
      />
      <MessageInput onSend={handleSendMessage} disabled={isStreaming} />
    </div>
  )
}
