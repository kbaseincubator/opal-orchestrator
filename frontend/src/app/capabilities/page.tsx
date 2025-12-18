'use client';

import { useEffect, useState } from 'react';
import { getCapabilities, getLabs } from '@/lib/api';
import type { Capability, Lab } from '@/types';

export default function CapabilitiesPage() {
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [labs, setLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLab, setSelectedLab] = useState<string>('all');
  const [selectedModality, setSelectedModality] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        const [capsData, labsData] = await Promise.all([
          getCapabilities(),
          getLabs(),
        ]);
        setCapabilities(capsData);
        setLabs(labsData);
      } catch (err) {
        setError('Failed to load capabilities');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Get unique modalities
  const allModalities = Array.from(
    new Set(capabilities.flatMap((c) => c.modalities || []))
  ).sort();

  // Filter capabilities
  const filteredCapabilities = capabilities.filter((cap) => {
    const matchesLab = selectedLab === 'all' || cap.lab_name === selectedLab;
    const matchesModality =
      selectedModality === 'all' ||
      (cap.modalities && cap.modalities.includes(selectedModality));
    const matchesSearch =
      !searchQuery ||
      cap.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cap.description && cap.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (cap.tags && cap.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase())));

    return matchesLab && matchesModality && matchesSearch;
  });

  // Group by lab
  const capabilitiesByLab = filteredCapabilities.reduce(
    (acc, cap) => {
      if (!acc[cap.lab_name]) {
        acc[cap.lab_name] = [];
      }
      acc[cap.lab_name].push(cap);
      return acc;
    },
    {} as Record<string, Capability[]>
  );

  return (
    <div className="min-h-screen bg-opal-50">
      {/* Header */}
      <div className="bg-white border-b border-opal-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-3 h-3 rounded-full bg-opal-purple"></div>
            <h1 className="text-2xl font-bold text-opal-navy">Capability Registry</h1>
          </div>
          <p className="text-opal-600 max-w-3xl">
            Explore the research capabilities available across the OPAL network.
            Each capability card describes the equipment, expertise, and services
            available at member laboratories.
          </p>

          {/* Filters */}
          <div className="mt-6 flex flex-wrap gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[250px]">
              <input
                type="text"
                placeholder="Search capabilities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-opal-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-opal-teal focus:border-transparent"
              />
            </div>

            {/* Lab filter */}
            <select
              value={selectedLab}
              onChange={(e) => setSelectedLab(e.target.value)}
              className="px-4 py-2 border border-opal-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-opal-teal bg-white"
            >
              <option value="all">All Labs</option>
              {labs.map((lab) => (
                <option key={lab.id} value={lab.name}>
                  {lab.institution}
                </option>
              ))}
            </select>

            {/* Modality filter */}
            <select
              value={selectedModality}
              onChange={(e) => setSelectedModality(e.target.value)}
              className="px-4 py-2 border border-opal-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-opal-teal bg-white"
            >
              <option value="all">All Modalities</option>
              {allModalities.map((mod) => (
                <option key={mod} value={mod}>
                  {mod}
                </option>
              ))}
            </select>
          </div>

          {/* Stats */}
          <div className="mt-4 flex gap-6 text-sm text-opal-500">
            <span>
              <strong className="text-opal-navy">{filteredCapabilities.length}</strong> capabilities
            </span>
            <span>
              <strong className="text-opal-navy">{Object.keys(capabilitiesByLab).length}</strong> labs
            </span>
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
              <span>Loading capabilities...</span>
            </div>
          </div>
        ) : error ? (
          <div className="bg-opal-magenta/10 border border-opal-magenta/30 rounded-lg p-4 text-opal-magenta-dark">
            {error}
          </div>
        ) : filteredCapabilities.length === 0 ? (
          <div className="text-center py-12 text-opal-500">
            <p>No capabilities found matching your criteria.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedLab('all');
                setSelectedModality('all');
              }}
              className="mt-2 text-opal-teal hover:text-opal-teal-dark font-medium"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(capabilitiesByLab).map(([labName, caps]) => (
              <div key={labName}>
                {/* Lab header */}
                <div className="flex items-center gap-2 mb-4">
                  <h2 className="text-lg font-semibold text-opal-navy">{labName}</h2>
                  <span className="text-sm text-opal-500">
                    ({caps[0].lab_institution})
                  </span>
                </div>

                {/* Capability cards */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {caps.map((cap) => (
                    <CapabilityCard key={cap.id} capability={cap} />
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

function CapabilityCard({ capability }: { capability: Capability }) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-opal-200 shadow-sm hover:border-opal-purple hover:shadow-md transition-all overflow-hidden">
      {/* Header */}
      <div
        className="px-4 py-3 cursor-pointer hover:bg-opal-50"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-opal-navy">{capability.name}</h3>
            <p className="text-sm text-opal-500">{capability.facility_name}</p>
          </div>
          <svg
            className={`w-5 h-5 text-opal-400 transition-transform mt-1 ${
              isExpanded ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Body */}
      <div className={`px-4 pb-4 ${isExpanded ? '' : 'max-h-32 overflow-hidden'}`}>
        {/* Description */}
        {capability.description && (
          <p className="text-sm text-opal-700 mb-3">{capability.description}</p>
        )}

        {/* Modalities */}
        {capability.modalities && capability.modalities.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {capability.modalities.map((mod, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-opal-teal/20 text-opal-teal-dark text-xs rounded font-medium"
              >
                {mod}
              </span>
            ))}
          </div>
        )}

        {isExpanded && (
          <>
            {/* Throughput */}
            {capability.throughput && (
              <div className="mb-3">
                <span className="text-xs font-semibold text-opal-500 uppercase">Throughput: </span>
                <span className="text-sm text-opal-700">{capability.throughput}</span>
              </div>
            )}

            {/* Outputs */}
            {capability.typical_outputs && capability.typical_outputs.length > 0 && (
              <div className="mb-3">
                <span className="text-xs font-semibold text-opal-500 uppercase block mb-1">Outputs</span>
                <ul className="text-sm text-opal-700 space-y-0.5">
                  {capability.typical_outputs.map((output, i) => (
                    <li key={i} className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-opal-purple rounded-full" />
                      {output}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Tags */}
            {capability.tags && capability.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {capability.tags.map((tag, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 bg-opal-100 text-opal-600 text-xs rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Readiness */}
            {capability.readiness_level && (
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-0.5 text-xs rounded font-medium ${
                    capability.readiness_level === 'Operational'
                      ? 'bg-opal-teal/20 text-opal-teal-dark'
                      : 'bg-opal-gold/20 text-opal-gold-dark'
                  }`}
                >
                  {capability.readiness_level}
                </span>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2 border-t border-opal-100 bg-opal-50">
        <a
          href={`/?query=${encodeURIComponent(capability.name)}`}
          className="text-sm text-opal-purple hover:text-opal-purple-dark font-medium flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          Use in research plan
        </a>
      </div>
    </div>
  );
}
