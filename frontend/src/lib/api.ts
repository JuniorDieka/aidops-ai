import { IngestionJob, WorkflowRequest, WorkflowResponse } from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function uploadFile(file: File): Promise<IngestionJob> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/ingest`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`)
  }

  return response.json()
}

export async function ingestSampleData(): Promise<{ message: string; jobs: IngestionJob[] }> {
  const response = await fetch(`${API_URL}/api/ingest-sample-data`, {
    method: 'POST',
  })

  if (!response.ok) {
    throw new Error(`Sample data ingestion failed: ${response.statusText}`)
  }

  return response.json()
}

export async function executeWorkflow(request: WorkflowRequest): Promise<WorkflowResponse> {
  const response = await fetch(`${API_URL}/api/workflows/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    // Try to get the actual error message from the response body
    try {
      const errorData = await response.json()
      const errorMessage = errorData.detail || response.statusText
      throw new Error(errorMessage)
    } catch (parseError) {
      throw new Error(`Workflow execution failed: ${response.statusText}`)
    }
  }

  return response.json()
}

export async function checkHealth(): Promise<{
  status: string
  version: string
  demo_mode: boolean
  services: Record<string, boolean>
}> {
  const response = await fetch(`${API_URL}/health`)

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`)
  }

  return response.json()
}
