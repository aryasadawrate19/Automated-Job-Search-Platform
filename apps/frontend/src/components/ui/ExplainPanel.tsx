import React from 'react';
import { MatchResponse } from '@shared/index';

export const ExplainPanel: React.FC<{ match: MatchResponse }> = ({ match }) => {
  const { explanation_detail } = match;
  if (!explanation_detail) return null;

  return (
    <div className="bg-[var(--stitch-surface)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] overflow-hidden shadow-[var(--stitch-shadow-md)]">
      
      <div className="bg-[var(--stitch-primary)]/10 border-b border-[var(--stitch-border)] p-4">
        <h3 className="font-semibold text-[var(--stitch-primary)] flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Why You Match
        </h3>
        <p className="text-sm text-[var(--stitch-typography-secondary)] mt-1">
          {explanation_detail.relevance_summary}
        </p>
      </div>

      <div className="p-5 space-y-6">
        
        {/* Experience & Location */}
        <div className="space-y-3">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 p-1.5 rounded-full bg-[var(--stitch-surface-hover)]">
              <svg className="w-4 h-4 text-[var(--stitch-typography-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-[var(--stitch-typography-primary)]">Experience Alignment</h4>
              <p className="text-sm text-[var(--stitch-typography-secondary)] mt-0.5">{explanation_detail.experience_alignment}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="mt-0.5 p-1.5 rounded-full bg-[var(--stitch-surface-hover)]">
              <svg className="w-4 h-4 text-[var(--stitch-typography-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h4 className="text-sm font-medium text-[var(--stitch-typography-primary)]">Location</h4>
              <p className="text-sm text-[var(--stitch-typography-secondary)] mt-0.5">{explanation_detail.location_note}</p>
            </div>
          </div>
        </div>

        {/* Skills Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-[var(--stitch-border)]">
          <div>
            <h4 className="text-sm font-medium text-[var(--stitch-success)] mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Matched Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {explanation_detail.matched_skills.map((skill, i) => (
                <span key={i} className="px-2 py-1 text-xs font-medium rounded bg-[var(--stitch-success)]/10 text-[var(--stitch-success)] border border-[var(--stitch-success)]/20">
                  {skill}
                </span>
              ))}
              {explanation_detail.matched_skills.length === 0 && (
                <span className="text-sm text-[var(--stitch-typography-secondary)]">None identified</span>
              )}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-[var(--stitch-error)] mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
              Missing Skills
            </h4>
            <div className="flex flex-wrap gap-2">
              {explanation_detail.missing_skills.map((skill, i) => (
                <span key={i} className="px-2 py-1 text-xs font-medium rounded bg-[var(--stitch-error)]/10 text-[var(--stitch-error)] border border-[var(--stitch-error)]/20">
                  {skill}
                </span>
              ))}
              {explanation_detail.missing_skills.length === 0 && (
                <span className="text-sm text-[var(--stitch-typography-secondary)]">Perfect match!</span>
              )}
            </div>
          </div>
        </div>

        {/* Improvement Tips */}
        {explanation_detail.improvement_tips && explanation_detail.improvement_tips.length > 0 && (
          <div className="pt-4 border-t border-[var(--stitch-border)]">
             <h4 className="text-sm font-medium text-[var(--stitch-primary)] mb-3 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Actionable Tips
            </h4>
            <ul className="space-y-2">
              {explanation_detail.improvement_tips.map((tip, i) => (
                <li key={i} className="text-sm text-[var(--stitch-typography-secondary)] flex items-start gap-2">
                  <span className="text-[var(--stitch-primary)] mt-0.5">•</span>
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

      </div>
    </div>
  );
};
