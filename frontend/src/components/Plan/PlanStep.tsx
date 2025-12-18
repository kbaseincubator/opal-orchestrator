'use client';

import { useState } from 'react';
import type { PlanStep as PlanStepType } from '@/types';

interface PlanStepProps {
  step: PlanStepType;
  index: number;
  totalSteps: number;
}

export function PlanStep({ step, index, totalSteps }: PlanStepProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-white rounded-lg border border-opal-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div
        className="px-4 py-3 flex items-center gap-3 cursor-pointer hover:bg-opal-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Step number */}
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
            step.is_hypothesis
              ? 'bg-opal-gold/20 text-opal-gold-dark border-2 border-opal-gold/50'
              : 'bg-opal-teal/20 text-opal-teal-dark'
          }`}
        >
          {index + 1}
        </div>

        {/* Title */}
        <div className="flex-1">
          <h4 className="font-medium text-opal-navy">{step.objective}</h4>
          <p className="text-sm text-opal-500">{step.recommended_facility}</p>
        </div>

        {/* Expand/collapse icon */}
        <svg
          className={`w-5 h-5 text-opal-400 transition-transform ${
            isExpanded ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-opal-100">
          {/* Hypothesis warning */}
          {step.is_hypothesis && (
            <div className="mt-3 px-3 py-2 bg-opal-gold/10 border border-opal-gold/30 rounded text-sm text-opal-gold-dark">
              This step is a hypothesis and may need verification
            </div>
          )}

          {/* Inputs/Outputs */}
          <div className="mt-3 grid grid-cols-2 gap-4">
            {step.inputs.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                  Inputs
                </h5>
                <ul className="text-sm text-opal-700 space-y-0.5">
                  {step.inputs.map((input, i) => (
                    <li key={i} className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-opal-teal rounded-full" />
                      {input}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {step.outputs.length > 0 && (
              <div>
                <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                  Outputs
                </h5>
                <ul className="text-sm text-opal-700 space-y-0.5">
                  {step.outputs.map((output, i) => (
                    <li key={i} className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-opal-purple rounded-full" />
                      {output}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Constraints */}
          {step.constraints.length > 0 && (
            <div className="mt-3">
              <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                Constraints
              </h5>
              <div className="flex flex-wrap gap-1">
                {step.constraints.map((constraint, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 bg-opal-100 text-opal-600 text-xs rounded"
                  >
                    {constraint}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Dependencies */}
          {step.dependencies.length > 0 && (
            <div className="mt-3">
              <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                Dependencies
              </h5>
              <div className="flex flex-wrap gap-1">
                {step.dependencies.map((dep, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 bg-opal-magenta/20 text-opal-magenta-dark text-xs rounded"
                  >
                    Step {dep}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Decision Points */}
          {step.decision_points.length > 0 && (
            <div className="mt-3">
              <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                Decision Points
              </h5>
              <ul className="text-sm text-opal-purple space-y-0.5">
                {step.decision_points.map((dp, i) => (
                  <li key={i} className="flex items-start gap-1">
                    <span className="mt-1.5 w-1.5 h-1.5 bg-opal-purple rounded-full flex-shrink-0" />
                    {dp}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Citations */}
          {step.citations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-opal-100">
              <h5 className="text-xs font-semibold text-opal-500 uppercase mb-1">
                Sources
              </h5>
              <div className="space-y-1">
                {step.citations.map((citation, i) => (
                  <div
                    key={i}
                    className="text-xs text-opal-600 italic bg-opal-50 px-2 py-1 rounded border-l-2 border-opal-teal"
                  >
                    "{citation.quote.slice(0, 150)}
                    {citation.quote.length > 150 ? '...' : ''}"
                    {citation.source_title && (
                      <span className="not-italic font-medium ml-1 text-opal-navy">
                        - {citation.source_title}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Connection line to next step */}
      {index < totalSteps - 1 && (
        <div className="flex justify-center py-2 bg-opal-50">
          <div className="w-0.5 h-4 bg-opal-300" />
        </div>
      )}
    </div>
  );
}
