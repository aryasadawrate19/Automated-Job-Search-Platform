import React from 'react';
import Link from 'next/link';

interface MatchCardProps {
  id: string;
  jobId: string;
  title: string;
  company: string;
  location: string;
  remote: boolean;
  score: number;
  tags: string[];
}

export const MatchCard: React.FC<MatchCardProps> = ({
  id,
  jobId,
  title,
  company,
  location,
  remote,
  score,
  tags,
}) => {
  const percentage = Math.round(score * 100);
  
  // Color based on score using Stitch tokens
  const scoreClass = percentage >= 80 
    ? 'text-[var(--stitch-success)]' 
    : percentage >= 60 
      ? 'text-[var(--stitch-warning)]' 
      : 'text-[var(--stitch-typography-secondary)]';

  return (
    <Link href={`/jobs/${jobId}`}>
      <div className="bg-[var(--stitch-surface)]/50 backdrop-blur-md border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-5 hover:bg-[var(--stitch-surface-hover)] hover:border-[var(--stitch-primary)]/50 transition-all duration-300 cursor-pointer shadow-[var(--stitch-shadow-sm)] hover:shadow-[var(--stitch-shadow-md)] flex flex-col gap-4">
        
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-[var(--stitch-typography-primary)] mb-1">
              {title}
            </h3>
            <p className="text-sm text-[var(--stitch-typography-secondary)]">
              {company} • {remote ? 'Remote' : location}
            </p>
          </div>
          <div className={`flex items-center justify-center w-12 h-12 rounded-full border-2 ${percentage >= 80 ? 'border-[var(--stitch-success)]/30 bg-[var(--stitch-success)]/10' : 'border-[var(--stitch-warning)]/30 bg-[var(--stitch-warning)]/10'}`}>
            <span className={`font-bold text-sm ${scoreClass}`}>{percentage}%</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-2">
          {tags.slice(0, 4).map((tag, i) => (
            <span 
              key={i} 
              className="px-2.5 py-1 text-xs font-medium rounded-full bg-[var(--stitch-surface-hover)] text-[var(--stitch-typography-primary)] border border-[var(--stitch-border)]"
            >
              {tag}
            </span>
          ))}
          {tags.length > 4 && (
            <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-transparent text-[var(--stitch-typography-secondary)] border border-dashed border-[var(--stitch-border)]">
              +{tags.length - 4} more
            </span>
          )}
        </div>

      </div>
    </Link>
  );
};
