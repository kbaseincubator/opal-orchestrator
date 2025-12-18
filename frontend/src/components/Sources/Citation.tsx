'use client';

import { useState } from 'react';
import type { SearchResult } from '@/types';

interface CitationProps {
  source: SearchResult;
}

export function Citation({ source }: CitationProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const previewLength = 150;
  const needsExpansion = source.text.length > previewLength;

  // Extract metadata safely
  const metadata = source.metadata || {};
  const page = metadata.page as string | number | undefined;
  const capabilityName = metadata.capability_name as string | undefined;
  const hasMetadata = page || capabilityName;

  return (
    <div className="bg-opal-50 rounded border border-opal-200 p-2 hover:border-opal-teal transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <p className="text-xs text-opal-700">
            {isExpanded || !needsExpansion
              ? source.text
              : `${source.text.slice(0, previewLength)}...`}
          </p>
          {needsExpansion && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-xs text-opal-teal hover:text-opal-teal-dark mt-1 font-medium"
            >
              {isExpanded ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>
        <div className="flex-shrink-0">
          <span
            className="inline-block px-1.5 py-0.5 bg-opal-teal/20 text-opal-teal-dark text-xs rounded font-medium"
            title={`Relevance score: ${(source.score * 100).toFixed(0)}%`}
          >
            {(source.score * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      {hasMetadata ? (
        <div className="mt-1 flex flex-wrap gap-1">
          {page ? (
            <span className="text-xs text-opal-500">Page {String(page)}</span>
          ) : null}
          {capabilityName ? (
            <span className="text-xs bg-opal-purple/20 text-opal-purple-dark px-1 rounded">
              {capabilityName}
            </span>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
