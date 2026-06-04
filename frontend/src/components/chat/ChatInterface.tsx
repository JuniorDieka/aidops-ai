'use client'

import { useState, useEffect, useRef } from 'react'
import { WebSocketClient } from '@/lib/websocket'
import { Message, Citation, StreamChunk } from '@/types'
import { uploadFile } from '@/lib/api'
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
  const streamContentRef = useRef('')
  const streamCitationsRef = useRef<Citation[]>([])

  useEffect(() => {
    const handleMessage = (chunk: StreamChunk) => {
      if (chunk.type === 'context_retrieved') {
        setIsStreaming(true)
        setCurrentStreamContent('')
        setCurrentCitations([])
        streamContentRef.current = ''
        streamCitationsRef.current = []
      } else if (chunk.type === 'citation' && chunk.citation) {
        streamCitationsRef.current = [...streamCitationsRef.current, chunk.citation]
        setCurrentCitations(streamCitationsRef.current)
      } else if (chunk.type === 'stream_start') {
        streamContentRef.current = ''
        setCurrentStreamContent('')
      } else if (chunk.type === 'token' && chunk.content) {
        streamContentRef.current += chunk.content
        setCurrentStreamContent(streamContentRef.current)
      } else if (chunk.type === 'stream_end') {
        const assistantMessage: Message = {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: streamContentRef.current,
          citations: streamCitationsRef.current,
          timestamp: new Date().toISOString(),
        }
        setMessages((prev) => [...prev, assistantMessage])
        setIsStreaming(false)
        setCurrentStreamContent('')
        setCurrentCitations([])
        streamContentRef.current = ''
        streamCitationsRef.current = []
      } else if (chunk.type === 'error') {
        console.error('Stream error:', chunk.content)
        setIsStreaming(false)
        setCurrentStreamContent('')
        streamContentRef.current = ''
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

  const handleFileUpload = async (file: File) => {
    try {
      // Add system message about upload
      const uploadMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `📎 Uploading ${file.name}...`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, uploadMessage])

      // Upload file
      const result = await uploadFile(file)
      
      // Add success message
      const successMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `✅ Successfully uploaded and processed ${file.name}. Created ${result.chunks_created} chunks. You can now ask questions about this document!`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev.slice(0, -1), successMessage])
    } catch (error) {
      // Add error message
      const errorMessage: Message = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `❌ Failed to upload ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev.slice(0, -1), errorMessage])
    }
  }

  return (
    <div className="flex flex-col h-full">
      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        streamContent={currentStreamContent}
        streamCitations={currentCitations}
      />
      <MessageInput 
        onSend={handleSendMessage} 
        onFileUpload={handleFileUpload}
        disabled={isStreaming} 
      />
    </div>
  )
}
