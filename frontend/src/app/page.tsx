'use client'

import { useState, useEffect } from 'react'
import ChatInterface from '@/components/chat/ChatInterface'
import FileUpload from '@/components/upload/FileUpload'
import WorkflowPanel from '@/components/workflows/WorkflowPanel'
import { AlertCircle, FileText, Zap } from 'lucide-react'

export default function Home() {
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`)
  const [demoMode, setDemoMode] = useState(false)
  const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'workflows'>('chat')

  useEffect(() => {
    const checkDemoMode = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)
        const data = await response.json()
        setDemoMode(data.demo_mode)
      } catch (error) {
        console.error('Failed to check demo mode:', error)
      }
    }
    checkDemoMode()
  }, [])

  return (
    <div className="flex flex-col h-screen bg-background">
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
                <Zap className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">AidOps AI</h1>
                <p className="text-sm text-muted-foreground">Humanitarian Operations Platform</p>
              </div>
            </div>
            {demoMode && (
              <div className="flex items-center space-x-2 px-3 py-1.5 bg-amber-100 dark:bg-amber-900/30 rounded-md">
                <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                <span className="text-sm font-medium text-amber-800 dark:text-amber-300">Demo Mode</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-64 border-r border-border bg-card p-4 space-y-2">
          <button
            onClick={() => setActiveTab('chat')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'chat'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent text-foreground'
            }`}
          >
            <FileText className="w-5 h-5" />
            <span className="font-medium">Chat</span>
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'upload'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent text-foreground'
            }`}
          >
            <FileText className="w-5 h-5" />
            <span className="font-medium">Upload Files</span>
          </button>
          <button
            onClick={() => setActiveTab('workflows')}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
              activeTab === 'workflows'
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent text-foreground'
            }`}
          >
            <Zap className="w-5 h-5" />
            <span className="font-medium">Workflows</span>
          </button>
        </aside>

        <main className="flex-1 overflow-hidden">
          {activeTab === 'chat' && <ChatInterface sessionId={sessionId} />}
          {activeTab === 'upload' && <FileUpload />}
          {activeTab === 'workflows' && <WorkflowPanel sessionId={sessionId} />}
        </main>
      </div>
    </div>
  )
}
