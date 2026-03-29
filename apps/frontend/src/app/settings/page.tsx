"use client";

import React from 'react';
import { Navbar } from '@/components/layout/Navbar';
import { AIProviderSettings } from '@/components/ui/AIProviderSettings';

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-[var(--stitch-background)]">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        <h1 className="text-3xl font-bold text-[var(--stitch-typography-primary)] tracking-tight mb-8">Settings</h1>
        
        <div className="space-y-8">
          <AIProviderSettings />

          <div className="bg-[var(--stitch-surface)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-lg)] p-6">
             <h2 className="text-xl font-semibold text-[var(--stitch-typography-primary)] mb-2">Preferences</h2>
             <p className="text-sm text-[var(--stitch-typography-secondary)] mb-6">
               Adjust your basic job seeking preferences.
             </p>

             <div className="space-y-4">
                <div>
                   <label className="block text-sm font-medium text-[var(--stitch-typography-primary)] mb-2">Remote Preference</label>
                   <select className="w-full max-w-xs bg-[var(--stitch-surface-hover)] border border-[var(--stitch-border)] rounded-[var(--stitch-radius-md)] px-4 py-2 text-sm text-[var(--stitch-typography-primary)] focus:outline-none focus:border-[var(--stitch-primary)]">
                      <option value="open">Open (Remote & Onsite)</option>
                      <option value="preferred">Remote Preferred</option>
                      <option value="only">Remote Only</option>
                   </select>
                </div>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
}
