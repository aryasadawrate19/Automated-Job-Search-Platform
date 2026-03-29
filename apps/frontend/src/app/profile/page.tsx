"use client";

import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { UserProfile } from '@shared/index';
import { Navbar } from '@/components/layout/Navbar';
import { ResumeUploader } from '@/components/ui/ResumeUploader';
import Link from 'next/link';

const USER_ID = "00000000-0000-0000-0000-000000000001";

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = async () => {
    try {
      const data = await api.getProfile(USER_ID);
      setProfile(data);
    } catch (err: any) {
      setError(err.message || "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleUploadSuccess = () => {
    setLoading(true);
    fetchProfile();
  };

  return (
    <div className="min-h-screen bg-[var(--stitch-background)]">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <h1 className="text-3xl font-bold text-[var(--stitch-typography-primary)] tracking-tight mb-8">Your Profile</h1>

        {error && (
          <div className="p-4 mb-6 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-error)]/10 border border-[var(--stitch-error)]/20 text-[var(--stitch-error)]">
            {error}
          </div>
        )}

        {loading ? (
          <div className="animate-pulse space-y-8">
            <div className="h-64 bg-[var(--stitch-surface-hover)] rounded-[var(--stitch-radius-lg)]"></div>
            <div className="h-40 bg-[var(--stitch-surface-hover)] rounded-[var(--stitch-radius-lg)]"></div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Resume Uploader Section */}
            <div className="bg-[var(--stitch-surface)] shadow-[var(--stitch-shadow-sm)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-6">
              <h2 className="text-xl font-semibold text-[var(--stitch-typography-primary)] mb-4">Resume Parsing</h2>
              <p className="text-[var(--stitch-typography-secondary)] mb-6 text-sm">
                Upload your latest resume to automatically extract your skills, compute your experience, and refresh your job matches.
              </p>
              <ResumeUploader onUploadSuccess={handleUploadSuccess} />
            </div>

            {/* Profile Overview */}
            {profile && profile.skills && profile.skills.length > 0 && (
              <div className="bg-[var(--stitch-surface)] shadow-[var(--stitch-shadow-sm)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] overflow-hidden">
                <div className="bg-[var(--stitch-primary)]/10 border-b border-[var(--stitch-border)] p-6 flex justify-between items-center">
                  <div>
                    <h2 className="text-xl font-semibold text-[var(--stitch-typography-primary)]">Parsed Profile</h2>
                    <p className="text-[var(--stitch-typography-secondary)] text-sm mt-1">Extracted from your resume</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-[var(--stitch-primary)]">{profile.experience_years}</div>
                    <div className="text-xs font-medium text-[var(--stitch-typography-secondary)] uppercase tracking-wider">Years Exp</div>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <h3 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-3">Seniority Level</h3>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[var(--stitch-primary)]/10 text-[var(--stitch-primary)] capitalize border border-[var(--stitch-primary)]/20">
                      {profile.experience_level}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-3">Extracted Skills ({profile.skills.length})</h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.skills.map((skill, index) => (
                        <span key={index} className="px-3 py-1.5 text-sm font-medium rounded-full bg-[var(--stitch-surface-hover)] text-[var(--stitch-typography-primary)] border border-[var(--stitch-border)]">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {profile.preferred_roles && profile.preferred_roles.length > 0 && (
                     <div>
                       <h3 className="text-sm font-medium text-[var(--stitch-typography-primary)] mb-3">Inferred Roles</h3>
                       <div className="flex flex-wrap gap-2">
                         {profile.preferred_roles.map((role, index) => (
                           <span key={index} className="px-3 py-1 text-sm rounded bg-transparent border border-dashed border-[var(--stitch-border)] text-[var(--stitch-typography-secondary)]">
                             {role}
                           </span>
                         ))}
                       </div>
                     </div>
                  )}

                  <div className="pt-6 border-t border-[var(--stitch-border)] text-center">
                     <Link href="/dashboard" className="text-[var(--stitch-primary)] hover:underline font-medium text-sm">
                       View Job Matches based on this profile →
                     </Link>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
