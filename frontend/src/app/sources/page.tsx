'use client';

import { useEffect, useState } from 'react';
import { getLabs } from '@/lib/api';
import type { Lab } from '@/types';

// Extended lab data with additional context from OPAL
const labDetails: Record<string, { focus: string; capabilities: string[] }> = {
  'Argonne National Laboratory': {
    focus: 'Synthetic biology, automation, and computational capabilities for biomanufacturing',
    capabilities: ['DBTL Automation', 'High-Throughput Screening', 'Chassis Strain Access'],
  },
  'Lawrence Berkeley National Laboratory': {
    focus: 'Genomics, systems biology, and bioenergy research through JGI and ENIGMA',
    capabilities: ['Whole Genome Sequencing', 'DNA Synthesis', 'Metagenomics', 'Microbial Community Analysis'],
  },
  'Pacific Northwest National Laboratory': {
    focus: 'Advanced proteomics, metabolomics, and environmental molecular sciences',
    capabilities: ['Proteomics', 'Metabolomics', 'NMR Spectroscopy'],
  },
  'Oak Ridge National Laboratory': {
    focus: 'Plant science, microbiology, and bioenergy research with extensive phenotyping capabilities',
    capabilities: ['Automated Plant Phenotyping', 'Root Imaging', 'Microbial Cultivation'],
  },
};

export default function SourcesPage() {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLabs() {
      try {
        const data = await getLabs();
        setLabs(data);
      } catch (err) {
        setError('Failed to load labs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchLabs();
  }, []);

  return (
    <div className="min-h-screen bg-opal-50">
      {/* Header */}
      <div className="bg-white border-b border-opal-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 rounded-full bg-opal-gold"></div>
            <h1 className="text-2xl font-bold text-opal-navy">OPAL Member Labs</h1>
          </div>
          <p className="text-opal-600 max-w-3xl">
            The OPAL (Orchestrated Platform for Autonomous Laboratories) consortium brings together
            four DOE national laboratories to advance bioenergy research through integrated
            plant-microbe systems. Each lab contributes unique capabilities to the network.
          </p>
          <div className="mt-4 flex gap-4">
            <a
              href="https://opal-doe.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-opal-teal hover:text-opal-teal-dark font-medium"
            >
              Visit OPAL Project
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-3 text-opal-500">
              <div className="w-2 h-2 bg-opal-teal rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-opal-purple rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-opal-magenta rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              <span>Loading labs...</span>
            </div>
          </div>
        ) : error ? (
          <div className="bg-opal-magenta/10 border border-opal-magenta/30 rounded-lg p-4 text-opal-magenta-dark">
            {error}
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {labs.map((lab) => {
              const details = labDetails[lab.name];
              const websiteUrl = lab.urls?.website;

              return (
                <div
                  key={lab.id}
                  className="bg-white rounded-lg border border-opal-200 shadow-sm hover:border-opal-teal hover:shadow-md transition-all overflow-hidden"
                >
                  {/* Card Header */}
                  <div className="bg-opal-navy px-4 py-3">
                    <h2 className="font-semibold text-white">{lab.name}</h2>
                    <p className="text-opal-200 text-sm">{lab.institution}</p>
                  </div>

                  {/* Card Body */}
                  <div className="p-4">
                    {/* Location */}
                    {lab.location && (
                      <div className="flex items-center gap-2 text-sm text-opal-500 mb-3">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {lab.location}
                      </div>
                    )}

                    {/* Description */}
                    <p className="text-opal-700 text-sm mb-4">
                      {lab.description || details?.focus || 'DOE national laboratory contributing to OPAL research.'}
                    </p>

                    {/* Key Capabilities */}
                    {details?.capabilities && (
                      <div className="mb-4">
                        <h3 className="text-xs font-semibold text-opal-500 uppercase mb-2">Key Capabilities</h3>
                        <div className="flex flex-wrap gap-1">
                          {details.capabilities.slice(0, 4).map((cap, i) => (
                            <span
                              key={i}
                              className="px-2 py-0.5 bg-opal-100 text-opal-700 text-xs rounded"
                            >
                              {cap}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Links */}
                    <div className="pt-3 border-t border-opal-100 flex gap-3">
                      {websiteUrl && (
                        <a
                          href={websiteUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-sm text-opal-teal hover:text-opal-teal-dark font-medium"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                          </svg>
                          Website
                        </a>
                      )}
                      <a
                        href={`/?lab=${encodeURIComponent(lab.name)}`}
                        className="inline-flex items-center gap-1 text-sm text-opal-purple hover:text-opal-purple-dark font-medium"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        Ask about this lab
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Additional Resources */}
        <div className="mt-12 bg-white rounded-lg border border-opal-200 p-6">
          <h2 className="text-lg font-semibold text-opal-navy mb-4">Additional Resources</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <a
              href="https://opal-doe.org/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-3 p-4 rounded-lg border border-opal-200 hover:border-opal-teal hover:bg-opal-50 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-opal-teal/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-opal-teal" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-opal-navy">OPAL Project Website</h3>
                <p className="text-sm text-opal-500">Learn more about the OPAL consortium</p>
              </div>
            </a>

            <a
              href="https://www.energy.gov/science/ber/biological-and-environmental-research"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-3 p-4 rounded-lg border border-opal-200 hover:border-opal-purple hover:bg-opal-50 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-opal-purple/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-opal-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-opal-navy">DOE BER Program</h3>
                <p className="text-sm text-opal-500">Biological & Environmental Research</p>
              </div>
            </a>

            <a
              href="/capabilities"
              className="flex items-start gap-3 p-4 rounded-lg border border-opal-200 hover:border-opal-gold hover:bg-opal-50 transition-colors"
            >
              <div className="w-10 h-10 rounded-lg bg-opal-gold/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-opal-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
              </div>
              <div>
                <h3 className="font-medium text-opal-navy">Browse Capabilities</h3>
                <p className="text-sm text-opal-500">Explore all available research capabilities</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
