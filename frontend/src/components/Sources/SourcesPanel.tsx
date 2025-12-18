'use client';

import { Citation } from './Citation';
import type { SearchResult } from '@/types';

interface SourcesPanelProps {
  sources: SearchResult[];
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  // Group sources by document
  const sourcesByDoc = sources.reduce(
    (acc, source) => {
      const docId = source.source_document_id;
      if (!acc[docId]) {
        acc[docId] = {
          title: source.source_title,
          chunks: [],
        };
      }
      acc[docId].chunks.push(source);
      return acc;
    },
    {} as Record<string, { title: string; chunks: SearchResult[] }>
  );

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-opal-200 bg-white">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-opal-gold"></div>
          <h2 className="font-semibold text-opal-navy">Sources</h2>
        </div>
        <p className="text-sm text-opal-500 mt-1">
          {sources.length > 0
            ? `${sources.length} citation${sources.length !== 1 ? 's' : ''} from ${
                Object.keys(sourcesByDoc).length
              } document${Object.keys(sourcesByDoc).length !== 1 ? 's' : ''}`
            : 'Citations will appear here as the plan develops'}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 bg-opal-50">
        {sources.length === 0 ? (
          <div className="text-center text-opal-400 mt-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-opal-100 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-opal-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <p className="text-sm">No sources yet</p>
            <p className="text-xs mt-1">
              Sources will be shown as capabilities are searched
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {Object.entries(sourcesByDoc).map(([docId, doc]) => (
              <div key={docId} className="bg-white rounded-lg p-4 border border-opal-200 shadow-sm">
                <h3 className="font-medium text-opal-navy text-sm mb-3 flex items-center gap-2">
                  <svg
                    className="w-4 h-4 text-opal-teal"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  {doc.title}
                </h3>
                <div className="space-y-2">
                  {doc.chunks.map((chunk, i) => (
                    <Citation key={i} source={chunk} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
