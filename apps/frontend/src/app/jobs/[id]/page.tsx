"use client";

import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { MatchResponse } from '@shared/index';
import { Navbar } from '@/components/layout/Navbar';
import { ExplainPanel } from '@/components/ui/ExplainPanel';

const USER_ID = "00000000-0000-0000-0000-000000000001";

export default function JobDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [match, setMatch] = useState<MatchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI Assist States
  const [coverLetter, setCoverLetter] = useState<string>('');
  const [generatingCL, setGeneratingCL] = useState(false);
  const [tips, setTips] = useState<string[]>([]);
  const [generatingTips, setGeneratingTips] = useState(false);
  const [assistError, setAssistError] = useState<string | null>(null);

  const clRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    const fetchJobDetail = async () => {
      try {
        const data = await api.getMatchDetail(USER_ID, id);
        setMatch(data);
      } catch (err: any) {
        setError(err.message || "Failed to load job details");
      } finally {
        setLoading(false);
      }
    };
    fetchJobDetail();
  }, [id]);

  const handleGenerateCoverLetter = async () => {
    if (!match?.job_id) return;
    setGeneratingCL(true);
    setCoverLetter('');
    setAssistError(null);

    try {
      const stream = await api.generateCoverLetter({ user_id: USER_ID, job_id: match.job_id });
      const reader = stream.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        setCoverLetter(prev => prev + chunk);
        
        // Auto-scroll inside pre
        if (clRef.current) {
          clRef.current.scrollTop = clRef.current.scrollHeight;
        }
      }
    } catch (err: any) {
      if (err.message && err.message.includes('api_key_required')) {
         setAssistError("API Key required. Please configure your active AI provider in Settings.");
      } else {
         setAssistError(err.message || "Cover letter generation failed");
      }
    } finally {
      setGeneratingCL(false);
    }
  };

  const handleGenerateTips = async () => {
    if (!match?.job_id) return;
    setGeneratingTips(true);
    setAssistError(null);

    try {
      const data = await api.generateResumeTips({ user_id: USER_ID, job_id: match.job_id });
      setTips(data.tips);
    } catch (err: any) {
      if (err.message && err.message.includes('api_key_required')) {
         setAssistError("API Key required. Please configure your active AI provider in Settings.");
      } else {
         setAssistError(err.message || "Resume tip generation failed");
      }
    } finally {
      setGeneratingTips(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--stitch-background)] pt-24">
        <Navbar />
        <div className="max-w-5xl mx-auto px-4 animate-pulse space-y-6">
           <div className="h-40 bg-[var(--stitch-surface-hover)] rounded-[var(--stitch-radius-lg)]"></div>
           <div className="h-96 bg-[var(--stitch-surface-hover)] rounded-[var(--stitch-radius-lg)]"></div>
        </div>
      </div>
    );
  }

  if (error || !match || !match.job) {
    return (
      <div className="min-h-screen bg-[var(--stitch-background)] pt-24 text-center">
        <Navbar />
        <h2 className="text-xl text-[var(--stitch-error)]">{error || "Job not found"}</h2>
      </div>
    );
  }

  const { job } = match;

  return (
    <div className="min-h-screen bg-[var(--stitch-background)]">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Job Content (Left: 2 cols) */}
          <div className="lg:col-span-2 space-y-8">
            {/* Header */}
            <div className="bg-[var(--stitch-surface)] shadow-[var(--stitch-shadow-sm)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-6">
               <h1 className="text-3xl font-bold text-[var(--stitch-typography-primary)] tracking-tight mb-2">
                 {job.title}
               </h1>
               <p className="text-lg text-[var(--stitch-typography-secondary)] mb-6">
                 {job.company} • {job.remote ? 'Remote' : job.location}
               </p>
               
               <div className="flex flex-wrap gap-4 pt-4 border-t border-[var(--stitch-border)]">
                 <div className="flex flex-col">
                   <span className="text-xs text-[var(--stitch-typography-secondary)] uppercase">Experience</span>
                   <span className="font-medium text-[var(--stitch-typography-primary)] capitalize">{job.experience_level || 'Not specified'}</span>
                 </div>
                 <div className="flex flex-col">
                   <span className="text-xs text-[var(--stitch-typography-secondary)] uppercase">Salary</span>
                   <span className="font-medium text-[var(--stitch-typography-primary)]">
                     {job.salary_min ? `$${(job.salary_min/1000)}k - $${(job.salary_max!/1000)}k` : 'Not specified'}
                   </span>
                 </div>
                 <div className="flex flex-col">
                   <span className="text-xs text-[var(--stitch-typography-secondary)] uppercase">Posted</span>
                   <span className="font-medium text-[var(--stitch-typography-primary)]">
                     {new Date(job.posted_at || job.ingested_at!).toLocaleDateString()}
                   </span>
                 </div>
               </div>
            </div>

            {/* Application Assist Tools */}
            <div className="bg-[var(--stitch-surface)] shadow-[var(--stitch-shadow-sm)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] overflow-hidden">
               <div className="bg-gradient-to-r from-[var(--stitch-primary)]/10 to-[#8A2BE2]/10 border-b border-[var(--stitch-border)] p-4">
                 <h3 className="font-semibold text-[var(--stitch-typography-primary)] flex items-center gap-2">
                    <svg className="w-5 h-5 text-[var(--stitch-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                    Luminous Assist
                 </h3>
               </div>
               
               <div className="p-5 space-y-6">
                  {assistError && (
                    <div className="p-3 bg-[var(--stitch-error)]/10 text-[var(--stitch-error)] text-sm rounded border border-[var(--stitch-error)]/20">
                      {assistError}
                    </div>
                  )}

                  <div className="flex flex-col sm:flex-row gap-4">
                     <button 
                       onClick={handleGenerateCoverLetter}
                       disabled={generatingCL}
                       className="flex-1 py-2 px-4 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-primary)] text-white font-medium hover:brightness-110 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2 shadow-[var(--stitch-shadow-sm)]"
                     >
                        {generatingCL ? (
                          <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div> Generating...</>
                        ) : 'Generate Cover Letter'}
                     </button>
                     
                     <button 
                       onClick={handleGenerateTips}
                       disabled={generatingTips}
                       className="flex-1 py-2 px-4 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] text-[var(--stitch-typography-primary)] font-medium hover:bg-[var(--stitch-surface)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
                     >
                        {generatingTips ? (
                          <><div className="w-4 h-4 border-2 border-[var(--stitch-primary)] border-t-transparent rounded-full animate-spin"></div> Parsing...</>
                        ) : 'Get Resume Tips'}
                     </button>
                  </div>

                  {coverLetter && (
                    <div className="mt-4">
                      <h4 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">Tailored Cover Letter</h4>
                      <div 
                        ref={clRef}
                        className="bg-[var(--stitch-background)] border border-[var(--stitch-border)] rounded-md p-4 h-64 overflow-y-auto text-sm text-[var(--stitch-typography-secondary)] whitespace-pre-wrap font-mono"
                      >
                        {coverLetter}
                      </div>
                    </div>
                  )}

                  {tips.length > 0 && (
                    <div className="mt-4">
                       <h4 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">Resume Improvement Tips</h4>
                       <ul className="space-y-2 pl-4">
                         {tips.map((tip, i) => (
                           <li key={i} className="text-sm text-[var(--stitch-typography-secondary)] list-disc">
                             {tip}
                           </li>
                         ))}
                       </ul>
                    </div>
                  )}
               </div>
            </div>

            {/* Description */}
            <div className="bg-[var(--stitch-surface)] shadow-[var(--stitch-shadow-sm)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-6">
              <h2 className="text-xl font-semibold text-[var(--stitch-typography-primary)] mb-4">Job Description</h2>
              <div 
                className="prose prose-sm md:prose-base dark:prose-invert max-w-none text-[var(--stitch-typography-secondary)]"
                dangerouslySetInnerHTML={{ __html: job.description_raw }}
              />
            </div>
          </div>

          {/* Sidebar (Right: 1 col) */}
          <div className="lg:col-span-1 space-y-6">
            
            <a 
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full py-3 px-4 text-center rounded-[var(--stitch-radius-lg)] bg-[var(--stitch-success)] text-white font-medium hover:brightness-110 transition-colors shadow-[var(--stitch-shadow-md)]"
            >
              Apply on {job.source === 'greenhouse' ? 'Greenhouse' : job.source === 'lever' ? 'Lever' : 'Source'}
            </a>

            <ExplainPanel match={match} />
            
          </div>

        </div>
      </main>
    </div>
  );
}
