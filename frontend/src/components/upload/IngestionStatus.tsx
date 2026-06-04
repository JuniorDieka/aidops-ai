'use client'

import { IngestionJob } from '@/types'
import { CheckCircle, XCircle, Loader2, Clock } from 'lucide-react'

interface IngestionStatusProps {
  job: IngestionJob
}

export default function IngestionStatus({ job }: IngestionStatusProps) {
  const getStatusColor = () => {
    switch (job.status) {
      case 'completed':
        return 'text-green-500'
      case 'failed':
        return 'text-red-500'
      case 'processing':
        return 'text-blue-500'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'failed':
        return <XCircle className="w-4 h-4" />
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin" />
      default:
        return <Clock className="w-4 h-4" />
    }
  }

  return (
    <div className={`flex items-center space-x-2 ${getStatusColor()}`}>
      {getStatusIcon()}
      <span className="text-sm font-medium capitalize">{job.status}</span>
    </div>
  )
}
