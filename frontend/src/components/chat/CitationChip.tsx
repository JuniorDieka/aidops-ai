'use client'

import { useState } from 'react'
import { Citation } from '@/types'
import { FileText, X } from 'lucide-react'

interface CitationChipProps {
  citation: Citation
  index: number
}

export default function CitationChip({ citation, index }: CitationChipProps) {
  const [showDetail, setShowDetail] = useState(false)

  return (
    <>
      <button
        onClick={() => setShowDetail(true)}
        className="inline-flex items-center space-x-1 px-2 py-1 bg-primary/10 hover:bg-primary/20 text-primary rounded text-xs font-medium transition-colors"
      >
        <FileText className="w-3 h-3" />
        <span>[{index}]</span>
        <span className="max-w-[150px] truncate">{citation.source_file}</span>
        {citation.page && <span>p.{citation.page}</span>}
      </button>

      {showDetail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-foreground">Citation Details</h3>
              <button
                onClick={() => setShowDetail(false)}
                className="p-1 hover:bg-accent rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-1">Source</p>
                <p className="text-foreground">{citation.source_file}</p>
              </div>

              {citation.page && (
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-1">Page</p>
                  <p className="text-foreground">{citation.page}</p>
                </div>
              )}

              {citation.section && (
                <div>
                  <p className="text-sm font-semibold text-muted-foreground mb-1">Section</p>
                  <p className="text-foreground">{citation.section}</p>
                </div>
              )}

              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-1">Relevance Score</p>
                <p className="text-foreground">{(citation.score * 100).toFixed(1)}%</p>
              </div>

              <div>
                <p className="text-sm font-semibold text-muted-foreground mb-1">Excerpt</p>
                <p className="text-sm text-foreground bg-muted p-3 rounded">
                  {citation.text}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
