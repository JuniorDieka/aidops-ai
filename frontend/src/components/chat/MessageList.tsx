'use client'

import { useEffect, useRef } from 'react'
import { Message, Citation } from '@/types'
import { User, Bot, Loader2 } from 'lucide-react'
import CitationChip from './CitationChip'
import { formatTimestamp } from '@/lib/utils'

interface MessageListProps {
  messages: Message[]
  isStreaming: boolean
  streamContent: string
  streamCitations: Citation[]
}

export default function MessageList({
  messages,
  isStreaming,
  streamContent,
  streamCitations,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamContent])

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {messages.length === 0 && !isStreaming && (
        <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
          <Bot className="w-16 h-16 text-muted-foreground" />
          <div>
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Welcome to AidOps AI
            </h2>
            <p className="text-muted-foreground max-w-md">
              Ask questions about your humanitarian operations data, request compliance checks,
              draft reports, or find grant opportunities.
            </p>
          </div>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex items-start space-x-3 ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          {message.role === 'assistant' && (
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
          )}

          <div
            className={`max-w-3xl ${
              message.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted text-foreground'
            } rounded-lg p-4 shadow-sm`}
          >
            <div className="prose prose-sm max-w-none">
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>

            {message.citations && message.citations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border/50 space-y-2">
                <p className="text-xs font-semibold text-muted-foreground">Sources:</p>
                <div className="flex flex-wrap gap-2">
                  {Array.from(new Map(message.citations.map(c => [c.source_file, c])).values()).map((citation, idx) => (
                    <CitationChip key={idx} citation={citation} index={idx + 1} />
                  ))}
                </div>
              </div>
            )}

            <p className="text-xs text-muted-foreground mt-2">
              {formatTimestamp(message.timestamp)}
            </p>
          </div>

          {message.role === 'user' && (
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-secondary-foreground" />
            </div>
          )}
        </div>
      ))}

      {isStreaming && (
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-primary-foreground" />
          </div>

          <div className="max-w-3xl bg-muted text-foreground rounded-lg p-4 shadow-sm">
            {streamContent ? (
              <>
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-wrap">{streamContent}</p>
                </div>

                {streamCitations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50 space-y-2">
                    <p className="text-xs font-semibold text-muted-foreground">Sources:</p>
                    <div className="flex flex-wrap gap-2">
                      {Array.from(new Map(streamCitations.map(c => [c.source_file, c])).values()).map((citation, idx) => (
                        <CitationChip key={idx} citation={citation} index={idx + 1} />
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm text-muted-foreground">Thinking...</span>
              </div>
            )}
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  )
}
