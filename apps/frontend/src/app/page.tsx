import React from 'react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--stitch-background)] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[var(--stitch-primary)]/20 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-[#8A2BE2]/20 blur-[120px] pointer-events-none"></div>

      <div className="max-w-3xl w-full text-center z-10 space-y-8">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-[var(--stitch-border)] bg-[var(--stitch-surface)]/50 backdrop-blur-md mb-4 shadow-[var(--stitch-shadow-sm)]">
          <span className="flex w-2 h-2 rounded-full bg-[var(--stitch-success)] animate-pulse"></span>
          <span className="text-xs font-semibold text-[var(--stitch-typography-primary)] tracking-wide uppercase">AI-Powered Job Intelligence</span>
        </div>

        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-[var(--stitch-typography-primary)] leading-tight">
          Find your next role with <span className="text-transparent bg-clip-text bg-gradient-to-r from-[var(--stitch-primary)] to-[#8A2BE2]">Luminous API</span>
        </h1>
        
        <p className="text-lg md:text-xl text-[var(--stitch-typography-secondary)] max-w-2xl mx-auto leading-relaxed">
          Upload your resume and let our hybrid AI matching engine find the perfect engineering roles for you across top companies.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
          <Link 
            href="/dashboard"
            className="w-full sm:w-auto px-8 py-4 rounded-[var(--stitch-radius-lg)] bg-[var(--stitch-primary)] text-white font-medium text-lg hover:brightness-110 transition-all shadow-[var(--stitch-shadow-md)] hover:shadow-[var(--stitch-shadow-lg)]"
          >
            Go to Dashboard
          </Link>
          <Link 
            href="/profile"
            className="w-full sm:w-auto px-8 py-4 rounded-[var(--stitch-radius-lg)] bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] text-[var(--stitch-typography-primary)] font-medium text-lg hover:bg-[var(--stitch-surface)] transition-all shadow-[var(--stitch-shadow-sm)] hover:shadow-[var(--stitch-shadow-md)]"
          >
            Upload Resume
          </Link>
        </div>
      </div>
    </div>
  );
}
