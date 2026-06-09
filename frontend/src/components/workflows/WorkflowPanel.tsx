'use client'

import { useState } from 'react'
import { executeWorkflow } from '@/lib/api'
import { WorkflowRequest, WorkflowResponse } from '@/types'
import { CheckSquare, FileEdit, DollarSign, AlertTriangle, Loader2, XCircle, Info } from 'lucide-react'

interface WorkflowPanelProps {
  sessionId: string
}

export default function WorkflowPanel({ sessionId }: WorkflowPanelProps) {
  const [executing, setExecuting] = useState(false)
  const [result, setResult] = useState<WorkflowResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const workflows = [
    {
      type: 'compliance' as const,
      title: 'Compliance Check',
      description: 'Cross-reference operational data against global standards',
      icon: <CheckSquare className="w-6 h-6" />,
      color: 'bg-blue-500',
    },
    {
      type: 'drafting' as const,
      title: 'Report Drafting',
      description: 'Generate structured reports from raw notes',
      icon: <FileEdit className="w-6 h-6" />,
      color: 'bg-green-500',
    },
    {
      type: 'grant_matching' as const,
      title: 'Grant Matching',
      description: 'Find funding opportunities for your projects',
      icon: <DollarSign className="w-6 h-6" />,
      color: 'bg-purple-500',
    },
    {
      type: 'crisis_monitor' as const,
      title: 'Crisis Monitor',
      description: 'Monitor news and weather alerts',
      icon: <AlertTriangle className="w-6 h-6" />,
      color: 'bg-red-500',
    },
  ]

  const handleExecute = async (workflowType: WorkflowRequest['workflow_type']) => {
    setExecuting(true)
    setResult(null)
    setError(null)

    try {
      const request: WorkflowRequest = {
        workflow_type: workflowType,
        parameters: getDefaultParameters(workflowType),
        session_id: sessionId,
      }

      const response = await executeWorkflow(request)
      setResult(response)
    } catch (error) {
      console.error('Workflow execution failed:', error)
      const errorMessage = error instanceof Error ? error.message : String(error)

      // Check if it's a demo mode error
      if (errorMessage.includes('LLM provider') || errorMessage.includes('API key')) {
        setError('Agent workflows require a real LLM provider (OpenAI or Anthropic). This feature is not available in demo mode. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your environment to use workflows.')
      } else if (errorMessage.includes('Failed to fetch')) {
        setError('Unable to connect to the backend server. Please ensure the backend is running at http://localhost:8000')
      } else {
        setError(`Workflow execution failed: ${errorMessage}`)
      }
    } finally {
      setExecuting(false)
    }
  }

  const getDefaultParameters = (workflowType: string) => {
    switch (workflowType) {
      case 'compliance':
        return {
          operational_data: 'Sample operational data for compliance check',
          standard_name: 'UN SDG',
        }
      case 'drafting':
        return {
          document_type: 'field report',
          key_points: 'Sample key points for report drafting',
        }
      case 'grant_matching':
        return {
          project_description: 'Sample humanitarian project',
          focus_area: 'health',
        }
      case 'crisis_monitor':
        return {
          region: 'global',
          alert_types: 'all',
        }
      default:
        return {}
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="container mx-auto max-w-4xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Agent Workflows</h2>
          <p className="text-muted-foreground">
            Execute autonomous workflows powered by LangChain agents
          </p>
        </div>

        {/* Demo Mode Warning */}
        <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 flex items-start gap-3">
          <Info className="w-5 h-5 text-amber-600 dark:text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-200 mb-1">
              Demo Mode - Workflows Unavailable
            </h4>
            <p className="text-sm text-amber-800 dark:text-amber-300">
              Agent workflows require a real LLM provider (OpenAI or Anthropic) and are not available in demo mode.
              To enable workflows, set <code className="px-1 py-0.5 bg-amber-100 dark:bg-amber-900 rounded text-xs">OPENAI_API_KEY</code> or <code className="px-1 py-0.5 bg-amber-100 dark:bg-amber-900 rounded text-xs">ANTHROPIC_API_KEY</code> in your environment.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((workflow) => (
            <button
              key={workflow.type}
              onClick={() => handleExecute(workflow.type)}
              disabled={executing}
              className="flex items-start space-x-4 p-6 bg-card border border-border rounded-lg hover:border-primary hover:shadow-md transition-all disabled:opacity-50 disabled:cursor-not-allowed text-left"
            >
              <div className={`${workflow.color} text-white p-3 rounded-lg`}>
                {workflow.icon}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-foreground mb-1">{workflow.title}</h3>
                <p className="text-sm text-muted-foreground">{workflow.description}</p>
              </div>
            </button>
          ))}
        </div>

        {executing && (
          <div className="bg-card border border-border rounded-lg p-6 flex items-center justify-center space-x-3">
            <Loader2 className="w-6 h-6 animate-spin text-primary" />
            <p className="text-foreground">Executing workflow...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
                  Workflow Execution Failed
                </h3>
                <p className="text-sm text-red-800 dark:text-red-300 whitespace-pre-wrap">
                  {error}
                </p>
                <button
                  onClick={() => setError(null)}
                  className="mt-4 px-4 py-2 bg-red-100 dark:bg-red-900 text-red-900 dark:text-red-100 rounded-lg hover:bg-red-200 dark:hover:bg-red-800 transition-colors text-sm font-medium"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-foreground">Workflow Result</h3>
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium ${result.status === 'completed'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
                  }`}
              >
                {result.status}
              </span>
            </div>

            <div className="bg-muted rounded p-4">
              <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                {JSON.stringify(result.result, null, 2)}
              </pre>
            </div>

            {result.citations && result.citations.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-2">
                  Sources ({result.citations.length})
                </p>
                <div className="space-y-2">
                  {result.citations.map((citation, idx) => (
                    <div key={idx} className="text-sm text-foreground bg-muted/50 p-2 rounded">
                      {citation.source_file}
                      {citation.page && ` - Page ${citation.page}`}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
