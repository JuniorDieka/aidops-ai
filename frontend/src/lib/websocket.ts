import { StreamChunk } from '@/types'

export class WebSocketClient {
  private ws: WebSocket | null = null
  private sessionId: string
  private onMessage: (chunk: StreamChunk) => void
  private onError: (error: Event) => void
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  constructor(
    sessionId: string,
    onMessage: (chunk: StreamChunk) => void,
    onError: (error: Event) => void
  ) {
    this.sessionId = sessionId
    this.onMessage = onMessage
    this.onError = onError
  }

  connect(): void {
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/api/ws/chat/${this.sessionId}`

    this.ws = new WebSocket(wsUrl)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const chunk: StreamChunk = JSON.parse(event.data)
        this.onMessage(chunk)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.onError(error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => this.connect(), 1000 * this.reconnectAttempts)
      }
    }
  }

  sendMessage(message: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ message }))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
