"use client";

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { MatchListResponse, MatchResponse } from '@shared/index';
import { MatchCard } from '@/components/ui/MatchCard';
import { Navbar } from '@/components/layout/Navbar';

// Hardcoded userId for demo purposes. In production, use standard Auth.
const USER_ID = "00000000-0000-0000-0000-000000000001";

export default function DashboardPage() {
  const [matches, setMatches] = useState<MatchResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const data = await api.getMatches(USER_ID);
        setMatches(data.items);
      } catch (err: any) {
        setError(err.message || "Failed to load matches");
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  return (
    <div className="min-h-screen bg-[var(--stitch-background)]">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[var(--stitch-typography-primary)] tracking-tight">Your Recommended Jobs</h1>
          <p className="text-[var(--stitch-typography-secondary)] mt-2">
            Based on your profile, here are the roles that match your skills and experience.
          </p>
        </div>

        {error && (
          <div className="p-4 mb-6 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-error)]/10 border border-[var(--stitch-error)]/20 text-[var(--stitch-error)]">
            {error}
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="animate-pulse bg-[var(--stitch-surface-hover)] h-40 rounded-[var(--stitch-radius-lg)] border border-[var(--stitch-border)]"></div>
            ))}
          </div>
        ) : matches.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {matches.map((match) => (
              <MatchCard 
                key={match.id}
                id={match.id!}
                jobId={match.job_id!}
                title={match.job?.title || 'Unknown Role'}
                company={match.job?.company || 'Unknown Company'}
                location={match.job?.location || 'Unspecified'}
                remote={match.job?.remote || false}
                score={match.final_score!}
                tags={match.matched_skills || []}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-20 bg-[var(--stitch-surface)] rounded-[var(--stitch-radius-lg)] border border-[var(--stitch-border)] shadow-[var(--stitch-shadow-sm)]">
            <svg className="w-16 h-16 mx-auto text-[var(--stitch-typography-secondary)] border-2 border-[var(--stitch-border)] rounded-full p-3 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="text-xl font-medium text-[var(--stitch-typography-primary)] mb-2">No matches found</h3>
            <p className="text-[var(--stitch-typography-secondary)]">
              Upload your resume or wait for the system to process new jobs.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
