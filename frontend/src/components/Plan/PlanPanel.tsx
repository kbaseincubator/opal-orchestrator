'use client';

import { PlanStep } from './PlanStep';
import type { OPALPlan } from '@/types';

interface PlanPanelProps {
  plan: OPALPlan | null;
}

export function PlanPanel({ plan }: PlanPanelProps) {
  if (!plan) {
    return (
      <div className="flex flex-col h-full">
        <div className="px-4 py-3 border-b border-opal-200 bg-white">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-opal-purple"></div>
            <h2 className="font-semibold text-opal-navy">Research Plan</h2>
          </div>
          <p className="text-sm text-opal-500 mt-1">
            Your plan will appear here as we develop it
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center text-opal-400">
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
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                />
              </svg>
            </div>
            <p className="text-sm">No plan generated yet</p>
            <p className="text-xs mt-1">
              Start by describing your research goal in the chat
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-opal-200 bg-white">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-opal-purple"></div>
          <h2 className="font-semibold text-opal-navy">Research Plan</h2>
        </div>
        <p className="text-sm text-opal-600 mt-1">{plan.goal_summary}</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {/* Assumptions */}
        {plan.assumptions.length > 0 && (
          <div className="mb-6 p-4 bg-white rounded-lg border border-opal-200">
            <h3 className="text-sm font-semibold text-opal-navy mb-2">
              Assumptions
            </h3>
            <ul className="text-sm text-opal-600 list-disc list-inside space-y-1">
              {plan.assumptions.map((assumption, i) => (
                <li key={i}>{assumption}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Steps */}
        <div className="space-y-4">
          {plan.steps.map((step, index) => (
            <PlanStep
              key={step.step_id}
              step={step}
              index={index}
              totalSteps={plan.steps.length}
            />
          ))}
        </div>

        {/* Open Questions */}
        {plan.open_questions.length > 0 && (
          <div className="mt-6 p-4 bg-opal-gold/10 border border-opal-gold/30 rounded-lg">
            <h3 className="text-sm font-semibold text-opal-gold-dark mb-2 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Open Questions
            </h3>
            <ul className="text-sm text-opal-700 list-disc list-inside space-y-1">
              {plan.open_questions.map((question, i) => (
                <li key={i}>{question}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Risks */}
        {plan.risks_and_alternatives.length > 0 && (
          <div className="mt-6 p-4 bg-opal-magenta/10 border border-opal-magenta/30 rounded-lg">
            <h3 className="text-sm font-semibold text-opal-magenta-dark mb-2 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Risks & Alternatives
            </h3>
            <div className="space-y-3">
              {plan.risks_and_alternatives.map((risk, i) => (
                <div key={i} className="text-sm">
                  <p className="text-opal-magenta-dark font-medium">{risk.risk}</p>
                  <p className="text-opal-600 text-xs">Impact: {risk.impact}</p>
                  {risk.alternative && (
                    <p className="text-opal-teal text-xs mt-1">
                      Alternative: {risk.alternative}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Export buttons */}
      <div className="p-4 border-t border-opal-200 bg-white flex gap-2">
        <button
          onClick={() => {
            const json = JSON.stringify(plan, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'opal-plan.json';
            a.click();
          }}
          className="flex-1 px-4 py-2 text-sm bg-opal-100 text-opal-navy hover:bg-opal-200 rounded-lg transition-colors font-medium"
        >
          Export JSON
        </button>
        <button
          onClick={() => {
            // Generate markdown
            let md = `# OPAL Research Plan\n\n`;
            md += `## Goal\n${plan.goal_summary}\n\n`;
            if (plan.assumptions.length > 0) {
              md += `## Assumptions\n`;
              plan.assumptions.forEach((a) => (md += `- ${a}\n`));
              md += '\n';
            }
            md += `## Steps\n\n`;
            plan.steps.forEach((step, i) => {
              md += `### Step ${i + 1}: ${step.objective}\n`;
              md += `**Facility:** ${step.recommended_facility}\n\n`;
              if (step.inputs.length > 0) {
                md += `**Inputs:** ${step.inputs.join(', ')}\n\n`;
              }
              if (step.outputs.length > 0) {
                md += `**Outputs:** ${step.outputs.join(', ')}\n\n`;
              }
              if (step.constraints.length > 0) {
                md += `**Constraints:** ${step.constraints.join(', ')}\n\n`;
              }
              if (step.dependencies.length > 0) {
                md += `**Dependencies:** ${step.dependencies.join(', ')}\n\n`;
              }
            });
            const blob = new Blob([md], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'opal-plan.md';
            a.click();
          }}
          className="flex-1 px-4 py-2 text-sm bg-opal-navy text-white hover:bg-opal-navy-light rounded-lg transition-colors font-medium"
        >
          Export Markdown
        </button>
      </div>
    </div>
  );
}
