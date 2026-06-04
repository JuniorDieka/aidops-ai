export interface Citation {
  source_file: string
  page?: number
  section?: string
  chunk_id: string
  score: number
  text: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  citations?: Citation[]
  timestamp: string
}

export interface StreamChunk {
  type: 'context_retrieved' | 'citation' | 'stream_start' | 'token' | 'stream_end' | 'error'
  content?: string
  citation?: Citation
  metadata?: Record<string, any>
}

export interface IngestionJob {
  id: string
  file_name: string
  file_type: 'pdf' | 'audio' | 'spreadsheet'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  error_message?: string
  chunks_created: number
}

export interface WorkflowRequest {
  workflow_type: 'compliance' | 'drafting' | 'grant_matching' | 'crisis_monitor'
  parameters: Record<string, any>
  session_id?: string
}

export interface WorkflowResponse {
  workflow_id: string
  workflow_type: string
  status: string
  result: Record<string, any>
  citations?: Citation[]
  created_at: string
}
