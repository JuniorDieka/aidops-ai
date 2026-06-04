'use client'

import { useState } from 'react'
import { uploadFile, ingestSampleData } from '@/lib/api'
import { IngestionJob } from '@/types'
import { Upload, FileText, Music, Table, CheckCircle, XCircle, Loader2, Database } from 'lucide-react'
import IngestionStatus from './IngestionStatus'

export default function FileUpload() {
  const [jobs, setJobs] = useState<IngestionJob[]>([])
  const [uploading, setUploading] = useState(false)
  const [ingesting, setIngesting] = useState(false)

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)

    try {
      for (const file of Array.from(files)) {
        const job = await uploadFile(file)
        setJobs((prev) => [job, ...prev])
      }
    } catch (error) {
      console.error('Upload failed:', error)
      alert(`Upload failed: ${error}`)
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const handleIngestSampleData = async () => {
    setIngesting(true)

    try {
      const result = await ingestSampleData()
      setJobs((prev) => [...result.jobs, ...prev])
      alert(result.message)
    } catch (error) {
      console.error('Sample data ingestion failed:', error)
      alert(`Sample data ingestion failed: ${error}`)
    } finally {
      setIngesting(false)
    }
  }

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case 'pdf':
        return <FileText className="w-5 h-5" />
      case 'audio':
        return <Music className="w-5 h-5" />
      case 'spreadsheet':
        return <Table className="w-5 h-5" />
      default:
        return <FileText className="w-5 h-5" />
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
      default:
        return <Loader2 className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="container mx-auto max-w-4xl space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Upload Documents</h2>
          <p className="text-muted-foreground">
            Upload PDFs, audio files, or spreadsheets to add them to your knowledge base
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-border rounded-lg p-8 cursor-pointer hover:border-primary hover:bg-accent/50 transition-colors">
            <Upload className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-sm font-medium text-foreground mb-1">Upload Files</p>
            <p className="text-xs text-muted-foreground mb-3">PDF, MP3, WAV, CSV, XLSX</p>
            <input
              type="file"
              multiple
              accept=".pdf,.mp3,.wav,.csv,.xlsx,.xls"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            {uploading && <Loader2 className="w-5 h-5 animate-spin text-primary" />}
          </label>

          <button
            onClick={handleIngestSampleData}
            disabled={ingesting}
            className="flex flex-col items-center justify-center border-2 border-border rounded-lg p-8 hover:border-primary hover:bg-accent/50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Database className="w-12 h-12 text-muted-foreground mb-3" />
            <p className="text-sm font-medium text-foreground mb-1">Load Sample Data</p>
            <p className="text-xs text-muted-foreground mb-3">Ingest bundled humanitarian docs</p>
            {ingesting && <Loader2 className="w-5 h-5 animate-spin text-primary" />}
          </button>
        </div>

        {jobs.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Ingestion History</h3>

            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-card border border-border rounded-lg p-4 flex items-center justify-between"
                >
                  <div className="flex items-center space-x-3 flex-1">
                    <div className="text-muted-foreground">{getFileIcon(job.file_type)}</div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {job.file_name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {job.status === 'completed' && `${job.chunks_created} chunks created`}
                        {job.status === 'failed' && job.error_message}
                        {job.status === 'processing' && 'Processing...'}
                      </p>
                    </div>
                  </div>
                  <div>{getStatusIcon(job.status)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
